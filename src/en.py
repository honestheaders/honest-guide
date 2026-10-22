"""English section (/en/). Articles live in content_en/*.md. No affiliate links here:
the only product links are to Honest Tools' own extensions and Gumroad products, written as
{{product:headers}}, {{product:cookies}}, {{product:scraper}}, {{product:checklist}} or {{product:templates}}."""
import json, re, html, datetime, pathlib, shutil
import markdown
from en_tools import TOOLS, BODIES, TOOL_CSS

PRODUCTS = {
    "headers": ("Honest Headers (free Chrome extension)",
                "Add, change or remove HTTP request and response headers. Profiles, URL filters, ModHeader JSON import. No data collection.",
                "https://chromewebstore.google.com/detail/nomciaobihmigkiocpafmhmhcabpneif", "Get it on the Chrome Web Store"),
    "cookies": ("Honest Cookies (free Chrome extension, open source)",
                "View, edit, add, delete, export and import cookies. Installs with no site access and asks for one site at a time.",
                "https://github.com/honestheaders/honest-cookies", "Get the source on GitHub"),
    "scraper": ("Honest Scraper (free Chrome extension, open source)",
                "Pick one element and get every similar one as a table, with a live XPath tester. Copy to Google Sheets or Excel, or save CSV. No site access until you click.",
                "https://chromewebstore.google.com/detail/cjannokcnbkomcfalmhahpiffpkjbfla", "Get it on the Chrome Web Store"),
    "checklist": ("Security Headers: 5-Minute Checklist (PDF, pay what you want from $0)",
                  "A 2-page printable version of the checklist, with sources.",
                  "https://honesttools.gumroad.com/l/irlsg", "Get the PDF on Gumroad"),
    "templates": ("Security Headers Config Templates ($7 PDF)",
                  "Copy-paste settings for nginx, Apache, Cloudflare and Vercel, with a safe rollout order.",
                  "https://honesttools.gumroad.com/l/ypsvgk", "See it on Gumroad"),
}

DISCLOSURE = ('<p class="pr">Disclosure: Honest Tools makes Honest Headers, Honest Cookies, Honest Scraper and the PDFs linked on this site. '
              'Links to them are links to our own products. This section has no ads and no affiliate links.</p>')

CSS_EN = 'article a{overflow-wrap:anywhere}td code{overflow-wrap:anywhere}article table{display:block;overflow-x:auto}body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.7}code{background:#f1f1ec;padding:1px 4px;border-radius:4px;font-size:.92em}pre{background:#f1f1ec;padding:12px;border-radius:8px;overflow-x:auto}pre code{padding:0}.own{background:#1f4e79;box-shadow:0 2px 0 #12304d}.own:hover,.own:focus-visible{background:#163a5c}.own .shop{color:#1f4e79}'

PRO = ('<p class="ispec pro">Free to use. Optional Pro features (redirects, rules for one tab only, resource-type filters, auto-off timer): '
       '<a href="https://honesttools.gumroad.com/l/rixjq" rel="noopener" target="_blank">$9 one-time license on Gumroad</a>.</p>')
# 無料ツールのページに出す自社商品(ツールを使った人が次に使う道具)
TOOL_PRODUCTS = {"security-headers-checker": ["headers", "templates"], "set-cookie-builder": ["cookies"], "cookie-converter": ["cookies"],
                 "xpath-tester": ["scraper"], "php-version-checker": ["checklist", "templates"], "mixed-content-finder": ["checklist", "templates"]}

