#!/usr/bin/env python3
"""Honest Guide 静的サイト生成。 python3 build.py で docs/ に出力する。"""
import json, re, html, shutil, datetime, pathlib
import markdown

ROOT = pathlib.Path(__file__).parent
CFG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
OUT = ROOT / "docs"
BASE = CFG["base_path"]
TODAY = datetime.date.today().isoformat()

CSS = (ROOT / "src" / "style.css").read_text(encoding="utf-8")

def rakuten_link(url, label):
    """楽天のURLをアフィリエイトリンクに包む。IDが未設定ならそのまま。"""
    aid = CFG["rakuten_affiliate_id"]
    if aid:
        from urllib.parse import quote
        href = f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={quote(url, safe='')}&link_type=text"
    else:
        href = url
    return f'<a href="{html.escape(href)}" rel="nofollow sponsored noopener" target="_blank">{html.escape(label)}</a>'

PR = '<p class="pr">※この記事にはプロモーション(広告)が含まれます。商品リンクから購入されると、当サイトに報酬が入ることがあります。</p>'

def page(path, title, desc, body, article=False):
    canon = f'{CFG["base_url"]}{path}'
    nav = f'''<header><div class="wrap"><a class="logo" href="{BASE}/">{CFG["site_name"]}</a>
<nav><a href="{BASE}/tools/">計算ツール</a><a href="{BASE}/guides/">えらび方ガイド</a><a href="{BASE}/about/">運営者情報</a></nav></div></header>'''
    foot = f'''<footer><div class="wrap"><p>当サイトは、楽天アフィリエイトなどのアフィリエイトプログラムに参加しています。商品リンクを通じて報酬を得ることがあります。</p>
<p><a href="{BASE}/about/">運営者情報</a> / <a href="{BASE}/privacy/">プライバシーポリシー</a></p><p>&copy; {datetime.date.today().year} {CFG["operator"]}</p></div></footer>'''
    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="{'article' if article else 'website'}">
<style>{CSS}</style></head><body>{nav}<main class="wrap">{body}</main>{foot}</body></html>'''
    d = OUT / path.strip("/")
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(doc, encoding="utf-8")
    return path

pages = []

# ---------- 計算ツール ----------
AREA = '''<h1>坪・平米・畳の換算ツール</h1>
<p>広さの単位を、まとめて換算します。どれか1つに数字を入れてください。</p>
<div class="tool"><label>平米(㎡)<input id="m2" type="number" step="any" inputmode="decimal"></label>
<label>坪<input id="tsubo" type="number" step="any" inputmode="decimal"></label>
<label>畳(1畳=1.62㎡)<input id="jo" type="number" step="any" inputmode="decimal"></label></div>
<p class="note">1坪=約3.3058㎡。畳は、不動産の広告で使われる目安(1畳=1.62㎡)で計算しています。地域や建物によって畳の大きさは違います。</p>
<script>
const T=3.305785,J=1.62,m2=document.getElementById('m2'),ts=document.getElementById('tsubo'),jo=document.getElementById('jo');
const r=(v)=>Math.round(v*100)/100;
function setFrom(src){const v=parseFloat(src.value);if(isNaN(v))return;let m;
 if(src===m2)m=v;else if(src===ts)m=v*T;else m=v*J;
 if(src!==m2)m2.value=r(m);if(src!==ts)ts.value=r(m/T);if(src!==jo)jo.value=r(m/J);}
[m2,ts,jo].forEach(e=>e.addEventListener('input',()=>setFrom(e)));
</script>'''
pages.append(page("/tools/area/", "坪・平米・畳の換算ツール|Honest Guide", "坪、平米(㎡)、畳を相互に換算できる無料ツール。", AREA))

DENKI = '''<h1>家電の電気代 計算ツール</h1>
<p>消費電力と使う時間から、電気代の目安を計算します。</p>
<div class="tool"><label>消費電力(W)<input id="w" type="number" step="any" inputmode="decimal" value="1000"></label>
<label>1日に使う時間(時間)<input id="h" type="number" step="any" inputmode="decimal" value="1"></label>
<label>1か月に使う日数(日)<input id="d" type="number" step="any" inputmode="decimal" value="30"></label>
<label>電気料金の単価(円/kWh)<input id="p" type="number" step="any" inputmode="decimal" value="31"></label></div>
<div class="result"><p>1日あたり <b id="r1">-</b> 円</p><p>1か月あたり <b id="r2">-</b> 円</p><p>1年あたり <b id="r3">-</b> 円</p></div>
<p class="note">単価の31円/kWhは、電気料金を比べるときによく使われる目安の単価(全国家庭電気製品公正取引協議会の目安)です。実際の単価は、ご契約の料金プランで違います。検針票やアプリで確認して入れると、より正確になります。</p>
<script>
const g=id=>parseFloat(document.getElementById(id).value)||0;
function calc(){const day=g('w')/1000*g('h')*g('p');const f=n=>Math.round(n).toLocaleString('ja-JP');
 document.getElementById('r1').textContent=f(day);document.getElementById('r2').textContent=f(day*g('d'));document.getElementById('r3').textContent=f(day*g('d')*12);}
