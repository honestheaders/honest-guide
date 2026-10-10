#!/usr/bin/env python3
"""英語記事の自動チェック(ループの「合格・不合格」を決める係)。

使い方:
    python3 check_en.py content_en/スラッグ.md
    python3 check_en.py --all          # すでにある英語記事を全部チェック

合格なら「PASS」と出して終了コード 0。
不合格なら、直すべき点を1行ずつ出して終了コード 1。
ここで機械的に見られないこと(事実が公式と合っているか)は、
書いた人が出典を開いて確かめる。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MIN_WORDS, MAX_WORDS = 400, 1800
MAX_PRODUCTS = 3
PRODUCTS = {"headers", "cookies", "checklist", "templates"}
# 保証表現・順位づけ(CLAUDE.md の英語コーナーのルール)
BANNED = [
    r"\bguarantee(d|s)?\b", r"\balways secure\b", r"\b100% (safe|secure)\b",
    r"\bthe best\b", r"\bbest (extension|tool|way)\b", r"#1\b", r"\bnumber one\b",
    r"\bI (tried|tested|used)\b", r"\bin my experience\b", r"\bwe tested\b",
]
SOURCE_OK = re.compile(
    r"(developer\.mozilla\.org|developer\.chrome\.com|web\.dev|owasp\.org|"
    r"rfc-editor\.org|datatracker\.ietf\.org|w3\.org|whatwg\.org|"
    r"curl\.se|gnu\.org|nginx\.org|vercel\.com|developers\.cloudflare\.com|"
    r"hstspreload\.org|support\.google\.com|chromium\.org|github\.com/honestheaders)"
)


def check(md_path: Path) -> list[str]:
    problems = []
    text = md_path.read_text(encoding="utf-8")
    slug = md_path.stem

    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return ["先頭の --- で囲んだ title / description / updated がない"]
    head, body = m.group(1), m.group(2)
    for key in ("title", "description", "updated"):
        if not re.search(rf"^{key}: \S", head, re.M):
            problems.append(f"先頭に {key}: がない")
    if re.search(r'^title: ["\']', head, re.M):
        problems.append("title が引用符で囲まれている(囲まない決まり)")
    if not re.search(r"^updated: \d{4}-\d{2}-\d{2}$", head, re.M):
        problems.append("updated が YYYY-MM-DD の形になっていない")

    words = len(re.findall(r"[A-Za-z0-9'’-]+", body))
    if not MIN_WORDS <= words <= MAX_WORDS:
        problems.append(f"長さが {words} words({MIN_WORDS}〜{MAX_WORDS} にする)")

    first = "\n".join([l for l in body.strip().splitlines() if l.strip()][:3])
    if first.lstrip().startswith("#"):
        problems.append("本文が見出しから始まっている(最初の3行で答えを書く)")

    if not re.search(r"^## Who this is not for", body, re.M):
        problems.append("「## Who this is not for」の見出しがない")

    src = re.search(r"^## Sources[^\n]*\n(.*)", body, re.M | re.S)
    if not src:
        problems.append("「## Sources」の見出しがない")
    else:
        if not re.search(r"\d{4}-\d{2}-\d{2}", src.group(0)):
            problems.append("Sources に確認日(YYYY-MM-DD)がない")
        urls = re.findall(r"https?://[^\s>)]+", src.group(1))
        if len(urls) < 2:
            problems.append(f"Sources のURLが {len(urls)} 本(2本以上にする)")
        bad = [u for u in urls if not SOURCE_OK.search(u)]
        if bad:
            problems.append("公式以外かもしれない出典(公式なら check_en.py の SOURCE_OK に足す): " + ", ".join(bad))

    cards = re.findall(r"\{\{product:([a-z]+)\}\}", body)
    if len(cards) > MAX_PRODUCTS:
        problems.append(f"商品カードが {len(cards)} 個({MAX_PRODUCTS} 個まで)")
    for c in cards:
        if c not in PRODUCTS:
            problems.append(f"知らない商品カード: {c}")
    if "rakuten" in text.lower():
        problems.append("楽天リンクが入っている(英語記事では使わない)")

    for pat in BANNED:
        hit = re.search(pat, body, re.I)
        if hit:
            problems.append(f"使わない言い方: 「{hit.group(0)}」")

    html = ROOT / "docs" / "en" / slug / "index.html"
    if not html.exists():
        problems.append(f"{html.relative_to(ROOT)} がない(python3 build.py を実行する)")
    else:
        page = html.read_text(encoding="utf-8")
        for link in set(re.findall(r'href="/honest-guide/([^"#?]*)', page)):
            target = ROOT / "docs" / link
            if not (target.is_file() or (target / "index.html").is_file()):
                problems.append(f"サイト内リンク切れ: /honest-guide/{link}")
        if "{{" in page:
            problems.append("HTMLに {{ }} が残っている(カードの書き方を確認)")

    others = [p for p in (ROOT / "content_en").glob("*.md") if p != md_path]
    first_line = first.splitlines()[0][:60] if first else ""
    for o in others:
        ob = o.read_text(encoding="utf-8").split("---", 2)[-1].strip()
        if first_line and ob.startswith(first_line):
            problems.append(f"書き出しが {o.name} と同じ(言い回しを変える)")
    return problems


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(2)
    paths = sorted((ROOT / "content_en").glob("*.md")) if args == ["--all"] else [Path(a).resolve() for a in args]
    failed = False
    for p in paths:
        probs = check(p)
        if probs:
            failed = True
            print(f"FAIL {p.name}")
            for x in probs:
                print(f"  - {x}")
        else:
            print(f"PASS {p.name}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
