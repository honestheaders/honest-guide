---
title: Content-Security-Policy Report-Only: the safe way to send your first CSP
description: How to send a CSP as Content-Security-Policy-Report-Only so violations are reported without blocking anything, why report-to is required, and what to fix before you switch to enforcing.
updated: 2026-10-20
---

Send your first policy as `Content-Security-Policy-Report-Only`, not `Content-Security-Policy`. MDN says this header "helps to monitor Content Security Policy (CSP) violations and their effects without enforcing the security policies", so you can find what would break before anything does. Two details catch people out: it needs a `report-to` directive to do anything useful, and it cannot be set in a `<meta>` tag.

## What a CSP does to a normal page

MDN's CSP guide says that once a policy contains `default-src` or `script-src`, inline JavaScript will not run unless you take extra steps. That covers `<script>` blocks, inline event handlers such as `onclick`, and `javascript:` URLs. The same rule blocks `eval()`, the `Function()` constructor, and string arguments to `setTimeout()` and `setInterval()`.

So a policy as short as `default-src 'self'` can stop a page that works today. That is the reason to watch first and enforce later.

## Step 1: define a place for reports

MDN's example sets up an endpoint with the `Reporting-Endpoints` header, then points the policy at it:

```http
Reporting-Endpoints: csp-endpoint="https://example.com/csp-reports"
Content-Security-Policy-Report-Only: default-src https:;
  report-uri /csp-report-url/;
  report-to csp-endpoint;
```

MDN states: "The CSP `report-to` directive must be specified for reports to be sent: if not, the operation won't have any effect." The example also lists the older `report-uri`, which MDN calls deprecated, because `report-to` "does not yet have full cross-browser support". The guide advises declaring both until `report-to` is supported everywhere.

Reports can also be seen inside the page with a `ReportingObserver`, according to the same page. That is handy when you do not have a collector yet.

## Step 2: run both headers side by side

You do not have to remove your old policy to test a new one. MDN's guide says that if both headers are in the same response, both are honored: the `Content-Security-Policy` policy is enforced, while the report-only policy "generates reports but is not enforced". A report-only header can also be used to test a future revision of a policy without deploying it.

| Situation | Header to send |
|---|---|
| No CSP yet | `Content-Security-Policy-Report-Only` only |
| Report-only has been quiet and you are ready | Move the same value to `Content-Security-Policy` |
| Enforcing a policy, want to try a stricter one | Keep `Content-Security-Policy`, add a new `Content-Security-Policy-Report-Only` |

## Step 3: read the reports and fix the causes

Most reports will point to the same few things. MDN's guide describes the fixes:

- **Inline scripts:** MDN says to avoid `'unsafe-inline'` because it "defeats much of the purpose of having a CSP". The recommended approach for scripts and styles is a nonce. MDN says the nonce must be different for every HTTP response and must not be predictable, which means the server cannot serve static HTML, because it has to insert a new nonce each time.
- **Static pages:** use a hash instead. MDN describes hashing the script contents with SHA-256, SHA-384 or SHA-512, Base64-encoding the result, and prefixing it with `sha256-`, `sha384-` or `sha512-`. Both the policy and the page can stay static, and external scripts also need the `integrity` attribute.
- **`eval()`:** MDN says developers should avoid `unsafe-eval`, so the usual fix is to remove the `eval()` call from your own code.

MDN calls the nonce- or hash-based approach a strict CSP, and its example looks like this:

```http
Content-Security-Policy:
  script-src 'nonce-{RANDOM}';
  object-src 'none';
  base-uri 'none';
```

Once reports stop showing violations you did not expect, move the policy to `Content-Security-Policy`. If you manage nginx, Apache, Cloudflare or Vercel, check where your host sets headers first; our [security headers checklist](/honest-guide/en/security-headers-checklist/) lists the other headers to review at the same time.

## Trying the header in your own browser

Because the header is a plain response header, you can add it to responses from your own site in your browser and watch what happens before any server change. See [how to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/) for the options. Remember that MDN says the header is not supported inside a `<meta>` element, so a `<meta http-equiv>` test will not work.

{{product:headers}}

{{product:templates}}

## Who this is not for

This page is about report-only testing, not about writing a complete allow-list for a site with many third-party scripts. Reports from your own traffic are what show which sources your pages actually load. It also does not cover `frame-ancestors` or `X-Frame-Options`, which are a separate topic. MDN says the `sandbox` directive is ignored in a report-only header, so you cannot preview sandbox behavior this way.

## Sources (checked 2026-10-20)

- MDN, Content-Security-Policy-Report-Only header: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy-Report-Only>
- MDN, Content Security Policy (CSP) guide: <https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP>
