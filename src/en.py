"""English section (/en/). Articles live in content_en/*.md. No affiliate links here:
the only product links are to Honest Tools' own extensions and Gumroad products, written as
{{product:headers}}, {{product:cookies}}, {{product:checklist}} or {{product:templates}}."""
import json, re, html, datetime, pathlib
import markdown

PRODUCTS = {
    "headers": ("Honest Headers (free Chrome extension)",
                "Add, change or remove HTTP request and response headers. Profiles, URL filters, ModHeader JSON import. No data collection.",
                "https://chromewebstore.google.com/detail/nomciaobihmigkiocpafmhmhcabpneif", "Get it on the Chrome Web Store"),
    "cookies": ("Honest Cookies (free Chrome extension, open source)",
                "View, edit, add, delete, export and import cookies. Installs with no site access and asks for one site at a time.",
                "https://chromewebstore.google.com/detail/fajimapdhdmcpbccjflmelfilgfpakci", "Get it on the Chrome Web Store"),
    "checklist": ("Security Headers: 5-Minute Checklist (PDF, pay what you want from $0)",
                  "A 2-page printable version of the checklist, with sources.",
                  "https://honesttools.gumroad.com/l/irlsg", "Get the PDF on Gumroad"),
    "templates": ("Security Headers Config Templates ($7 PDF)",
                  "Copy-paste settings for nginx, Apache, Cloudflare and Vercel, with a safe rollout order.",
                  "https://honesttools.gumroad.com/l/ypsvgk", "See it on Gumroad"),
}

DISCLOSURE = ('<p class="pr">Disclosure: Honest Tools makes Honest Headers, Honest Cookies and the PDFs linked on this site. '
              'Links to them are links to our own products. This section has no ads and no affiliate links.</p>')

CSS_EN = 'article a{overflow-wrap:anywhere}td code{overflow-wrap:anywhere}article table{display:block;overflow-x:auto}body{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;line-height:1.7}code{background:#f1f1ec;padding:1px 4px;border-radius:4px;font-size:.92em}pre{background:#f1f1ec;padding:12px;border-radius:8px;overflow-x:auto}pre code{padding:0}.own{background:#1f4e79;box-shadow:0 2px 0 #12304d}.own:hover,.own:focus-visible{background:#163a5c}.own .shop{color:#1f4e79}'

def product_card(key):
    name, desc, url, label = PRODUCTS[key]
    return (f'<div class="item"><p class="iname">{html.escape(name)}</p><p class="ispec">{html.escape(desc)}</p>'
            f'<a class="buy own" href="{url}" rel="noopener" target="_blank"><span class="shop">Honest Tools</span>{html.escape(label)}<span class="arrow">›</span></a></div>')

def build(OUT, CFG, CSS, ROOT):
    BASE = CFG["base_path"] + "/en"
    URL = CFG["base_url"] + "/en"
    TODAY = datetime.date.today().isoformat()
    year = datetime.date.today().year

    def page(path, title, desc, body, article=False, extra_head=""):
        canon = f"{URL}{path}"
        nav = (f'<header><div class="wrap"><a class="logo" href="{BASE}/">Honest Guide</a>'
               f'<nav><a href="{BASE}/">Guides</a><a href="{BASE}/about/">About</a><a href="{CFG["base_path"]}/">日本語</a></nav></div></header>')
        foot = (f'<footer><div class="wrap"><p>Practical notes on HTTP headers, cookies and browser tools, by {CFG["operator"]}. '
                f'Facts are checked against official documentation; each article lists its sources and the date they were checked.</p>'
                f'<p><a href="{BASE}/about/">About</a> / <a href="{BASE}/privacy/">Privacy</a></p><p>&copy; {year} {CFG["operator"]}</p></div></footer>')
        doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="google-site-verification" content="hqAGwjMx_F-TdJl79qigCCcuhYe7_9BUhfd7nEK2TMI"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{html.escape(title)}"><meta property="og:description" content="{html.escape(desc)}"><meta property="og:type" content="{'article' if article else 'website'}">