['w','h','d','p'].forEach(i=>document.getElementById(i).addEventListener('input',calc));calc();
</script>'''
pages.append(page("/tools/denki/", "家電の電気代 計算ツール|Honest Guide", "消費電力と使用時間から、家電の電気代の目安を計算できる無料ツール。", DENKI))

tools_body = f'''<h1>計算ツール</h1><ul class="cards">
<li><a href="{BASE}/tools/area/"><b>坪・平米・畳の換算</b><span>広さの単位をまとめて換算</span></a></li>
<li><a href="{BASE}/tools/denki/"><b>家電の電気代</b><span>消費電力と時間から電気代の目安</span></a></li></ul>'''
pages.append(page("/tools/", "計算ツール一覧|Honest Guide", "暮らしの計算ツール一覧。", tools_body))

# ---------- 記事(content/*.md) ----------
articles = []
for f in sorted((ROOT / "content").glob("*.md")):
    raw = f.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m: continue
    meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    body_md = m.group(2)
    # {{rakuten:URL|ラベル}} をアフィリエイトリンクに置換
    body_md = re.sub(r"\{\{rakuten:(.+?)\|(.+?)\}\}", lambda x: rakuten_link(x.group(1), x.group(2)), body_md)
    body_html = markdown.markdown(body_md, extensions=["tables"])
    slug = f.stem
    articles.append((slug, meta))
    body = f'<article><h1>{html.escape(meta["title"])}</h1><p class="date">更新日:{meta.get("updated", TODAY)}</p>{PR}{body_html}</article>'
    pages.append(page(f"/guides/{slug}/", f'{meta["title"]}|Honest Guide', meta.get("description", ""), body, article=True))

lst = "".join(f'<li><a href="{BASE}/guides/{s}/"><b>{html.escape(m["title"])}</b><span>{html.escape(m.get("description",""))}</span></a></li>' for s, m in articles) or "<li>準備中です。</li>"
pages.append(page("/guides/", "えらび方ガイド一覧|Honest Guide", "暮らしの道具のえらび方ガイド一覧。", f"<h1>えらび方ガイド</h1><ul class=\"cards\">{lst}</ul>"))

# ---------- 固定ページ ----------
about = f'''<h1>運営者情報</h1><table class="plain"><tr><th>サイト名</th><td>{CFG["site_name"]}</td></tr>
<tr><th>運営者</th><td>{CFG["operator"]}(個人)</td></tr>
<tr><th>お問い合わせ</th><td><a href="{CFG["contact_url"]}">BOOTHショップ「{CFG["operator"]}」</a>のメッセージ機能からご連絡ください。</td></tr></table>
<h2>このサイトについて</h2><p>暮らしのなかの「計算がめんどう」「どれを選べばいいか分からない」を、少しだけ楽にするための道具箱です。計算ツールと、道具のえらび方ガイドを載せています。</p>
<h2>広告について</h2><p>当サイトは、楽天アフィリエイトなどのアフィリエイトプログラムに参加しています。商品リンクから購入されると、当サイトに報酬が入ることがあります。報酬の有無で、記事の内容や評価を変えることはしません。</p>
<h2>記事の内容について</h2><p>できるだけ正確な情報を載せるよう努めていますが、商品の仕様や価格、制度の内容は変わることがあります。購入や手続きの前に、必ず公式サイトや販売ページで最新の情報をご確認ください。</p>
<h2>AIの利用について</h2><p>記事の下書きや調べものに、AI(Claude)を使っています。公開前に内容を確認しています。</p>'''
pages.append(page("/about/", "運営者情報|Honest Guide", "運営者情報と、広告・AI利用についてのご案内。", about))

privacy = '''<h1>プライバシーポリシー</h1>
<h2>個人情報の取り扱い</h2><p>当サイトでは、お問い合わせの際に、お名前やメールアドレスなどの個人情報をお伺いすることがあります。いただいた情報は、お問い合わせへの返信のためだけに使い、法令に基づく場合を除き、第三者に渡すことはありません。</p>
<h2>アクセス解析・広告について</h2><p>当サイトは、今後、アクセス解析ツールや広告サービスを利用することがあります。これらは、Cookie(クッキー)を使って、閲覧の情報を集めることがあります。この情報から、個人が特定されることはありません。Cookieは、お使いのブラウザの設定で無効にできます。</p>
<h2>アフィリエイトプログラムについて</h2><p>当サイトは、楽天アフィリエイトなどに参加しています。商品リンクをクリックすると、リンク先のサービスがCookieを使って、購入の情報を記録することがあります。</p>
<h2>免責事項</h2><p>当サイトの情報は、できるだけ正確に載せるよう努めていますが、正確さや安全さを保証するものではありません。当サイトの情報で生じた損害について、責任を負いかねます。</p>
<h2>改定</h2><p>この内容は、予告なく変えることがあります。</p>'''
pages.append(page("/privacy/", "プライバシーポリシー|Honest Guide", "当サイトのプライバシーポリシー。", privacy))

# ---------- トップ ----------
top = f'''<section class="hero"><h1>{CFG["site_name"]}</h1><p>{CFG["tagline"]}</p></section>
<h2>計算ツール</h2><ul class="cards"><li><a href="{BASE}/tools/area/"><b>坪・平米・畳の換算</b><span>広さの単位をまとめて換算</span></a></li>
<li><a href="{BASE}/tools/denki/"><b>家電の電気代</b><span>消費電力と時間から電気代の目安</span></a></li></ul>
<h2>えらび方ガイド</h2><ul class="cards">{lst}</ul>'''
pages.append(page("/", "Honest Guide|暮らしの計算と、えらび方の道具箱", "計算ツールと、道具のえらび方ガイド。", top))

# ---------- サイトマップ等 ----------
urls = "".join(f'<url><loc>{CFG["base_url"]}{p}</loc><lastmod>{TODAY}</lastmod></url>' for p in pages)
(OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
(OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {CFG["base_url"]}/sitemap.xml\n', encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")
print(f"{len(pages)} pages, {len(articles)} articles")
