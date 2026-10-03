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

def rakuten_href(url):
    """楽天のURLをアフィリエイトリンクのURLに包む。IDが未設定ならそのまま。"""
    aid = CFG["rakuten_affiliate_id"]
    if not aid:
        return url
    from urllib.parse import quote
    return f"https://hb.afl.rakuten.co.jp/hgc/{aid}/?pc={quote(url, safe='')}&link_type=text"

def search_url(words):
    """楽天市場の検索ページのURL。words は「加湿器 気化式 14畳」のような空白区切りの語。"""
    from urllib.parse import quote
    return "https://search.rakuten.co.jp/search/mall/" + quote(words.strip()) + "/"

def rakuten_link(url, label):
    """押しやすいボタン形のリンク(楽天)。表示名の先頭の「楽天市場で」は、ボタンに楽天市場の印があるので省く。"""
    label = re.sub(r"^楽天(市場)?で", "", label)
    return (f'<a class="buy" href="{html.escape(rakuten_href(url))}" rel="nofollow sponsored noopener" target="_blank">'
            f'<span class="shop">楽天市場</span>{html.escape(label)}<span class="arrow">›</span></a>')

def item_card(name, spec, fit, words, label=""):
    """型番カード。name=商品名(型番)、spec=公式で確認した仕様、fit=向いている人、words=楽天で探す語。"""
    btn = rakuten_link(search_url(words), label or "楽天で価格とレビューを見る")
    return (f'<div class="item"><p class="iname">{html.escape(name)}</p>'
            f'<p class="ispec">{html.escape(spec)}</p>'
            f'<p class="ifit"><b>向いている人</b>{html.escape(fit)}</p>{btn}</div>')

def expand_links(md):
    """記事の中の商品リンクの書き方を、HTMLに変える。
    {{rakuten:URL|表示名}}            … 楽天のURLを直接指定するボタン
    {{search:探す語|表示名}}           … 楽天の検索ページへのボタン(URLを自分で作らなくてよい)
    {{item:商品名|公式の仕様|向いている人|探す語}} … 型番カード
    """
    md = re.sub(r"\{\{item:(.+?)\|(.+?)\|(.+?)\|(.+?)\}\}", lambda x: item_card(*[g.strip() for g in x.groups()]), md)
    md = re.sub(r"\{\{search:(.+?)\|(.+?)\}\}", lambda x: rakuten_link(search_url(x.group(1)), x.group(2).strip()), md)
    md = re.sub(r"\{\{rakuten:(.+?)\|(.+?)\}\}", lambda x: rakuten_link(x.group(1).strip(), x.group(2).strip()), md)
    return md

def quick_box(body_html):
    """記事の最初の段落のすぐ後ろに「先に商品を見たい人へ」の箱を入れる(記事の中のボタンを集めて並べる)。"""
    btns = re.findall(r'<a class="buy".*?</a>', body_html, re.S)
    uniq = []
    for b in btns:
        if b not in uniq:
            uniq.append(b)
    # 手続きの記事(チェック表への案内がある記事)は、手続きを読みに来た人なので先頭の箱は出さない
    if not uniq or f"{BASE}/templates/" in body_html:
        return body_html
    box = ('<aside class="quick"><p class="qh">先に商品を見たい人へ</p>' + "".join(uniq[:4]) +
           '<p class="qn">選び方のポイントは、このあと本文で説明しています。</p></aside>')
    i = body_html.find("</p>")
    return body_html if i < 0 else body_html[:i+4] + box + body_html[i+4:]

PR = '<p class="pr">※この記事にはプロモーション(広告)が含まれます。商品リンクから購入されると、当サイトに報酬が入ることがあります。</p>'