ICONS = {"headers": "honest-headers-48.png", "cookies": "honest-cookies-48.png", "scraper": "honest-scraper-48.png"}
SRC = pathlib.Path(__file__).resolve().parent
TOOL_FOR = {"hsts-rollout-max-age-preload": "mixed-content-finder", "security-headers-checklist": "security-headers-checker", "samesite-cookie-attribute": "set-cookie-builder", "edit-cookies-in-chrome": "set-cookie-builder", "test-xpath-in-chrome-devtools": "xpath-tester", "web-page-table-to-spreadsheet-xpath": "xpath-tester", "cookie-editor-json-to-cookies-txt-for-curl": "cookie-converter", "php-security-release-october-2026-check-your-version": "php-version-checker"}
REPORT = '<p class="fix">Found a mistake or something out of date? <a href="https://github.com/honestheaders/honest-headers/issues">Tell us on GitHub</a>. We check each fact against the sources above.</p>'

CSS_EN += ('.item .iname img{width:28px;height:28px;vertical-align:-7px;margin-right:8px;border-radius:6px}'
           '.answer{background:#eef3f8;border-left:5px solid #1f4e79;border-radius:8px;padding:12px 16px;margin:18px 0}.answer .ah{margin:0;font-size:13px;font-weight:700;color:#1f4e79;letter-spacing:.03em}.answer p{margin:4px 0 0}'
           '.toc{background:#fff;border:1px solid #ddd;border-radius:10px;padding:10px 16px;margin:18px 0;font-size:15px}.toc p{margin:0;font-size:13px;color:#666}.toc ol{margin:6px 0 0;padding-left:20px}.toc li{margin:2px 0}.toc a{color:#1f4e79;margin-left:0;font-size:inherit;text-decoration:underline}'
           'figure.dia{margin:20px auto;max-width:520px;background:#fff;border:1px solid #ddd;border-radius:10px;padding:10px}figure.dia svg,figure.shot img{display:block;width:100%;height:auto}'
           'figure.shot{margin:20px auto;max-width:520px}figure.shot img{border:1px solid #ddd;border-radius:10px}figcaption{font-size:13px;color:#666;text-align:center;margin-top:6px}'
           'pre{position:relative}.cp{position:absolute;top:6px;right:6px;font:12px system-ui,sans-serif;background:#fff;border:1px solid #bbb;border-radius:6px;padding:3px 8px;cursor:pointer}'
           'h2[id]{scroll-margin-top:12px}.tl{background:#fff8dc;border:1px solid #ecd98a;border-radius:8px;padding:8px 12px;font-size:15px}.fix{font-size:13px;color:#666;border-top:1px solid #ddd;padding-top:10px;margin-top:28px}' + TOOL_CSS)

COPY_JS = ('<script>document.querySelectorAll("article pre").forEach(function(p){var b=document.createElement("button");b.type="button";b.className="cp";b.textContent="Copy";'
           'b.onclick=function(){navigator.clipboard.writeText((p.querySelector("code")||p).innerText).then(function(){b.textContent="Copied";setTimeout(function(){b.textContent="Copy"},1500)})};p.appendChild(b)})</script>')

STOP = set("a an and the to of in on for with how what why is it its your you or by from vs do does chrome".split())

def topic_words(title):
    return {w for w in re.findall(r"[a-z]+", title.lower()) if w not in STOP and len(w) > 2} | {w.rstrip("s") for w in re.findall(r"[a-z]+", title.lower()) if len(w) > 3}

def diagram(name, caption):
    svg = (SRC / "diagrams" / f"{name}.svg").read_text(encoding="utf-8").strip()
    return f'<figure class="dia">{svg}<figcaption>{html.escape(caption)}</figcaption></figure>'

