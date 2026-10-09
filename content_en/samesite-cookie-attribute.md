---
title: SameSite cookies explained: Strict, Lax and None (and why None needs Secure)
description: Strict sends a cookie only on same-site requests, Lax also on some top-level navigations, None on every request but only with Secure. What Chrome does when SameSite is missing.
updated: 2026-10-09
---

Short answer: **Strict** sends the cookie only on requests from the same site. **Lax** also sends it on some cross-site requests (top-level navigations with a safe method such as GET). **None** sends it on every request, but **only if the cookie is also `Secure`**. If you leave SameSite out, Chrome treats the cookie as `Lax`.

## The three values

| Value | Sent on same-site requests | Sent on cross-site requests | Typical use |
|---|---|---|---|
| `Strict` | Yes | No | Cookies that should never follow a link from another site |
| `Lax` | Yes | Only for top-level navigations with a safe method (for example clicking a link) | Most login and session cookies |
| `None` | Yes | Yes, but the cookie must also have `Secure` | Cookies used inside iframes or by embedded widgets on other sites |

MDN on `None`: "The `Secure` attribute must also be set when using this value."

## What happens when SameSite is missing

MDN says "Some browsers use `Lax` as the default value if `SameSite` is not specified." For Chrome, web.dev says "Cookies without a `SameSite` attribute are treated as `SameSite=Lax`", a change listed for Chrome 80. So do not rely on the default: set the value you mean.

## A working example

```
Set-Cookie: session=abc123; Path=/; Secure; HttpOnly; SameSite=Lax
Set-Cookie: widget_id=xyz; Path=/; Secure; SameSite=None; Partitioned
```

## Related attributes that often go together

- **HttpOnly**: JavaScript cannot read the cookie through `document.cookie`. It is still sent with `fetch()` and `XMLHttpRequest` requests.
- **Partitioned**: the cookie is stored separately for each top-level site (CHIPS). `Secure` is required.
- **Max-Age and Expires**: if both are set, `Max-Age` wins.
- **Name prefixes**: a cookie named `__Secure-...` must be set with `Secure` from an HTTPS page. A cookie named `__Host-...` also must have no `Domain` and `Path=/`.

## How to check what a site actually sets

Open DevTools, go to **Application > Storage > Cookies**, and look at the SameSite, Secure and Partition Key columns. Our guide [How to view and edit cookies in Chrome](/honest-guide/en/edit-cookies-in-chrome/) shows the steps. If you change these attributes often while testing, a cookie editor saves time:

{{product:cookies}}

## Who this is not for

- This page explains what the attribute does. It is not a full guide to CSRF protection; SameSite is one layer, not a replacement for CSRF tokens where you need them.
- Browser behavior changes. If you depend on a default, check your target browsers' current documentation.

## Sources (checked 2026-10-09)

- MDN, Set-Cookie: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie>
- web.dev, "SameSite cookies explained": <https://web.dev/articles/samesite-cookies-explained>
