"""プライバシーポリシー(/privacy/)と利用規約(/terms/)。英語だけ。
YouTube の投稿アプリ(Honest Tools Uploader)を Google の本番に切り替えるために、
honestheaders.github.io の上に置く必要がある。中身は事実だけを書く。"""

UPDATED = "2026-10-14"
CONTACT = "honestheaders.dev@gmail.com"

YT_TERMS = "https://www.youtube.com/t/terms"
G_PRIVACY = "https://policies.google.com/privacy"
G_PERMS = "https://security.google.com/settings/security/permissions"


def privacy(BASE):
    return f'''<article><h1>Privacy Policy</h1><p class="date">Last updated {UPDATED}</p>
<p>This policy covers everything published by Honest Tools: the Honest Guide website, our Chrome extensions, the products we sell on Gumroad, and our YouTube upload app, Honest Tools Uploader. In short: we do not collect personal data, and we do not sell or share any.</p>
<h2>The Honest Guide website</h2>
<ul><li>This is a static website hosted on GitHub Pages. We do not run analytics, ads or tracking scripts, and the site itself does not set cookies.</li>
<li>GitHub may log technical information, such as IP addresses, when it serves pages. See <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub's privacy statement</a>.</li>
<li>Some free tools on this site remember your inputs or checkboxes in your own browser (localStorage). That data stays on your device and is never sent to us.</li>
<li>Some Japanese pages contain Rakuten Affiliate links. If you click one, Rakuten may use cookies to record the purchase. Links to other services (Rakuten, Gumroad, the Chrome Web Store, BOOTH, GitHub, YouTube) take you to sites that have their own privacy policies.</li></ul>
<h2>Our Chrome extensions</h2>
<ul><li><b>Honest Headers</b> uses only the declarativeNetRequest, storage and alarms permissions. It does not read the content of the pages you visit and makes no network requests of its own. It collects no data. Your settings are stored only in your own browser (chrome.storage).</li>
<li><b>Honest Cookies</b> reads and changes cookies only in your own browser. It makes no network requests of its own, collects no data, and never sends cookies to us or anyone else.</li>
<li><b>Honest Scraper</b> reads a page only when you click its button or menu item, and only in that tab. What it reads stays on your computer unless you copy or save it. It makes no network requests of its own and collects no data.</li></ul>
<p>None of our extensions use analytics, telemetry, advertising or remotely hosted code.</p>
<h2>Purchases on Gumroad</h2>
<p>Our paid products (the Honest Headers Pro key, config templates and checklists) are sold through <a href="https://honesttools.gumroad.com">Gumroad</a>. Gumroad handles payment and your email address under <a href="https://gumroad.com/privacy">its own privacy policy</a>. We do not receive or store your card details.</p>
<h2>YouTube: Honest Tools Uploader</h2>
<p>Honest Tools Uploader is our own app. It uses <b>YouTube API Services</b> only to upload our own videos and captions to our own YouTube channel, Honest Tools (@honesttoolsdev). It does not access, collect, store or share data about any other YouTube user. The authorization token is stored only on our own computer and is never shared.</p>
<ul><li>By using YouTube features, you agree to the <a href="{YT_TERMS}">YouTube Terms of Service</a>.</li>
<li>Google's handling of data is described in the <a href="{G_PRIVACY}">Google Privacy Policy</a>.</li>
<li>You can revoke an app's access to your Google account at any time on the <a href="{G_PERMS}">Google security settings page</a>.</li></ul>
<h2>Children</h2><p>We do not knowingly collect information from anyone, including children.</p>
<h2>Changes</h2><p>We may update this policy. The current version, with its date, is always on this page.</p>
<h2>Contact</h2><p>Email <a href="mailto:{CONTACT}">{CONTACT}</a>. See also our <a href="{BASE}/terms/">Terms of Service</a>.</p></article>'''


def terms(BASE):
    return f'''<article><h1>Terms of Service</h1><p class="date">Last updated {UPDATED}</p>
<p>These terms apply to the Honest Guide website, the Chrome extensions and products made by Honest Tools, and our YouTube upload app, Honest Tools Uploader. By using them, you agree to these terms.</p>
<h2>Provided "as is"</h2><p>The website, extensions and products are provided "as is", without warranties of any kind. We try to keep information accurate and to check facts against official sources, but we cannot promise that everything is complete, correct or up to date. Please check important details with the official source before you rely on them.</p>
<h2>Limitation of liability</h2><p>To the extent allowed by law, Honest Tools is not liable for any loss or damage that comes from using the website, extensions or products.</p>
<h2>Purchases and refunds</h2><p>Paid products are sold through <a href="https://honesttools.gumroad.com">Gumroad</a>, and Gumroad's terms apply to the purchase. If you have a problem with a purchase or would like a refund, email us at <a href="mailto:{CONTACT}">{CONTACT}</a> and we will handle it in line with Gumroad's refund rules.</p>
<h2>Software licenses</h2><p>The source code of our extensions is published on <a href="https://github.com/honestheaders">GitHub</a> under the license included in each repository.</p>
<h2>YouTube API Services</h2><p>The parts of our service that use YouTube API Services (Honest Tools Uploader) are subject to the <a href="{YT_TERMS}">YouTube Terms of Service</a>. Our <a href="{BASE}/privacy/">Privacy Policy</a> explains how data is handled.</p>
<h2>Changes</h2><p>We may change these terms. The current version, with its date, is always on this page.</p>
<h2>Contact</h2><p>Email <a href="mailto:{CONTACT}">{CONTACT}</a>.</p></article>'''