def page(path, title, desc, body, article=False, extra_head=""):
    canon = f'{CFG["base_url"]}{path}'
    nav = f'''<header><div class="wrap"><a class="logo" href="{BASE}/">{CFG["site_name"]}</a>
<nav><a href="{BASE}/tools/">計算ツール</a><a href="{BASE}/guides/">えらび方ガイド</a><a href="{BASE}/templates/">手続き表</a><a href="{BASE}/about/">運営者情報</a></nav></div></header>'''
    foot = f'''<footer><div class="wrap"><p>当サイトは、楽天アフィリエイトなどのアフィリエイトプログラムに参加しています。商品リンクを通じて報酬を得ることがあります。</p>
<p><a href="{BASE}/about/">運営者情報</a> / <a href="{BASE}/privacy/">プライバシーポリシー</a></p><p>&copy; {datetime.date.today().year} {CFG["operator"]}</p></div></footer>'''
    doc = f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="google-site-verification" content="hqAGwjMx_F-TdJl79qigCCcuhYe7_9BUhfd7nEK2TMI"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="{'article' if article else 'website'}">
<link rel="icon" href="{BASE}/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="{CFG["site_name"]}" href="{CFG["base_url"]}/feed.xml">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebSite","name":"{CFG["site_name"]}","url":"{CFG["base_url"]}/"}}</script>{extra_head}
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
</script>
<h2>広さを測る道具</h2><p>部屋の広さを自分で測るときに使う道具です。</p>
''' + rakuten_link(search_url("レーザー距離計"), "レーザー距離計を探す") + rakuten_link(search_url("メジャー 5.5m"), "メジャー(5.5m)を探す") + f'''<p class="note">畳・坪・平米のくわしい関係は<a href="{BASE}/guides/tatami-tsubo-heibei/">こちらの記事</a>で説明しています。</p>'''
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
</script>
<h2>家電の消費電力を実際に測るには</h2><p>コンセントと家電の間につなぐと、使っている電力(W)と電気代が表示される「ワットチェッカー」という道具があります。箱に書かれた数字ではなく、実際の数字で計算できます。</p>
''' + rakuten_link(search_url("ワットチェッカー"), "ワットチェッカーを探す") + f'''<p class="note">待機電力の測り方は<a href="{BASE}/guides/taiki-denryoku/">こちらの記事</a>で説明しています。</p>'''
pages.append(page("/tools/denki/", "家電の電気代 計算ツール|Honest Guide", "消費電力と使用時間から、家電の電気代の目安を計算できる無料ツール。", DENKI))

import sys; sys.path.insert(0, str(ROOT / "src")); import kigen
KIGEN = kigen.build(page, rakuten_link, search_url, BASE, CFG)
pages += [k[0] for k in KIGEN]
kigen_cards = "".join(f'<li><a href="{BASE}{p}"><b>{html.escape(t)}</b><span>日付を入れると期限日と残り日数が出ます。カレンダー登録・LINE共有つき</span></a></li>' for p, t, d in KIGEN)

tools_body = f'''<h1>計算ツール</h1><h2>手続きの期限</h2><ul class="cards">{kigen_cards}</ul><h2>暮らしの計算</h2><ul class="cards">
<li><a href="{BASE}/tools/area/"><b>坪・平米・畳の換算</b><span>広さの単位をまとめて換算</span></a></li>
<li><a href="{BASE}/tools/denki/"><b>家電の電気代</b><span>消費電力と時間から電気代の目安</span></a></li></ul>'''
pages.append(page("/tools/", "計算ツール一覧|Honest Guide", "暮らしの計算ツール一覧。", tools_body))

