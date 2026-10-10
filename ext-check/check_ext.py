#!/usr/bin/env python3
"""拡張機能の「出す前チェック」(Honest Headers / Honest Cookies 共通)。

ストアに出す前に、これを通ったものだけをオーナーに渡す。
「合格」でなければ、直すべき点を1行ずつ出して終了コード1になる。

使い方:
    python3 ext-check/check_ext.py <拡張のフォルダ> --baseline ext-check/baseline-headers.json
    python3 ext-check/check_ext.py <拡張のフォルダ> --baseline ... --zip dist   # 合格したときだけ zip も作る
    (今すでに出している版を点検するだけのときは --audit をつける。バージョンの増加を見ない)

見ること(どれも「ストアで落ちる」か「うちの約束がくずれる」ことの防止):
  1. manifest が MV3 で、バージョンが前回提出より大きい
  2. 権限が baseline(オーナーが決めた許可リスト)を超えていない。
     webRequest / scripting / tabs などの「広く覗ける権限」と content_scripts は、baseline に書いても通さない
  3. 拡張のコードが外へ通信しない・外のコードを読まない(fetch, XMLHttpRequest, eval, 外部script など)
     コード内のURLは baseline の allowed_url_prefixes にあるものだけ
  4. manifest が参照するファイルが実在する
  5. 英語と日本語の表示文のキーがそろっている / コードが使うキーが英語に存在する
  6. JavaScript の文法エラーがない / test/*.test.mjs があれば実行して全部通る
  7. README・PRIVACY が manifest の権限と食い違っていない / 古い案内(baseline の forbidden_strings)が残っていない
  8. 提出用zipの中身(ストアに不要なファイルや秘密が入っていない)
事実の確認(ストアの審査基準に合うか等)はここでは見ない。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

# 「広く覗ける」権限。baseline に書いても通さない(足したいときは、このファイルを直す=人の目に入る)
ALWAYS_FORBIDDEN_PERMS = {
    "webRequest", "webRequestBlocking", "scripting", "tabs", "history", "topSites", "management",
    "webNavigation", "nativeMessaging", "declarativeNetRequestFeedback", "debugger", "proxy",
    "browsingData", "downloads", "clipboardRead", "desktopCapture", "tabCapture", "pageCapture",
    "privacy", "identity", "identity.email", "background", "bookmarks", "geolocation",
}
NETWORK_PATTERNS = [
    (r"\bfetch\s*\(", "fetch("), (r"XMLHttpRequest", "XMLHttpRequest"), (r"\bWebSocket\b", "WebSocket"),
    (r"\bEventSource\b", "EventSource"), (r"sendBeacon", "sendBeacon"), (r"\beval\s*\(", "eval("),
    (r"new\s+Function\s*\(", "new Function("), (r"importScripts\s*\(", "importScripts("),
    (r"""<script[^>]+src=["']https?://""", "外部の <script src>"),
    (r"""import\s*\(\s*["']https?://""", "外部URLの動的import"),
    (r"""from\s+["']https?://""", "外部URLからのimport"),
]
URL_RE = re.compile(r"""https?://[^\s"'`<>)\\]+""")
EXCLUDE_FROM_ZIP = {".git", ".github", "test", "tests", "store", "node_modules", "dist", ".DS_Store"}
EXCLUDE_SUFFIX = {".md", ".map", ".pem", ".key", ".env", ".zip", ".log"}
CODE_SUFFIX = {".js", ".mjs", ".html", ".htm"}


def load_manifest(root, errs):
    p = root / "manifest.json"
    if not p.exists():
        errs.append("manifest.json がない")
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errs.append(f"manifest.json が読めない: {e}")
        return None


def vtuple(v):
    return tuple(int(x) for x in v.split("."))


def code_files(root):
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in CODE_SUFFIX and not (set(p.relative_to(root).parts) & EXCLUDE_FROM_ZIP):
            yield p


