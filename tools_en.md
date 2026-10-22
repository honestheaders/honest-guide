# Free tool ideas (English, /en/tools/)

Rules: self-check only (your own site or browser), runs in the visitor's browser, sends nothing out, no crawling of other people's sites, nothing usable for attacks. Check every rule in the official source before building and list it with the date on the tool page. Build **one per run**, top to bottom. After building, add it to `TOOLS`/`BODIES` (src/en_tools.py), `TOOL_FOR` and `TOOL_PRODUCTS` (src/en.py), then set Status to published.

| No | Tool | Problem it helps with | Sources to check | Links to | Status |
|---|---|---|---|---|---|
| T1 | PHP version checker + own-site bookmark | PHP CVE-2026-109618/109619 (Oct 2026) | php.net advisory, GHSAs | E28 | published |
| T2 | Security headers checker: own-site bookmark + nginx/Apache/PHP fixes | Missing or leaky headers | nginx, Apache mod_headers, PHP manual | E4, E17 | published |
| T3 | Mixed content finder (bookmark): lists `http://` images, scripts, iframes on the HTTPS page you are on | Padlock warnings, blocked scripts after moving to HTTPS | MDN Mixed content, web.dev | E8 | todo |
| T4 | CSP builder: pick sources, get a Report-Only header first, then the enforcing one | CSP breaks sites when added blind | MDN CSP, CSP Level 3 | E7, templates | todo |
| T5 | Subresource Integrity (SRI) hash generator: paste a file's text, get `integrity="sha384-..."` | CDN scripts changed without notice | MDN SRI, W3C SRI | E4 | todo |
| T6 | Certificate expiry reminder: paste a PEM certificate, see expiry and SANs, add an .ics reminder 14 days before | Sites going down on a forgotten renewal | RFC 5280, MDN (Web Crypto not needed) | E8 | todo |
| T7 | security.txt generator (RFC 9116): contact, expires, policy | Researchers cannot find who to tell | RFC 9116 | E4 | todo |
| T8 | HSTS preload readiness: paste the header, see what hstspreload.org requires | Preload rejected, or added too early | hstspreload.org, MDN HSTS | E8 | todo |
| T9 | Set-Cookie audit: paste several Set-Cookie lines, flag missing Secure/HttpOnly/SameSite and bad prefixes | Session cookies without flags | MDN Set-Cookie, OWASP Session Mgmt | E10, cookies | todo |
| T10 | CORS response checker: paste the preflight + response headers, see why the browser blocks it | "blocked by CORS policy" errors | MDN CORS, Fetch standard | E6, headers | todo |
| T11 | robots.txt tester: paste robots.txt and a path, see allow/deny per Google's rules | Scraping politely, blocking pages by mistake | Google Search Central robots.txt spec, RFC 9309 | E27, scraper | todo |
| T12 | Permissions-Policy builder | Turning off camera/mic/geolocation you never use | MDN Permissions-Policy | E14, templates | todo |
