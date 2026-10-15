---
title: Header changes not working in Manifest V3? What changed and what still works
description: Chrome removed blocking webRequest for most extensions in Manifest V3. How header edits work now with declarativeNetRequest, and a short checklist for rules that do nothing.
updated: 2026-10-16
---

If a header rule worked in an older extension and does nothing in a newer one, the likely cause is not a bug in your rule. In Manifest V3, most Chrome extensions can no longer intercept a request and rewrite it in code. They hand Chrome a list of declarative rules instead, and Chrome applies them. Header edits still work this way, with a few differences in how rules are scoped, ordered and checked.

## What actually changed

In Manifest V2, an extension could register a blocking `webRequest` listener and change headers in its own code. Chrome's migration guide says blocking web requests "could significantly degrade both the performance of extensions and the performance of pages they work with", and that the permissions needed for it are invasive. Manifest V3 replaces the callbacks with declarative rules handled by the `declarativeNetRequest` API.

The `webRequestBlocking` permission is no longer available for most extensions. The documented exception is an extension installed by policy, where it is still available. The `webRequest` API itself remains for observing requests, limited to the hosts the extension has permission for.

## How a header edit is written now

A header change is a rule whose action type is `modifyHeaders`. The action has a `requestHeaders` list (and a `responseHeaders` list for responses), and each entry names a header and an operation. Chrome's own example removes the `cookie` header and limits the rule with a `resourceTypes` condition.

| Operation | What Chrome documents |
|---|---|
| `set` | Replaces any existing header with the same name. |
| `append` | Adds a new entry. Works only for an allowlist of headers, and the match is case sensitive. |
| `remove` | Deletes all entries for that header. |

The `append` limits get their own page: [why "append" fails on some request headers](/honest-guide/en/move-modheader-rules-append-not-supported/).

## Why a rule may do nothing

- **Priority.** `priority` defaults to 1, and the highest priority among matching rules wins. The documentation says browser vendors do not promise any order for same-priority rules, so set an explicit priority when order matters.
- **An earlier rule got there first.** If a rule removes a header, lower-priority rules cannot modify it further. If a rule sets a header, only lower-priority rules from the same extension can append to it.
- **The page itself is not covered.** When a rule uses `excludedResourceTypes` without `resourceTypes`, Chrome matches every type except `main_frame`. To change the headers of the page request itself, list `main_frame` under `resourceTypes`.
- **Wrong stage.** The documentation notes that request-header changes have no effect once a request has been sent.
- **Permissions.** The `declarativeNetRequest` permission shows an install-time warning. `declarativeNetRequestWithHostAccess` shows no warning, but you must request host permissions before it can act on a site. If your tool seems inactive on one site, check its site access first. Our guide to [reading extension permissions](/honest-guide/en/read-chrome-extension-permissions-before-install/) shows where.

## Check what was really sent

Open DevTools, go to the **Network** tab, click a request, and read **Request Headers**. That is what left the browser, whatever the extension's own screen says.

For developers who build the extension, `getMatchedRules()` needs the `declarativeNetRequestFeedback` permission or an `activeTab` grant, and `onRuleMatchedDebug` is available only to unpacked extensions with that permission. `testMatchOutcome()` is also limited to unpacked extensions.

{{product:headers}}

## Who this is not for

If you are a user of an existing extension and the rule is correct but the site still behaves oddly, the cause may be on the server or in a cache, which this page does not cover. If you need to change headers for traffic from scripts, servers or other apps, a browser extension cannot do that. And if your extension must be force-installed by an organization, ask its administrator which permissions apply, since policy-installed extensions are treated differently.

## Sources (checked 2026-10-16)

- Chrome for Developers, Replace blocking web request listeners (why blocking was replaced, `modifyHeaders` example, policy exception): <https://developer.chrome.com/docs/extensions/develop/migrate/blocking-web-requests>
- Chrome for Developers, `chrome.webRequest` (`webRequestBlocking` availability, observation limits): <https://developer.chrome.com/docs/extensions/reference/api/webRequest>
- Chrome for Developers, `chrome.declarativeNetRequest` (permissions, header operations, priority, resource types, debugging): <https://developer.chrome.com/docs/extensions/reference/api/declarativeNetRequest>
