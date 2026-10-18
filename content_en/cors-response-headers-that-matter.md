---
title: CORS errors in local development: the response headers that matter
description: A short map of the CORS response headers your server must send for simple requests, preflights and credentialed requests, with the browser error message each missing header produces.
updated: 2026-10-19
---

When a page on `http://localhost:3000` calls an API on another origin and the browser blocks it, the fix is almost always on the server: the response needs the right `Access-Control-*` headers. Which ones depends on three things: is the request "simple", does it need a preflight, and does it send credentials.

## Step 1: is it a simple request?

MDN's CORS guide says a simple request meets all of these conditions: the method is `GET`, `HEAD` or `POST`; only CORS-safelisted headers are set by hand (`Accept`, `Accept-Language`, `Content-Language`, `Content-Type` with extra requirements, and `Range`); and `Content-Type` is one of `application/x-www-form-urlencoded`, `multipart/form-data` or `text/plain`.

For a simple request the browser sends it straight away. The response only needs `Access-Control-Allow-Origin` set to your page's origin (or `*`). Without it, Firefox reports `Reason: CORS header 'Access-Control-Allow-Origin' missing`.

A common surprise: a `fetch()` that posts JSON with `Content-Type: application/json` is not simple, because that type is not on the list above. It gets a preflight.

## Step 2: answer the preflight

For a non-simple request, the browser first sends an `OPTIONS` request "in order to determine if the actual request is safe to send", as the guide puts it. MDN's glossary says that request carries `Access-Control-Request-Method`, `Origin`, and optionally `Access-Control-Request-Headers`.

Your server must answer that `OPTIONS` request itself. MDN's example response looks like this:

```http
HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://foo.example
Access-Control-Allow-Methods: POST, GET, OPTIONS
Access-Control-Allow-Headers: X-PINGOTHER, Content-Type
Access-Control-Max-Age: 86400
Vary: Accept-Encoding, Origin
```

| Header | What it does |
|---|---|
| `Access-Control-Allow-Origin` | Names the origin allowed to read the response. |
| `Access-Control-Allow-Methods` | Lists the methods the actual request may use. |
| `Access-Control-Allow-Headers` | Lists the request headers the actual request may carry. MDN says it is required if the preflight has `Access-Control-Request-Headers`. |
| `Access-Control-Max-Age` | How many seconds the preflight answer may be cached. MDN gives the default as 5 seconds and says each browser has its own maximum that takes precedence. |

The guide's examples use `204` for the preflight response, but it does not say that status is mandatory. It does say the actual request does not repeat the `Access-Control-Request-*` headers; they exist only on the `OPTIONS` request.

If your server returns an error for `OPTIONS` (a framework route that only allows `POST`, say), Firefox shows `Reason: CORS preflight channel did not succeed`. If the preflight works but a header you send is missing from `Access-Control-Allow-Headers`, you get `Reason: missing token 'xyz' in CORS header 'Access-Control-Allow-Headers' from CORS preflight channel`. MDN's CORS errors page lists both messages.

## Step 3: credentials change the rules

If the request carries cookies or HTTP authentication (`credentials: "include"` in `fetch`), MDN lists extra requirements:

- The response must include `Access-Control-Allow-Credentials: true`, or the browser rejects it.
- The preflight response must also carry `Access-Control-Allow-Credentials: true`, and the preflight itself never includes credentials.
- `Access-Control-Allow-Origin`, `-Allow-Headers`, `-Allow-Methods` and `-Expose-Headers` must not be the `*` wildcard; use explicit values.
- `Access-Control-Allow-Headers` documentation adds that `Authorization` does not accept the wildcard and must be listed explicitly.

The matching Firefox message is `Reason: Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*'`.

## If you echo the origin, add Vary

Servers often compare the request's `Origin` to an allowlist and reply with that single origin. MDN says that in this case the server "should also include `Origin` in the `Vary` response header", so caches know responses differ by origin:

```http
Access-Control-Allow-Origin: https://mozilla.org
Vary: Origin
```

## A quick way to check

Open DevTools, go to the Network tab, click the failing request and read the response headers. For a preflight, look for the `OPTIONS` row just above it. Compare what you see with the table above. The browser console message names the missing piece, but MDN notes that JavaScript cannot see the specific reason, so the console is where to look. For general header inspection in Chrome, see [how to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/); for the headers that protect your own pages, see the [security headers checklist](/honest-guide/en/security-headers-checklist/).

## Who this is not for

This page covers response headers only. If the request never reaches the server because of a network failure, or the page is blocked by something other than CORS (for example a Content-Security-Policy rule), these headers will not help.

## Sources (checked 2026-10-19)

- MDN, Cross-Origin Resource Sharing (CORS): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS>
- MDN, CORS errors (reason messages): <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CORS/Errors>
- MDN, Access-Control-Allow-Headers: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Access-Control-Allow-Headers>
- MDN Glossary, Preflight request: <https://developer.mozilla.org/en-US/docs/Glossary/Preflight_request>
