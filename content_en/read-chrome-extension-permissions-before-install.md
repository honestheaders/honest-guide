---
title: Chrome extension permissions: what "site access" means and how to limit it
description: How to read a Chrome extension's permissions before installing: host permissions, activeTab, optional permissions, and the three site-access settings you can change yourself.
updated: 2026-10-10
---

An extension that can "read and change all your data on all websites" can do that on every page you open, until you change the setting. Chrome lets you narrow it yourself: open the extension's Details page and pick **On select**, **On specific sites** or **On all sites**. Below is how to read the permission list, which parts to question, and how to limit access after you have installed.

## Two kinds of permissions, and why the difference matters

Chrome's developer documentation says extensions declare their intent in the manifest's permission fields, and it separates them like this:

- `permissions` are for extension APIs. Some of them show a warning at install time, and some show none.
- `host_permissions` let an extension interact with URLs that match the given patterns. A pattern for all sites means every page you visit.
- `optional_permissions` and `optional_host_permissions` are "granted by the user at runtime, instead of at install time". The documentation recommends optional permissions wherever the extension's features allow it.

So when you read a listing, the question is not only "what does it ask for?" but also "does it ask up front, or only when I use a feature?" An extension built around optional permissions starts with less access.

## What activeTab means

`activeTab` is a narrower alternative to all-sites access. Chrome's documentation says it "gives an extension temporary access to the currently active tab when the user invokes the extension". Invoking means one of these actions:

- clicking the extension's toolbar button,
- running one of its context menu items,
- using a keyboard shortcut it defines, or
- accepting one of its omnibox suggestions.

The access is revoked when you navigate away or close the tab. The documentation says it is not granted for restricted pages, and moving to another path on the same site keeps the access. If an extension's job is "do something to the page I am looking at, when I ask", `activeTab` is the shape of permission that matches that job.

## Quick reference

| What you see | What it means | What to ask |
|---|---|---|
| Access to all sites at install | The extension can act on every page you open | Does its job really need every site? |
| `activeTab` | Temporary access to the current tab after you invoke it | Nothing special. This is the narrow option |
| Optional permissions | The extension asks later, when you use a feature | Do I want to grant this when asked? |
| A new warning after an update | Chrome turns the extension off until you accept | Why does it need this now? |

On that last row: Chrome's permission-warning page says that when a new permission triggers a warning, "the extension will be disabled until the user accepts the new permission". That protects you from permissions that are added later. It does not protect you from code that changes what it does with access you already granted. For that case, the useful control is a narrower site-access setting.

## Limit site access in four steps

These are the steps from Chrome's help page. Chrome calls the first option **On select**.

1. Open Chrome, choose **More**, then **Extensions**, then **Manage extensions**.
2. On the extension, select **Details**.
3. Next to "Allow this extension to read and change all your data on websites you visit", choose **On select**, **On specific sites** or **On all sites**.
4. For specific sites, go to **Permissions**, then **Allowed sites**, and select **Add**. If you do not see Add, set the option to **On specific sites** first.

You can also click the Extensions icon next to the address bar, open **More**, and use **This can read and change site data** to choose between running when you select the extension, on the current site, or on all sites.

An extension set to run on select, or on a short list of sites, has less to work with than one set to all sites. Some extensions need all-sites access for their feature, such as a tool that edits request headers on any page you test. In that case the setting is a trade-off you make on purpose. You can still narrow it to the sites you work on.

## A short checklist before you click Add to Chrome

1. Read the permissions on the store page. Is anything there that the extension's one-line description does not explain?
2. Check whether it asks for all-sites access at install, or uses `activeTab` or optional permissions.
3. After installing, open Details and move site access to **On select** or **On specific sites** if the feature still works.
4. Remove extensions you stopped using. An unused extension with broad access still has that access.

If you want to see how this applies to a tool that edits headers, read [what was reported about ModHeader and how to check a header extension](/honest-guide/en/modheader-removed-from-chrome-what-to-do/). For cookie tools, the same question applies: see [how to view and edit cookies in Chrome](/honest-guide/en/edit-cookies-in-chrome/).

{{product:cookies}}

## Who this is not for

If you only install extensions from your employer's managed list, your administrator may already control site access, and the options above may be locked. If you need an extension that works on every site by design, this guide does not tell you to avoid it. It shows where the setting is. And a permission list cannot tell you whether the publisher is trustworthy. It tells you what the extension is able to do, not what it will do.

## Sources

Checked on 2026-10-10.

- [Declare permissions (Chrome for Developers)](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)
- [The activeTab permission (Chrome for Developers)](https://developer.chrome.com/docs/extensions/develop/concepts/activeTab)
- [Permission warning guidelines (Chrome for Developers)](https://developer.chrome.com/docs/extensions/permission_warnings)
- [Install and manage extensions (Chrome Help)](https://support.google.com/chrome_webstore/answer/2664769)