# ---------- 記事(content/*.md) ----------
articles = []
articles_full = []
for f in sorted((ROOT / "content").glob("*.md")):
    raw = f.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m: continue
    meta = dict(l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    body_md = m.group(2)
    # {{rakuten:URL|ラベル}} をアフィリエイトリンクに置換
    body_md = expand_links(body_md)
    body_html = quick_box(markdown.markdown(body_md, extensions=["tables"]))
    slug = f.stem
    articles.append((slug, meta))
    articles_full.append((slug, meta, body_html))

for i, (slug, meta, body_html) in enumerate(articles_full):
    others = [a for a in articles_full if a[0] != slug]
    # 関連記事: 直前・直後の2本(単純だが偏らない)
    rel = (others[i-1:i] + others[i:i+1]) if len(others) > 1 else others
    rel = rel[:2] or others[:2]
    rel_html = "".join(f'<li><a href="{BASE}/guides/{r[0]}/">{html.escape(r[1]["title"])}</a></li>' for r in rel)
    related = f'<section class="related"><h2>関連する記事</h2><ul>{rel_html}</ul><p>計算がめんどうなときは<a href="{BASE}/tools/">計算ツール</a>もどうぞ。</p></section>' if rel else ""
    crumb = f'<nav class="crumb"><a href="{BASE}/">ホーム</a> › <a href="{BASE}/guides/">えらび方ガイド</a> › {html.escape(meta["title"])}</nav>'
    ld = json.dumps({"@context":"https://schema.org","@type":"Article","headline":meta["title"],"description":meta.get("description",""),
        "dateModified":meta.get("updated",TODAY),"author":{"@type":"Organization","name":CFG["operator"]},"publisher":{"@type":"Organization","name":CFG["operator"]},
        "mainEntityOfPage":f'{CFG["base_url"]}/guides/{slug}/'}, ensure_ascii=False)
    body = f'{crumb}<article><h1>{html.escape(meta["title"])}</h1><p class="date">更新日:{meta.get("updated", TODAY)}</p>{PR}{body_html}</article>{related}'
    pages.append(page(f"/guides/{slug}/", f'{meta["title"]}|Honest Guide', meta.get("description", ""), body, article=True, extra_head=f'<script type="application/ld+json">{ld}</script>'))

lst = "".join(f'<li><a href="{BASE}/guides/{s}/"><b>{html.escape(m["title"])}</b><span>{html.escape(m.get("description",""))}</span></a></li>' for s, m in articles) or "<li>準備中です。</li>"
pages.append(page("/guides/", "えらび方ガイド一覧|Honest Guide", "暮らしの道具のえらび方ガイド一覧。", f"<h1>えらび方ガイド</h1><ul class=\"cards\">{lst}</ul>"))

# ---------- 手続きチェック表(BOOTH) ----------
tpl = f'''<h1>手続きの期限チェック表(Excel)</h1>
<p>役所や年金などの手続きは、期限がばらばらで、数えるのがめんどうです。日付を1か所入れるだけで、すべての手続きの期限日と残り日数が自動で出るExcelの表を、{CFG["operator"]}のショップで販売しています。ExcelでもGoogleスプレッドシートでも使え、スマホでも開けます。</p>
<ul class="cards">
<li><a href="https://honest-tools.booth.pm/items/8919127" rel="noopener" target="_blank"><b>死亡後の手続き 期限チェック表(完全版)</b><span>亡くなった日を入れて8つの質問に答えると、33の手続きから、あなたの家族に必要なものだけが期限の近い順に並びます</span></a></li>
<li><a href="https://honest-tools.booth.pm/" rel="noopener" target="_blank"><b>退職後の手続き 期限チェック表(完全版)</b><span>退職日と質問の答えから、22の手続きの期限日と、失業給付を受け取れる日数の目安が出ます</span></a></li>
<li><a href="https://honest-tools.booth.pm/" rel="noopener" target="_blank"><b>引っ越しの手続き 期限チェック表(完全版)</b><span>引っ越しの日を入れると、転入届・マイナンバー・車・児童手当など30の手続きの期限日が出ます</span></a></li>
</ul>
<p>まずは無料の期限計算ツールで、主な手続きの期限だけ確かめることもできます。</p><ul class="cards">{kigen_cards}</ul>
<p>3つとも、質問に「はい・いいえ」で答えると必要な手続きだけに絞りこめる「やることリスト」、同じ窓口の手続きをまとめた「窓口別まとめ」、窓口ごとの「持ち物リスト」、期限をGoogleカレンダーに入れるボタン、すべての期限の公的な出典がついています。価格はBOOTHのページでご確認ください(3つセットもあります)。</p>
<p class="note">いずれも一般的な期限をまとめた目安で、法律・税務・社会保険の助言ではありません。個別の事情は各窓口でご確認ください。販売ページはBOOTH(ピクシブ株式会社が運営する販売サイト)です。</p>'''
pages.append(page("/templates/", "手続きの期限チェック表(Excel)|Honest Guide", "日付を入れるだけで手続きの期限日が自動で出るExcelチェック表の案内。", tpl))

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
<h2>手続きの期限を計算する(無料)</h2><ul class="cards">{kigen_cards}</ul>
<h2>計算ツール</h2><ul class="cards"><li><a href="{BASE}/tools/area/"><b>坪・平米・畳の換算</b><span>広さの単位をまとめて換算</span></a></li>
<li><a href="{BASE}/tools/denki/"><b>家電の電気代</b><span>消費電力と時間から電気代の目安</span></a></li></ul>
<h2>えらび方ガイド</h2><ul class="cards">{lst}</ul>
<h2>手続きの期限チェック表</h2><ul class="cards"><li><a href="{BASE}/templates/"><b>Excelの期限チェック表</b><span>日付を入れるだけで、手続きの期限日が自動で出ます</span></a></li></ul>'''
pages.append(page("/", "Honest Guide|暮らしの計算と、えらび方の道具箱", "計算ツールと、道具のえらび方ガイド。", top))

# ---------- サイトマップ等 ----------
urls = "".join(f'<url><loc>{CFG["base_url"]}{p}</loc><lastmod>{TODAY}</lastmod></url>' for p in pages)
(OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding="utf-8")
(OUT / "robots.txt").write_text(f'User-agent: *\nAllow: /\nSitemap: {CFG["base_url"]}/sitemap.xml\n', encoding="utf-8")
(OUT / ".nojekyll").write_text("", encoding="utf-8")
# 404
nf = f'<h1>ページが見つかりません</h1><p>アドレスが変わったか、ページがなくなった可能性があります。</p><p><a href="{BASE}/">トップページへ戻る</a> / <a href="{BASE}/guides/">記事一覧</a> / <a href="{BASE}/tools/">計算ツール</a></p>'
page("/404/", "ページが見つかりません|Honest Guide", "", nf)
shutil.move(OUT / "404" / "index.html", OUT / "404.html"); shutil.rmtree(OUT / "404")
# RSS
items = "".join(f'<item><title>{html.escape(m["title"])}</title><link>{CFG["base_url"]}/guides/{s_}/</link><guid>{CFG["base_url"]}/guides/{s_}/</guid><description>{html.escape(m.get("description",""))}</description><pubDate>{datetime.datetime.strptime(m.get("updated",TODAY),"%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0900")}</pubDate></item>' for s_, m in sorted(articles, key=lambda a: a[1].get("updated",""), reverse=True))
(OUT / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{CFG["site_name"]}</title><link>{CFG["base_url"]}/</link><description>{CFG["tagline"]}</description><language>ja</language>{items}</channel></rss>', encoding="utf-8")
# IndexNow key file (検索エンジンへの通知用)
kf = ROOT / "indexnow_key.txt"
if kf.exists():
    k = kf.read_text().strip(); (OUT / f"{k}.txt").write_text(k, encoding="utf-8")
# favicon
(OUT / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#1f4e79"/><circle cx="32" cy="32" r="20" fill="#ffe699"/><path d="M22 33l7 7 13-14" fill="none" stroke="#1f4e79" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/></svg>', encoding="utf-8")
print(f"{len(pages)} pages, {len(articles)} articles")
