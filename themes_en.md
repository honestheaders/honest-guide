# English topics (content_en/)

Status: todo / on hold (reason) / published. Work **top to bottom**. Topics are things developers search for that our tools or PDFs actually help with. Every fact must be checked in the official source yourself.

| No | Topic | Official sources to check | Product card | Status |
|---|---|---|---|---|
| E1 | How to view and edit cookies in Chrome | Chrome DevTools docs, chrome.cookies API | cookies | published |
| E2 | SameSite cookies: Strict, Lax, None | MDN Set-Cookie, web.dev | cookies | published |
| E3 | How to change HTTP headers in Chrome | Chrome DevTools overrides, declarativeNetRequest | headers | published |
| E4 | Security headers checklist (7 to add, 5 to remove) | OWASP, MDN | headers, checklist, templates | published |
| E21 | ModHeader was removed from the Chrome Web Store: what was reported, and how to check any header extension | Stripe OLT report, Chrome for Developers (declarativeNetRequest, webRequest) | headers | published |
| E22 | How to read a Chrome extension's permissions before you install it (site access, "on click" vs "all sites") | Chrome for Developers (permissions list, declare permissions), Chrome Help (extension site access) | headers, cookies | todo |
| E23 | Move your ModHeader rules to another tool: what a JSON export holds, and why `append` fails on some request headers | Chrome for Developers (declarativeNetRequest modifyHeaders append allowlist), MDN (HTTP headers) | headers | todo |
| E24 | EditThisCookie is gone: move your cookies to another tool (JSON, cookies.txt). Only write the "what happened" part if a primary source is found; otherwise write only the export/import steps | Chrome Help, curl docs (cookie file format), Chrome for Developers (chrome.cookies) | cookies | todo |
| E25 | Header changes that stopped working in Manifest V3: why, and what still works | Chrome for Developers (Manifest V3 migration, declarativeNetRequest) | headers | todo |
| E5 | Export Chrome cookies to cookies.txt (Netscape format) for curl / wget | curl docs (cookie file format), wget manual | cookies | todo |
| E6 | Test CORS locally: which response headers matter | MDN CORS guide, Fetch standard | headers | todo |
| E7 | Content-Security-Policy: start with Report-Only | MDN CSP, CSP Level 3 spec | headers, templates | todo |
| E8 | HSTS max-age and preload: a safe rollout order | MDN HSTS, hstspreload.org | templates | todo |
| E9 | Partitioned cookies (CHIPS) explained | MDN, Chrome for Developers (privacy sandbox docs) | cookies | todo |
| E10 | HttpOnly and Secure cookies: what they do and don't stop | MDN Set-Cookie, OWASP Session Management Cheat Sheet | cookies | todo |
| E11 | Cookie size and count limits | RFC 6265 / 6265bis, MDN | cookies | todo |
| E12 | Add an Authorization header to every request in Chrome (for API testing) | MDN Authorization, declarativeNetRequest | headers | todo |
| E13 | Referrer-Policy values compared | MDN Referrer-Policy, W3C Referrer Policy | checklist | todo |
| E14 | Permissions-Policy: turn off camera, mic, geolocation | MDN Permissions-Policy | templates | todo |
| E15 | X-Frame-Options vs CSP frame-ancestors | MDN, OWASP Clickjacking Cheat Sheet | checklist | todo |
| E16 | Cross-Origin-Opener-Policy and sign-in popups | MDN COOP | templates | todo |
| E17 | Security headers on nginx: add_header inheritance | nginx official docs | templates | todo |
| E18 | Security headers on Vercel (vercel.json headers) | Vercel docs | templates | todo |
| E19 | Security headers on Cloudflare (Transform Rules) | Cloudflare docs | templates | todo |
| E20 | Delete cookies for one site only in Chrome | Chrome Help, DevTools docs | cookies | todo |