def enhance(body_html, extra=""):
    """Short-answer box, table of contents with reading time, diagrams and screenshots."""
    body_html = re.sub(r"<p>\{\{diagram:([\w-]+)\|([^}]*)\}\}</p>", lambda m: diagram(m.group(1), m.group(2)), body_html)
    def first(m):
        inner = re.sub(r"^(<strong>)?Short answer:?(</strong>)?:?\s*", "", m.group(1))
        inner = re.sub(r"^(<[^>]+>)?([a-z])", lambda x: (x.group(1) or "") + x.group(2).upper(), inner)
        return f'<div class="answer"><p class="ah">THE SHORT ANSWER</p><p>{inner}</p></div>{extra}'
    body_html = re.sub(r"^\s*<p>(.*?)</p>", first, body_html, count=1, flags=re.S)
    heads, used = [], set()
    def anchor(m):
        text = re.sub(r"<[^>]+>", "", m.group(1))
        hid = re.sub(r"[^a-z0-9]+", "-", html.unescape(text).lower()).strip("-")[:48] or "s"
        while hid in used:
            hid += "-2"
        used.add(hid)
        heads.append((hid, text))
        return f'<h2 id="{hid}">{m.group(1)}</h2>'
    body_html = re.sub(r"<h2>(.*?)</h2>", anchor, body_html)
    words = len(re.findall(r"[A-Za-z0-9'-]+", re.sub(r"<svg.*?</svg>|<[^>]+>", " ", body_html, flags=re.S)))
    if len(heads) >= 3:
        items = "".join(f'<li><a href="#{h}">{t}</a></li>' for h, t in heads)
        toc = f'<nav class="toc" aria-label="On this page"><p>On this page · about {max(1, round(words / 220))} min read</p><ol>{items}</ol></nav>'
        body_html = body_html.replace("</div>" + extra, "</div>" + extra + toc, 1) if body_html.startswith('<div class="answer">') else toc + body_html
    return body_html

def product_card(key, base=""):
    name, desc, url, label = PRODUCTS[key]
    icon = f'<img src="{base}/img/{ICONS[key]}" alt="" width="28" height="28">' if key in ICONS else ""
    return (f'<div class="item"><p class="iname">{icon}{html.escape(name)}</p><p class="ispec">{html.escape(desc)}</p>'
            f'<a class="buy own" href="{url}" rel="noopener" target="_blank"><span class="shop">Honest Tools</span>{html.escape(label)}<span class="arrow">›</span></a>{PRO if key == "headers" else ""}</div>')

def build(OUT, CFG, CSS, ROOT):
    BASE = CFG["base_path"] + "/en"
    URL = CFG["base_url"] + "/en"
    TODAY = datetime.date.today().isoformat()
    year = datetime.date.today().year

    def page(path, title, desc, body, article=False, extra_head=""):
        canon = f"{URL}{path}"
        nav = (f'<header><div class="wrap"><a class="logo" href="{BASE}/">Honest Guide</a>'
               f'<nav><a href="{BASE}/">Guides</a><a href="{BASE}/tools/">Tools</a><a href="{BASE}/about/">About</a><a href="{CFG["base_path"]}/">日本語</a></nav></div></header>')
        foot = (f'<footer><div class="wrap"><p>Practical notes on HTTP headers, cookies and browser tools, by {CFG["operator"]}. '
                f'Facts are checked against official documentation; each article lists its sources and the date they were checked.</p>'
                f'<p><a href="{BASE}/about/">About</a> / <a href="{CFG["base_path"]}/privacy/">Privacy Policy</a> / <a href="{CFG["base_path"]}/terms/">Terms of Service</a></p><p>&copy; {year} {CFG["operator"]}</p></div></footer>')
        doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="google-site-verification" content="hqAGwjMx_F-TdJl79qigCCcuhYe7_9BUhfd7nEK2TMI"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:url" content="{canon}"><meta property="og:site_name" content="Honest Guide"><meta name="twitter:card" content="summary"><meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="{'article' if article else 'website'}">
