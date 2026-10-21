---
title: Partitioned cookies (CHIPS): one cookie jar per top-level site
description: What the Partitioned attribute does, which attributes it needs, how the partition key is chosen, and how to see partitioned cookies in Chrome DevTools. Based on MDN and Chrome's CHIPS docs.
updated: 2026-10-22
---

A partitioned cookie is a third-party cookie that the browser stores separately for each top-level site. Add `Partitioned` (together with `Secure`) to `Set-Cookie`, and an embedded widget on `site-a.example` can no longer read the cookie it set while embedded on `site-b.example`. This page explains the attribute, the partition key, the limits, and where to look in DevTools.

## What changes when you add Partitioned

CHIPS stands for Cookies Having Independent Partitioned State. MDN describes it as a way to "opt a cookie into partitioned storage, with a separate cookie jar per top-level site". Such a cookie is double-keyed: by the origin that sets it and by the origin of the top-level page. It can only be read within the top-level site it was set on.

A typical use is an embedded chat or payment widget that needs to remember state inside one site, but has no need to follow the visitor across sites.

## The header

MDN's example looks like this:

```http
Set-Cookie: __Host-example=34d8g; SameSite=None; Secure; Path=/; Partitioned;
```

What the two sources say about each part:

- **`Secure`** is required. MDN: "Partitioned cookies must be set with `Secure`."
- **`Path`** is not stated as required. The examples use `Path=/`.
- **`__Host-` prefix** is optional. MDN recommends it if you do not need to share the cookie between subdomains, because it binds the cookie to the current host.
- **`SameSite=None`** appears in the example because the cookie is meant for third-party contexts. For what the three SameSite values do, see [SameSite cookies: Strict, Lax and None](/honest-guide/en/samesite-cookie-attribute/).

## How the partition key is chosen

With `Partitioned` set, the cookie is stored with the host key plus a partition key. MDN says the partition key is based on the site, including the scheme, of the top-level URL the browser was visiting when the request that set the cookie was made.

Example: `https://3rd-party.example` is embedded in `https://site-a.example` and sets a partitioned cookie. If the same embed is later loaded under `https://site-b.example`, the keys do not match, so the cookie is not sent there.

Inside one top-level site, the cookie stays available. MDN's chat example shows the same cookie being matched on `support.shoppy.example` and `checkout.shoppy.example` when the top-level site is `shoppy.example`.

## Limits and support

Chrome's CHIPS page gives a limit of "maximum 180 cookies per partition that cannot exceed 10 KB per-embedded-site". MDN's page does not state a size limit.

On support, Chrome's page says CHIPS has been supported by default since Chrome 114, after an origin trial from Chrome 100 to 116. MDN labels the feature "Baseline 2025 – Newly available", meaning it works in the latest browser versions and may not work in older ones. Test in the browsers your users have.

## See them in DevTools

Following the Chrome page: open DevTools, go to **Application**, then **Storage**, then **Cookies**, and select the embedded site's origin. Partitioned cookies show the partition key of the top-level site. To read or change what a cookie holds, see [How to view and edit cookies in Chrome](/honest-guide/en/edit-cookies-in-chrome/).

## Who this is not for

If your cookie is first-party only (your own site, not embedded elsewhere), you do not need `Partitioned`. If your embed must recognize the same user across different top-level sites, a partitioned cookie is designed to prevent exactly that, so it will not fit. This page does not cover the IETF draft text or how other browsers partition cookies by default, which I did not open for this article.

## Sources (checked 2026-10-22)

- MDN, Cookies Having Independent Partitioned State (CHIPS): <https://developer.mozilla.org/docs/Web/Privacy/Privacy_sandbox/Partitioned_cookies>
- Privacy Sandbox, Cookies Having Independent Partitioned State (CHIPS): <https://privacysandbox.google.com/cookies/chips>
