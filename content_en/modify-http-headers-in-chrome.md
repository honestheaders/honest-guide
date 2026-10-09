---
title: How to change HTTP headers in Chrome (response headers in DevTools, request headers with an extension)
description: DevTools can override response headers locally (Network > right-click > Override headers). To add or change request headers, you need an extension that uses declarativeNetRequest.
updated: 2026-10-09
---

Short answer: to change **response** headers, use DevTools: in the **Network** panel, right-click a request and choose **Override headers**, then reload. To add, change or remove **request** headers (for example `Authorization` or a custom `X-` header), use an extension. Chrome's DevTools guide only covers response headers.

## Which tool for which job

| You want to | Use |
|---|---|
| Test a new response header (CSP, CORS, cache) without touching the server | DevTools local overrides |
| Send a custom request header on every request to a site | An extension |
| Remove a header the server sends | DevTools overrides, or an extension |
| Switch between sets of headers quickly | An extension with profiles |

## Override response headers in DevTools

1. Open DevTools and the **Network** panel. Reload the page.
2. Right-click the request and choose **Override headers**. DevTools opens the **Headers > Response Headers** editor.
3. The first time, DevTools asks you to **select a folder** to store override files in. Click **Allow** to give it access.
4. Edit a value, or add a new header.
5. Reload the page to apply it.

The rules are saved in a `.headers` file under **Sources > Overrides**. Two things to know: local overrides **disable the cache** while they are on, and they only apply while DevTools is open.

## Change request headers with an extension

Extensions change headers through Chrome's `declarativeNetRequest` API. Its `modifyHeaders` action can work on request and response headers with three operations:

- **set**: "Sets a new value for the specified header, removing any existing headers with the same name."
- **remove**: "Removes all entries for the specified header."
- **append**: "Adds a new entry for the specified header" (for request headers, only an allowlist of headers can be appended).

Because the browser applies the rules itself, a well-built header extension does not need to read your pages. Look for one that does not collect data and lets you limit it to the sites you test.

We make one that only uses these built-in rules, has profiles and URL filters, and can import ModHeader exports:

{{product:headers}}

## Who this is not for

- If you only need to test one response header once, DevTools overrides are enough.
- If you need headers changed for every user, change the server, CDN or proxy configuration. Browser tools only change what your own browser sends and sees.
- Changing headers in your browser does not bypass server-side security. Use it for testing your own sites.

## Sources (checked 2026-10-09)

- Chrome for Developers, "Override web content and HTTP response headers locally": <https://developer.chrome.com/docs/devtools/overrides>
- Chrome for Developers, chrome.declarativeNetRequest: <https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest>
