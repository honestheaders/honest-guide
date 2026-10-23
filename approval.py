#!/usr/bin/env python3
"""承認式の公開(オーナーが「投稿して」と言ったときだけ main に出す)。

  python3 approval.py stage      … 作業ツリーの変更を draft/<スラッグ> ブランチに退避して push する(main には出さない)
  python3 approval.py status     … 承認待ちの下書きを一覧する
  python3 approval.py publish    … 承認待ちの下書きをすべて main に入れ、build.py と check_en.py を通して push、届いたかまで確かめる
  python3 approval.py discard    … 承認待ちの下書きをすべて捨てる(オーナーが「やめて」と言ったとき)

approval.json の mode が "manual" のとき、毎日の自動運転は stage だけを使う。"auto" なら従来どおり main へ直接 push。
docs/ は下書きに入れない(publish のときに main 上で作り直す。docs の衝突を避けるため)。
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PREFIX = "draft/"
EXCLUDE = [":(exclude)docs", ":(exclude)src/__pycache__", ":(exclude)__pycache__"]


def git(*args, check=True):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} が失敗: {r.stderr.strip() or r.stdout.strip()}")
    return r.stdout.strip()


def mode():
    try:
        return json.loads((ROOT / "approval.json").read_text(encoding="utf-8")).get("mode", "manual")
    except FileNotFoundError:
        return "manual"


def drafts():
    git("fetch", "origin", "--prune")
    out = git("for-each-ref", "--sort=committerdate", "--format=%(refname:short)", f"refs/remotes/origin/{PREFIX}")
    return [l.removeprefix("origin/") for l in out.splitlines() if l]


def new_slug():
    out = git("status", "--porcelain", "--", "content_en")
    for line in out.splitlines():
        m = re.search(r"content_en/([^/]+)\.md$", line)
        if m and line[:2].strip() in ("A", "??", "AM"):
            return m.group(1)
    return None


def stage():
    slug = new_slug()
    if not slug:
        raise SystemExit("content_en に新しい記事がありません。stage するものがない。")
    branch = PREFIX + slug[:60]
    git("branch", "-D", branch, check=False)
    git("checkout", "-b", branch)
    git("add", "-A", "--", ".", *EXCLUDE)
    git("commit", "-m", f"[承認待ち] English article draft: {slug}")
    git("push", "-u", "origin", branch)
    sha = git("rev-parse", "HEAD")
    git("checkout", "main")
    git("checkout", "--", ".", check=False)
    remote = git("ls-remote", "origin", f"refs/heads/{branch}").split()[0]
    if remote != sha:
        raise SystemExit("下書きが GitHub に届いていません。承認待ちにできなかった。")
    print(f"STAGED {branch} (まだ公開されていません。オーナーが「投稿して」と言ったら publish)")


def status():
    ds = drafts()
    if not ds:
        print("承認待ちはありません")
    for d in ds:
        print(d, "|", git("log", "-1", "--format=%cs %s", f"origin/{d}"))


def publish():
    ds = drafts()
    if not ds:
        print("承認待ちはありません。何も公開しません。")
        return
    git("checkout", "main")
    git("pull", "--ff-only", "origin", "main")
    merged, slugs = [], []
    for d in ds:
        r = subprocess.run(["git", "merge", "--no-ff", "-m", f"Publish approved draft {d}", f"origin/{d}"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            git("merge", "--abort", check=False)
            print(f"SKIP {d}: main とぶつかった。手で直す必要あり。\n{r.stdout.strip()}")
            continue
        merged.append(d)
        slugs += re.findall(r"content_en/([^/\s]+)\.md", git("diff", "--name-only", "HEAD~1", "HEAD"))
    if not merged:
        raise SystemExit("公開できる下書きがなかった(すべてぶつかった)")
    build = subprocess.run([sys.executable, "build.py"], cwd=ROOT, capture_output=True, text=True)
    if build.returncode != 0:
        raise SystemExit("build.py が失敗: " + build.stderr[-400:])
    for s in slugs:
        c = subprocess.run([sys.executable, "check_en.py", f"content_en/{s}.md"], cwd=ROOT, capture_output=True, text=True)
        print(c.stdout.strip())
        if c.returncode != 0:
            git("reset", "--hard", "origin/main")
            git("clean", "-fdq", "docs", "content_en")
            raise SystemExit(f"{s} が check_en.py に不合格。公開を中止(main は元のまま)。")
    git("add", "-A", "--", ".", *EXCLUDE)
    git("commit", "-m", "Rebuild docs for approved drafts", check=False)
    git("push", "origin", "main")
    git("fetch", "origin", "main")
    if git("rev-parse", "origin/main") != git("rev-parse", "HEAD"):
        raise SystemExit("push が届いていない(origin/main が自分のコミットと違う)。公開できなかった。")
    for d in merged:
        git("push", "origin", "--delete", d, check=False)
    print("PUBLISHED", ", ".join(merged), "→ https://honestheaders.github.io/honest-guide/en/" + (slugs[-1] if slugs else "") + "/")


def discard():
    for d in drafts():
        git("push", "origin", "--delete", d, check=False)
        print("DISCARDED", d)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"stage": stage, "status": status, "publish": publish, "discard": discard}.get(cmd, status)()