<link rel="icon" href="{CFG["base_path"]}/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Honest Guide (English)" href="{URL}/feed.xml">{extra_head}
<style>{CSS}{CSS_EN}</style></head><body>{nav}<main class="wrap">{body}</main>{foot}</body></html>'''
        d = OUT / "en" / path.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(doc, encoding="utf-8")
        return "/en" + path

    img_out = OUT / "en" / "img"
    img_out.mkdir(parents=True, exist_ok=True)
    for f in (SRC / "img").glob("*"):
        shutil.copyfile(f, img_out / f.name)

    pages, arts = [], []
    for f in sorted((ROOT / "content_en").glob("*.md")):
        m = re.match(r"---\n(.*?)\n---\n(.*)", f.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        meta = {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)}
        body_md = re.sub(r"\{\{product:(\w+)\}\}", lambda x: product_card(x.group(1), BASE), m.group(2))
        body_md = re.sub(r"\{\{shot:([\w.-]+)\|([^}]*)\}\}", lambda x: f'<figure class="shot"><img src="{BASE}/img/{x.group(1)}" alt="{html.escape(x.group(2))}" loading="lazy"><figcaption>{html.escape(x.group(2))}</figcaption></figure>', body_md)
        tool = TOOL_FOR.get(f.stem)
        extra = (f'<p class="tl">Free tool: <a href="{BASE}/tools/{tool}/">{html.escape(dict((t[0], t[1]) for t in TOOLS)[tool])}</a>, runs in your browser.</p>') if tool else ""
        arts.append((f.stem, meta, enhance(markdown.markdown(body_md, extensions=["tables", "fenced_code"]), extra)))
    arts.sort(key=lambda a: a[1].get("updated", ""), reverse=True)

    for slug, meta, body_html in arts:
        mine = topic_words(meta["title"])
        rel = sorted((a for a in arts if a[0] != slug), key=lambda a: -len(mine & topic_words(a[1]["title"])))[:3]
        rel_html = "".join(f'<li><a href="{BASE}/{r[0]}/">{html.escape(r[1]["title"])}</a></li>' for r in rel)
        related = f'<section class="related"><h2>More guides</h2><ul>{rel_html}</ul></section>' if rel else ""
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": meta["title"], "description": meta.get("description", ""),
                         "inLanguage": "en", "dateModified": meta.get("updated", TODAY), "author": {"@type": "Organization", "name": CFG["operator"]},
                         "publisher": {"@type": "Organization", "name": CFG["operator"]}, "mainEntityOfPage": f"{URL}/{slug}/"})
        body = (f'<nav class="crumb"><a href="{BASE}/">Guides</a> › {html.escape(meta["title"])}</nav><article><h1>{html.escape(meta["title"])}</h1>'
                f'<p class="date">Updated {meta.get("updated", TODAY)}</p>{DISCLOSURE}{body_html}{REPORT}</article>{related}{COPY_JS if "<pre>" in body_html else ""}')
        pages.append(page(f"/{slug}/", f'{meta["title"]} | Honest Guide', meta.get("description", ""), body, True, f'<script type="application/ld+json">{ld}</script>'))

    lst = "".join(f'<li><a href="{BASE}/{s}/"><b>{html.escape(m["title"])}</b><span>{html.escape(m.get("description", ""))}</span></a></li>' for s, m, _ in arts) or "<li>Coming soon.</li>"
    tools = "".join(f'<li><a href="{u}" rel="noopener" target="_blank"><b>{html.escape(n)}</b><span>{html.escape(d)}</span></a></li>' for n, d, u, _ in PRODUCTS.values())
    free = "".join(f'<li><a href="{BASE}/tools/{sl}/"><b>{html.escape(t)}</b><span>{html.escape(d)}</span></a></li>' for sl, t, d in TOOLS)
    for sl, t, d in TOOLS:
        crumb = f'<nav class="crumb"><a href="{BASE}/">Guides</a> › <a href="{BASE}/tools/">Tools</a> › {html.escape(t)}</nav>'
        body_t = BODIES[sl].replace("BASE/", BASE + "/")
        guides = [a for a in arts if TOOL_FOR.get(a[0]) == sl]
        nxt = ""
        if guides:
            nxt += '<h2 id="guides">Guides that use this tool</h2><ul>' + "".join(f'<li><a href="{BASE}/{a[0]}/">{html.escape(a[1]["title"])}</a></li>' for a in guides) + "</ul>"
        if TOOL_PRODUCTS.get(sl):
            nxt += '<h2 id="next">Doing this often?</h2>' + DISCLOSURE + "".join(product_card(k, BASE) for k in TOOL_PRODUCTS[sl])
        body_t = body_t.replace('<h2 id="sources"', nxt + '<h2 id="sources"', 1) if '<h2 id="sources"' in body_t else body_t + nxt
        pages.append(page(f"/tools/{sl}/", f"{t} | Honest Guide", d, crumb + "<article>" + body_t + "</article>"))
    pages.append(page("/tools/", "Free tools for HTTP headers and cookies | Honest Guide", "Free browser tools: check security headers and build Set-Cookie headers. Nothing is sent to a server.",
                      f'<h1>Free tools</h1><p>Small tools that run only in your browser. Nothing you type is sent anywhere.</p><ul class="cards">{free}</ul>'))
    top = (f'<section class="hero"><h1>Honest Guide</h1><p>Plain answers about HTTP headers, cookies and browser developer tools. '
           f'Checked against official docs, with sources and dates.</p></section>'
           f'<p class="tl"><b>Moving off ModHeader?</b> Start with <a href="{BASE}/modheader-removed-from-chrome-what-to-do/">what was reported and how to check any header extension</a>, '
           f'then <a href="{BASE}/move-modheader-rules-append-not-supported/">how to move your rules</a>.</p><h2>Guides</h2><ul class="cards">{lst}</ul>'
           f'<h2>Free tools (run in your browser)</h2><ul class="cards">{free}</ul><h2>Tools we make</h2><ul class="cards">{tools}</ul>')
    pages.append(page("/", "Honest Guide | HTTP headers, cookies and browser dev tools, explained", "Plain answers about HTTP headers, cookies and browser developer tools, checked against official documentation.", top))

    about = f'''<h1>About</h1><p>Honest Guide is written by {CFG["operator"]}, a small maker of browser tools. We write about the problems our tools solve: HTTP headers, cookies and browser developer tools.</p>