<link rel="icon" href="{CFG["base_path"]}/favicon.svg" type="image/svg+xml"><link rel="alternate" type="application/rss+xml" title="Honest Guide (English)" href="{URL}/feed.xml">{extra_head}
<style>{CSS}{CSS_EN}</style></head><body>{nav}<main class="wrap">{body}</main>{foot}</body></html>'''
        d = OUT / "en" / path.strip("/")
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(doc, encoding="utf-8")
        return "/en" + path

    pages, arts = [], []
    for f in sorted((ROOT / "content_en").glob("*.md")):
        m = re.match(r"---\n(.*?)\n---\n(.*)", f.read_text(encoding="utf-8"), re.S)
        if not m:
            continue
        meta = {k.strip(): v.strip() for k, v in (l.split(":", 1) for l in m.group(1).splitlines() if ":" in l)}
        body_md = re.sub(r"\{\{product:(\w+)\}\}", lambda x: product_card(x.group(1)), m.group(2))
        arts.append((f.stem, meta, markdown.markdown(body_md, extensions=["tables", "fenced_code"])))
    arts.sort(key=lambda a: a[1].get("updated", ""), reverse=True)

    for slug, meta, body_html in arts:
        rel = [a for a in arts if a[0] != slug][:3]
        rel_html = "".join(f'<li><a href="{BASE}/{r[0]}/">{html.escape(r[1]["title"])}</a></li>' for r in rel)
        related = f'<section class="related"><h2>More guides</h2><ul>{rel_html}</ul></section>' if rel else ""
        ld = json.dumps({"@context": "https://schema.org", "@type": "Article", "headline": meta["title"], "description": meta.get("description", ""),
                         "inLanguage": "en", "dateModified": meta.get("updated", TODAY), "author": {"@type": "Organization", "name": CFG["operator"]},
                         "publisher": {"@type": "Organization", "name": CFG["operator"]}, "mainEntityOfPage": f"{URL}/{slug}/"})
        body = (f'<nav class="crumb"><a href="{BASE}/">Guides</a> › {html.escape(meta["title"])}</nav><article><h1>{html.escape(meta["title"])}</h1>'
                f'<p class="date">Updated {meta.get("updated", TODAY)}</p>{DISCLOSURE}{body_html}</article>{related}')
        pages.append(page(f"/{slug}/", f'{meta["title"]} | Honest Guide', meta.get("description", ""), body, True, f'<script type="application/ld+json">{ld}</script>'))

    lst = "".join(f'<li><a href="{BASE}/{s}/"><b>{html.escape(m["title"])}</b><span>{html.escape(m.get("description", ""))}</span></a></li>' for s, m, _ in arts) or "<li>Coming soon.</li>"
    tools = "".join(f'<li><a href="{u}" rel="noopener" target="_blank"><b>{html.escape(n)}</b><span>{html.escape(d)}</span></a></li>' for n, d, u, _ in PRODUCTS.values())
    top = (f'<section class="hero"><h1>Honest Guide</h1><p>Plain answers about HTTP headers, cookies and browser developer tools. '
           f'Checked against official docs, with sources and dates.</p></section><h2>Guides</h2><ul class="cards">{lst}</ul>'
           f'<h2>Tools we make</h2><ul class="cards">{tools}</ul>')
    pages.append(page("/", "Honest Guide | HTTP headers, cookies and browser dev tools, explained", "Plain answers about HTTP headers, cookies and browser developer tools, checked against official documentation.", top))

    about = f'''<h1>About</h1><p>Honest Guide is written by {CFG["operator"]}, a small maker of browser tools. We write about the problems our tools solve: HTTP headers, cookies and browser developer tools.</p>
<h2>How we write</h2><ul><li>Facts, numbers and steps come from official documentation (MDN, Chrome for Developers, OWASP, vendor docs). Every article lists its sources and the date we checked them.</li>
<li>We do not write fake reviews or made-up experiences, and we do not rank products we have not measured.</li>
<li>Each article says who the approach is <em>not</em> for.</li><li>We use AI (Claude) to help draft and research. Articles are checked against the sources before publishing.</li></ul>
<h2>Our products</h2><p>We make Honest Headers, Honest Cookies and a few PDFs. When an article mentions them, it says so. There are no ads or affiliate links in the English section.</p>
<h2>Contact</h2><p>Please open an issue on <a href="https://github.com/honestheaders/honest-headers/issues">GitHub</a>.</p>'''
    pages.append(page("/about/", "About | Honest Guide", "Who writes Honest Guide and how articles are checked.", about))
    privacy = '''<h1>Privacy</h1><p>This site is a static site hosted on GitHub Pages. We do not run analytics, ads or tracking scripts, and we do not set cookies. GitHub may log technical information such as IP addresses when serving pages; see GitHub's privacy statement.</p>
<p>Links to Gumroad and the Chrome Web Store take you to those services, which have their own privacy policies.</p><p>This policy may change; the current version is always on this page.</p>'''
    pages.append(page("/privacy/", "Privacy | Honest Guide", "Privacy policy for the English section of Honest Guide.", privacy))

    items = "".join(f'<item><title>{html.escape(m["title"])}</title><link>{URL}/{s}/</link><guid>{URL}/{s}/</guid><description>{html.escape(m.get("description", ""))}</description>'
                    f'<pubDate>{datetime.datetime.strptime(m.get("updated", TODAY), "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")}</pubDate></item>' for s, m, _ in arts)
    (OUT / "en" / "feed.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>Honest Guide (English)</title><link>{URL}/</link>'
                                         f'<description>HTTP headers, cookies and browser dev tools, explained</description><language>en</language>{items}</channel></rss>', encoding="utf-8")
    return pages, len(arts)