def check_manifest(m, base, audit, errs, warns):
    if m.get("manifest_version") != 3:
        errs.append("manifest_version が 3 ではない")
    v = m.get("version", "")
    if not re.fullmatch(r"\d+(\.\d+){1,3}", v):
        errs.append(f"version の形が違う: {v!r}")
    elif base.get("published_version") and not audit:
        if vtuple(v) <= vtuple(base["published_version"]):
            errs.append(f"version {v} が前回提出 {base['published_version']} より大きくない(ストアは同じ版を受け付けない)")
    for k in ("permissions", "host_permissions", "optional_permissions", "optional_host_permissions"):
        allowed = set(base.get("allowed_" + k, []))
        got = set(m.get(k, []))
        for perm in sorted(got):
            if perm in ALWAYS_FORBIDDEN_PERMS:
                errs.append(f"{k} に広く覗ける権限 {perm!r} がある(うちは使わない決まり)")
            elif perm not in allowed:
                errs.append(f"{k} に baseline にない権限 {perm!r} が増えた(増やすならオーナーの決定が必要)")
        for perm in sorted(allowed - got):
            warns.append(f"baseline にある {k} の {perm!r} が manifest から消えた(意図したものか確認)")
    if m.get("content_scripts"):
        errs.append("content_scripts がある(ページの中身を読む仕組みは入れない決まり)")
    if m.get("externally_connectable") or m.get("update_url"):
        errs.append("externally_connectable / update_url がある(外から操作・更新される口は作らない)")
    csp = json.dumps(m.get("content_security_policy", {}))
    if "unsafe-eval" in csp or "http:" in csp or "https:" in csp:
        errs.append("content_security_policy がゆるい(unsafe-eval や外部URLの許可)")


def check_files_exist(root, m, errs):
    refs = []
    refs += list((m.get("icons") or {}).values())
    act = m.get("action") or {}
    if act.get("default_popup"):
        refs.append(act["default_popup"])
    refs += list((act.get("default_icon") or {}).values()) if isinstance(act.get("default_icon"), dict) else []
    bg = m.get("background") or {}
    if bg.get("service_worker"):
        refs.append(bg["service_worker"])
    if m.get("options_page"):
        refs.append(m["options_page"])
    if (m.get("options_ui") or {}).get("page"):
        refs.append(m["options_ui"]["page"])
    for r in refs:
        if not (root / r).is_file():
            errs.append(f"manifest が参照する {r} がない")
    # html が読むローカルの js/css も確認
    for h in root.glob("*.html"):
        for ref in re.findall(r"""(?:src|href)=["']([^"':#?]+)["']""", h.read_text(encoding="utf-8")):
            if not (root / ref).exists():
                errs.append(f"{h.name} が読む {ref} がない")


def check_code(root, base, errs):
    allowed = tuple(base.get("allowed_url_prefixes", []))
    for p in code_files(root):
        rel = p.relative_to(root)
        text = p.read_text(encoding="utf-8")
        for pat, label in NETWORK_PATTERNS:
            if re.search(pat, text):
                errs.append(f"{rel}: 通信・外部コードにつながる書き方 {label}(うちは外へ通信しない約束)")
        for url in sorted(set(URL_RE.findall(text))):
            if not url.startswith(allowed):
                errs.append(f"{rel}: baseline にないURL {url}")


def msg_keys(path):
    try:
        return set(json.loads(path.read_text(encoding="utf-8")).keys())
    except Exception as e:  # noqa: BLE001
        return {f"__読めない:{e}__"}


def check_i18n(root, m, errs, warns):
    loc = root / "_locales"
    if not loc.is_dir():
        warns.append("_locales がない")
        return
    sets = {d.name: msg_keys(d / "messages.json") for d in loc.iterdir() if (d / "messages.json").exists()}
    default = m.get("default_locale", "en")
    if default not in sets:
        errs.append(f"default_locale {default!r} の messages.json がない")
        return
    for name, keys in sets.items():
        for k in sorted(sets[default] - keys):
            errs.append(f"_locales/{name} に {k!r} がない({default} にはある)")
        for k in sorted(keys - sets[default]):
            errs.append(f"_locales/{default} に {k!r} がない({name} にはある)")
    used = set(re.findall(r"__MSG_(\w+)__", json.dumps(m)))
    for p in code_files(root):
        t = p.read_text(encoding="utf-8")
        used |= set(re.findall(r"""data-i18n(?:-[a-z]+)?=["'](\w+)["']""", t))
        used |= set(re.findall(r"""getMessage\(\s*["'](\w+)["']""", t))
        used |= set(re.findall(r"""\bt\(\s*["'](\w+)["']""", t))
    for k in sorted(used - sets[default]):
        errs.append(f"コードが使う表示文のキー {k!r} が _locales/{default} にない")
    for k in sorted(sets[default] - used):
        warns.append(f"使われていない表示文のキー {k!r}(消してよいか確認)")


