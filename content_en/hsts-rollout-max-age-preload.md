---
title: HSTS rollout order: ramp up max-age in three stages before you preload
description: A safe order for rolling out Strict-Transport-Security: check every subdomain, ramp max-age from 5 minutes to 1 month, then decide on preload, which hstspreload.org says cannot easily be undone.
updated: 2026-10-21
---

Do not start with `max-age=31536000; includeSubDomains; preload`. The preload site hstspreload.org recommends ramping up `max-age` in three stages (5 minutes, 1 week, 1 month), checking subdomains first, and adding `preload` only at the end, because inclusion in the preload list "cannot easily be undone". This page follows that order.

## Why the order matters

The preload site describes HSTS as the way to have browsers "enforce that your page is loaded only over HTTPS". The risk is that the rule covers more than you may expect. The same page says HSTS preloading applies to all subdomains, "including internal subdomains that are not publicly accessible". A forgotten host that only serves plain `http://` is one way this can go wrong.

## Step 0: list every subdomain and test it over HTTPS

Before sending any header, examine all subdomains and nested subdomains and make sure they work properly over HTTPS. That includes internal ones. If a `www` DNS record exists, it needs to serve HTTPS too.

## Step 1: three stages, one header each

Add `Strict-Transport-Security` to all HTTPS responses and raise `max-age` in stages. The values below are the ones hstspreload.org gives:

| Stage | Wait | Header value |
|---|---|---|
| 1 | 5 minutes | `max-age=300; includeSubDomains` |
| 2 | 1 week | `max-age=604800; includeSubDomains` |
| 3 | 1 month | `max-age=2592000; includeSubDomains` |

```http
Strict-Transport-Security: max-age=300; includeSubDomains
```

During each stage, check for broken pages and watch your site metrics such as traffic and revenue. Fix problems, then "wait the full `max-age` of the stage before you move on", for example a month in the last stage. If you have employees or users who can beta test, the page suggests trying the first few stages on them, then going through all stages for everyone from the beginning.

You can try each header value in your own browser first, without a server change. See [How to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/). The other headers worth reviewing at the same time are in the [security headers checklist](/honest-guide/en/security-headers-checklist/).

## Step 2: decide on preload separately

Preloading is a different decision from sending HSTS. To be accepted, hstspreload.org lists these requirements:

- Serve a valid certificate.
- If the host listens on port 80, redirect HTTP to HTTPS on the same host.
- Serve all subdomains over HTTPS.
- Send an HSTS header on the base domain for HTTPS requests with `max-age` of at least `31536000` seconds (1 year), plus `includeSubDomains` and `preload`. Any redirect from the HTTPS site must also carry the header.

The site must keep meeting these requirements, and it says sites may be removed automatically if they stop doing so.

## What removal looks like

The preload page warns: "Don't request inclusion unless you're sure that you can support HTTPS for your entire site." To leave the list, the removal page says the site must be preloaded or pending preload, serve HTTPS with a valid certificate, and send a valid HSTS header that does not contain `preload`. It also says removal "may take 6-12 weeks to reach most Chrome users, and may take longer for other browsers". So treat the third stage as a long trial run, not a formality.

{{product:templates}}

## Who this is not for

If any subdomain must stay on plain HTTP, such as an old internal tool, `includeSubDomains` and preload do not fit until that is fixed. This page does not cover how to set the header in nginx, Vercel or Cloudflare, or the exact browser behavior defined in the HSTS specification, which I did not open for this article. It is also not a complete security review: HSTS is one header among several.

## Sources (checked 2026-10-21)

- HSTS Preload List Submission, deployment recommendations and requirements: <https://hstspreload.org/>
- HSTS Preload List, removal requirements: <https://hstspreload.org/removal/>