<h2>How we write</h2><ul><li>Facts, numbers and steps come from official documentation (MDN, Chrome for Developers, OWASP, vendor docs). Every article lists its sources and the date we checked them.</li>
<li>We do not write fake reviews or made-up experiences, and we do not rank products we have not measured.</li>
<li>Each article says who the approach is <em>not</em> for.</li><li>We use AI (Claude) to help draft and research. Articles are checked against the sources before publishing.</li></ul>
<h2>Our products</h2><p>We make Honest Headers, Honest Cookies, Honest Scraper and a few PDFs. When an article mentions them, it says so. There are no ads or affiliate links in the English section.</p>
<h2>Contact</h2><p>Please open an issue on <a href="https://github.com/honestheaders/honest-headers/issues">GitHub</a>.</p>'''
    pages.append(page("/about/", "About | Honest Guide", "Who writes Honest Guide and how articles are checked.", about))
    import legal
    pages.append(page("/privacy/", "Privacy Policy | Honest Guide", "Privacy policy for Honest Guide and Honest Tools.", legal.privacy(CFG["base_path"])))

    items = "".join(f'<item><title>{html.escape(m["title"])}</title><link>{URL}/{s}/</link><guid>{URL}/{s}/</guid><description>{html.escape(m.get("description", ""))}</description>'
                    f'<pubDate>{datetime.datetime.strptime(m.get("updated", TODAY), "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate></item>' for s, m, _ in arts)
    (OUT / "en" / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Honest Guide (English)</title><link>{URL}/</link>'
                                         f'<description>HTTP headers, cookies and browser dev tools, explained</description><language>en</language>{items}</channel></rss>', encoding="utf-8")
    return pages, len(arts)