def check_js(root, errs, warns):
    node = shutil.which("node")
    if not node:
        warns.append("node がないので文法・テストの確認ができない")
        return
    tmp = Path(tempfile.mkdtemp(prefix="extchk-"))
    try:
        for p in code_files(root):
            if p.suffix not in (".js", ".mjs"):
                continue
            t = tmp / (p.stem + ".mjs")
            shutil.copyfile(p, t)
            r = subprocess.run([node, "--check", str(t)], capture_output=True, text=True)
            if r.returncode:
                lines = [l for l in r.stderr.splitlines() if "Error" in l]
                errs.append(f"{p.relative_to(root)}: 文法エラー: {lines[0].strip() if lines else r.stderr.strip()[:120]}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tests = sorted((root / "test").glob("*.test.mjs")) if (root / "test").is_dir() else []
    if not tests:
        warns.append("test/*.test.mjs がない(自動テストなし)")
        return
    r = subprocess.run([node, "--test", *map(str, tests)], capture_output=True, text=True, cwd=root)
    if r.returncode:
        tail = "\n".join((r.stdout + r.stderr).strip().splitlines()[-8:])
        errs.append("自動テストが通らない:\n    " + tail.replace("\n", "\n    "))


def check_docs(root, m, base, errs, warns):
    perms = set(m.get("permissions", [])) | set(m.get("optional_permissions", []))
    readme = root / "README.md"
    priv = root / "PRIVACY.md"
    if not priv.exists():
        errs.append("PRIVACY.md がない(ストアの提出に必要)")
    if readme.exists():
        text = readme.read_text(encoding="utf-8")
        for perm in sorted(perms):
            if perm not in text:
                errs.append(f"README.md の権限の説明に {perm!r} がない(manifest と食い違い)")
    else:
        warns.append("README.md がない")
    for f in (readme, priv):
        if f.exists():
            t = f.read_text(encoding="utf-8")
            for s in base.get("forbidden_strings", []):
                if s in t:
                    errs.append(f"{f.name} に古い案内 {s!r} が残っている")


def build_zip(root, m, out_dir, errs):
    out_dir.mkdir(parents=True, exist_ok=True)
    name = f"{m.get('short_name', 'extension').lower().replace(' ', '-')}-{m['version']}.zip"
    out = out_dir / name
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            rel = p.relative_to(root)
            if not p.is_file() or (set(rel.parts) & EXCLUDE_FROM_ZIP) or p.suffix in EXCLUDE_SUFFIX or p.name.startswith("."):
                continue
            z.write(p, rel.as_posix())
    with zipfile.ZipFile(out) as z:
        names = set(z.namelist())
    if "manifest.json" not in names:
        errs.append("zip の直下に manifest.json がない")
    if out.stat().st_size > 10 * 1024 * 1024:
        errs.append(f"zip が大きい({out.stat().st_size // 1024} KB)")
    return out, sorted(names)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("--baseline", required=True)
    ap.add_argument("--zip", metavar="OUT_DIR")
    ap.add_argument("--audit", action="store_true", help="今の版の点検だけ(バージョンの増加は見ない)")
    a = ap.parse_args()
    root = Path(a.folder).resolve()
    base = json.loads(Path(a.baseline).read_text(encoding="utf-8"))
    errs, warns = [], []
    m = load_manifest(root, errs)
    if m:
        check_manifest(m, base, a.audit, errs, warns)
        check_files_exist(root, m, errs)
        check_code(root, base, errs)
        check_i18n(root, m, errs, warns)
        check_js(root, errs, warns)
        check_docs(root, m, base, errs, warns)
    out = None
    if a.zip and m and not errs:
        out, names = build_zip(root, m, Path(a.zip), errs)
        if not errs:
            print(f"zip: {out}({len(names)}ファイル)")
    print(f"== {base.get('name', root.name)} {m.get('version', '?') if m else '?'} ==")
    for w in warns:
        print(f"  注意: {w}")
    if errs:
        print("FAIL")
        for e in errs:
            print(f"  - {e}")
        if out:
            out.unlink(missing_ok=True)
        sys.exit(1)
    print("PASS")


if __name__ == "__main__":
    main()
