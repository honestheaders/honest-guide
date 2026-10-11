---
title: Moving header rules to a new tool: why "append" fails on some request headers in Chrome
description: Chrome only allows the append operation on 21 listed request headers. Which ones, what to use instead, and three other things to check after you move your rules.
updated: 2026-10-12
---

A rule that appends a value to `Authorization` or `X-Api-Key` will not work in a Chrome extension built on declarativeNetRequest, because `append` is only supported for a short list of request headers. The fix is usually to switch that rule to `set`. The rest of this page covers the list, and what else tends to differ when you move rules from one header tool to another.

## The 21 request headers that accept `append`

Chrome's declarativeNetRequest documentation says that for request headers, `append` is supported only for the headers below, and that the list is case sensitive:

| Group | Headers |
|---|---|
| Content negotiation | `accept`, `accept-encoding`, `accept-language`, `content-language` |
| Caching and conditions | `cache-control`, `if-match`, `if-none-match`, `range`, `want-digest` |
| Connection and proxies | `connection`, `keep-alive`, `te`, `trailer`, `transfer-encoding`, `upgrade`, `via`, `forwarded`, `x-forwarded-for` |
| Other | `access-control-request-headers`, `cookie`, `user-agent` |

That grouping is ours; the list itself is Chrome's. Headers that people often try to append and that are **not** on it include `authorization`, `referer`, `origin`, `content-type` and custom `x-` headers other than `x-forwarded-for`.

Because the list is case sensitive, write the names in lowercase when you write rules by hand.

## What to do with a rule that fails

The documentation describes the three operations like this: `append` adds a new entry for the header, `set` replaces any existing entries with the new value, and `remove` deletes all entries. For a header that is not on the list:

1. Change the operation from `append` to `set`.
2. If the old rule was combining your value with one the page already sends, write the combined value yourself.
3. Reload the page, open DevTools, go to the **Network** tab, click a request and check **Request Headers**. That shows what the browser actually sent.

The same documentation says that when you append to a request or response header, the browser uses the appropriate separator where possible. For response headers it does not state the same restriction on which names are allowed.

## Three other things to check after the move

- **Page loads.** If a rule does not name any resource types, Chrome applies it to every type except `main_frame`. A rule that changed the headers of the page itself in your old tool may need `main_frame` listed explicitly.
- **Scope.** Rules can be limited with `requestDomains` or a `urlFilter`. If `urlFilter` is left out, all URLs match. A rule you meant for one test server can end up touching every site.
- **Value required.** For `append` and `set`, the documentation says a value must be given.

Chrome also caps how many dynamic rules one extension can add: 30,000, with a separate limit of 5,000 for "unsafe" dynamic rules. Most personal profiles stay far below this.

If you only want to try a header change once, DevTools can do it without an extension. See [how to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/). To check what a tool asks for before you install it, see [reading a Chrome extension's permissions](/honest-guide/en/read-chrome-extension-permissions-before-install/).

{{product:headers}}

## Who this is not for

If your rules only touch headers on the list, such as `accept-language` or `user-agent`, `append` already works and you can skip this page. If you need to change the headers of requests made outside the browser, such as from a script or a server, a browser extension is the wrong tool. And if you need to attach a secret to every request, an extension is a risky place to keep it; use a throwaway test credential.

## Sources (checked 2026-10-12)

- Chrome for Developers, `chrome.declarativeNetRequest` (append allowlist, header operations, resource types, rule limits): <https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest>
- Chrome for Developers, Replace blocking web request listeners (the `modifyHeaders` rule action in Manifest V3): <https://developer.chrome.com/docs/extensions/develop/migrate/blocking-web-requests>
