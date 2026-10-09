---
title: Security headers checklist: the 7 to add and the 5 to remove
description: Check for HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy and COOP, and remove X-Powered-By, server versions, X-XSS-Protection, HPKP and Expect-CT.
updated: 2026-10-09
---

Short answer: look for **7 headers** (Strict-Transport-Security, Content-Security-Policy, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, Cross-Origin-Opener-Policy) and **remove 5** (X-Powered-By, a version number in `Server`, X-XSS-Protection, Public-Key-Pins, Expect-CT). Fix the "remove" list first: those are usually one-line changes.

Headers are one layer of protection. A full set does not make a site secure on its own.

## Step 1: see your current headers

Use any one of these:

- Command line: `curl -sI https://your-site.example` prints the response headers.
- Browser: open DevTools, **Network**, reload, click the first (document) request and read **Response Headers**.
- Online: Mozilla's HTTP Observatory tests a site's headers and gives recommendations.

Check the home page, one inner page, a 404 page and a redirect. Some servers only add headers to successful responses.

## Step 2: the 7 headers to look for

| Header | Look for | Why |
|---|---|---|
| Strict-Transport-Security | Present on HTTPS responses, e.g. `max-age=31536000; includeSubDomains` | Tells browsers to use HTTPS only. Ignored if sent over plain HTTP. |
| Content-Security-Policy | Present; at minimum `frame-ancestors`, `object-src 'none'`, `base-uri` | Limits where scripts load from and who can frame the page |
| X-Frame-Options | `DENY` or `SAMEORIGIN` | Blocks framing (clickjacking). OWASP prefers CSP `frame-ancestors` where possible. |
| X-Content-Type-Options | `nosniff` | Stops the browser from guessing file types |
| Referrer-Policy | Set explicitly, e.g. `strict-origin-when-cross-origin` | Controls how much of your URL is shared with other sites |
| Permissions-Policy | Unused features off, e.g. `geolocation=(), camera=(), microphone=()` | Stops the page and embeds from using features you never need |
| Cross-Origin-Opener-Policy | `same-origin` (or `same-origin-allow-popups` for sign-in or payment popups) | Separates your page from cross-origin windows |

OWASP's own example for HSTS is `max-age=63072000; includeSubDomains; preload`. Only add `preload` once every subdomain serves HTTPS.

## Step 3: the 5 to remove

| Header | What to do |
|---|---|
| X-Powered-By | Remove it. OWASP: "Remove all `X-Powered-By` headers." |
| Server with a version number | Remove the version (for example `server_tokens off;` in nginx) |
| X-XSS-Protection | OWASP: "Do not set this header or explicitly turn it off." Use CSP instead. |
| Public-Key-Pins | OWASP: "Do not use." |
| Expect-CT | OWASP: "Do not use it." |

## Test before you deploy

CSP, COOP and HSTS can break parts of a site if set without testing. Add them one at a time. You can try a new response header in your own browser first, without touching the server, using DevTools overrides or a header extension (see [How to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/)):

{{product:headers}}

A printable version of this checklist, and copy-paste settings for nginx, Apache, Cloudflare and Vercel:

{{product:checklist}}

{{product:templates}}

## Who this is not for

- This is a checklist, not a security audit or penetration test.
- If your site is behind a platform that controls headers for you (some site builders), you may not be able to change them; check the platform's documentation first.
- Do not copy a strict CSP into production without testing; it can block your own scripts.

## Sources

- OWASP HTTP Headers Cheat Sheet (checked 2026-10-09): <https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html>
- MDN, Strict-Transport-Security (checked 2026-10-08): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Strict-Transport-Security>
- MDN, X-Frame-Options (checked 2026-10-08): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options>
- MDN, Content Security Policy guide (checked 2026-10-08): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP>
- MDN, Cross-Origin-Opener-Policy (checked 2026-10-08): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy>
- Mozilla HTTP Observatory: <https://developer.mozilla.org/en-US/observatory>
- nginx, server_tokens: <https://nginx.org/en/docs/http/ngx_http_core_module.html#server_tokens>
