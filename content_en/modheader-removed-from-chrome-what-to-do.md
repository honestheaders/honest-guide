---
title: ModHeader was removed from the Chrome Web Store: what was reported, and how to check any header extension
description: Google removed ModHeader on 10 July 2026 after Stripe OLT found a dormant browsing-history collector. What the report says, what it does not say, and a 2-minute permission check.
updated: 2026-10-10
---

If you used ModHeader, here is the short version. On 10 July 2026 Google removed it from the Chrome Web Store after a security firm, Stripe OLT, reported a dormant browsing-history collector in version 7.0.18. The report says it did **not** observe browsing history being sent out. It does say the extension had far more access than editing headers needs. Remove it, move your rules, and check the permissions of whatever you install next.

## What was reported

Stripe OLT's write-up (linked in Sources) describes ModHeader version 7.0.18, extension ID `idgpnmonknjnojddfkpgkljpfnnfcklj`. In summary:

- The code could fingerprint the device and keep an encrypted list of visited domains, capped at 1,000, in the browser's local storage.
- A daily upload routine was present, but the report says it was gated off by an empty allow-list.
- The extension sent small messages on install, update and uninstall to a third-party domain (product name, version, browser type).
- The permissions included access to all sites, a content script on all sites, `webRequest` and `scripting`.
- Google removed the listing on 10 July 2026 after responsible disclosure.

## What was not reported

The report states that active browsing-history exfiltration was not observed in that build. It also notes that an update could have switched the upload on without asking for new permissions. That is the real lesson: an extension that already has broad access does not need your permission again to change what it does.

We could not confirm, as of 10 October 2026, whether ModHeader has been relisted. Check the store page before relying on any claim about its current state, including ours.

## Check any header extension in two minutes

Open `chrome://extensions`, click **Details** on the extension, and read "Site access" and the permissions list. For a tool that only edits headers, these are what matter:

| Permission | What it lets an extension do | Needed to edit headers? |
|---|---|---|
| `declarativeNetRequest` | Ask Chrome to change requests and responses by rules, without the extension seeing the content | Yes, this is the intended API |
| `storage` | Save your profiles in the browser | Yes |
| `webRequest` | Observe network requests as they happen | No. In Manifest V3 it can no longer modify requests for normal extensions |
| `scripting` / content scripts | Run code inside the pages you visit | No |
| Site access: all sites | Apply to every site | Chrome requires host access for header rules, so expect it. Look for ways to limit it with URL filters |

Chrome's own documentation says declarativeNetRequest lets an extension "modify network requests without intercepting them and viewing their content", and that webRequest can no longer block or modify requests in Manifest V3 except for policy-installed extensions. So a header editor that asks for `webRequest`, `scripting` or content scripts is doing something beyond editing headers. That does not prove bad intent. It does mean you should ask why.

Two more checks: is the source public, and does the privacy policy say the extension makes no network requests of its own?

## Move your rules

1. If ModHeader is still installed, export your profiles to JSON first. If you never exported, you will have to rebuild the rules by hand.
2. Install the replacement you picked and import the file. Honest Headers reads ModHeader JSON exports.
3. Open each profile and check what carried over. Some rules may be skipped or switched off.
4. Chrome only allows the `append` operation on a short list of request headers. For any other request header, use `set`. Response headers can be appended freely.
5. If a rule does not apply, check whether another extension is changing the same header.
6. If you ever typed an API key or token into a header value, consider replacing it as a precaution.

If you only need to change a header now and then, you may not need an extension at all. See [how to change HTTP headers in Chrome](/honest-guide/en/modify-http-headers-in-chrome/) for the built-in DevTools option.

{{product:headers}}

## What Honest Headers asks for

We make Honest Headers, so judge this against the table above. Version 1.1.x requests `declarativeNetRequest`, `storage` and `alarms` (only for the optional auto-off timer), plus access to all sites, which Chrome requires for header rules. It has no content scripts, no `webRequest`, no `scripting`, and the code makes no network requests of its own. The source is public under the MIT license, so you can check this rather than take our word for it.

## Who this is not for

If you have never used ModHeader, nothing here requires action. Teams that need shared rule workspaces or cloud sync need a different kind of tool than a single-user header editor. And if the DevTools overrides cover your case, you do not need to install anything.

## Sources (checked 2026-10-10)

- Stripe OLT, threat research on the ModHeader extension: <https://stripeolt.com/knowledge-hub/threat-research/chrome-extension-hidden-data-exfiltration-900k-users/>
- Chrome for Developers, `chrome.declarativeNetRequest`: <https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest>
- Chrome for Developers, `chrome.webRequest`: <https://developer.chrome.com/docs/extensions/reference/api/webRequest>
