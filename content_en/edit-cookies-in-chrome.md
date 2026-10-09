---
title: How to view and edit cookies in Chrome (DevTools, or an extension)
description: Open DevTools, go to Application > Storage > Cookies, pick the site, and double-click a field to edit it. When an extension is the better choice, and what permissions it needs.
updated: 2026-10-09
---

Short answer: open DevTools, go to **Application > Storage > Cookies**, select the site, and **double-click any field to edit it**. You do not need to install anything. An extension only helps if you edit cookies often, or need to export and import them.

## Edit a cookie in DevTools (no install)

1. Open DevTools on the page (F12, or Ctrl+Shift+I / Cmd+Option+I).
2. Go to **Application > Storage > Cookies** and select an origin.
3. The table shows Name, Value, Domain, Path, Expires / Max-Age, Size, HttpOnly, Secure, SameSite, Partition Key and Priority.

| To do this | Do this in the Cookies pane |
|---|---|
| Edit a value or attribute | Double-click the field and type |
| Add a cookie | Double-click an empty row, enter a Name and Value, press Enter |
| Delete one cookie | Select it, then click **Delete selected** |
| Delete all cookies for the site | Click **Clear all** |
| Find a cookie | Type in **Filter** (matches Name or Value only, not case-sensitive) |
| Read an encoded value | Tick **Show URL-decoded** |

Size is calculated for you and cannot be edited. Cookies with invalid values are shown in red; **Only show cookies with an issue** lists just those.

## When an extension is the better tool

DevTools is enough for a one-off change. A cookie extension is handier when you:

- switch test accounts or sessions many times a day,
- need to export cookies as JSON or as a `cookies.txt` file (for command-line tools), and import them again,
- want to do it from a toolbar button without opening DevTools.

## Check the permissions before you install

An extension reads cookies through Chrome's `chrome.cookies` API. Chrome's documentation says the extension must declare the `cookies` permission **and host permissions** for the sites whose cookies it reads; without host permission for a URL, the call fails. That is why many cookie editors ask to "read and change all your data on all websites" when you install them.

Cookies often hold login sessions, so it is worth choosing an extension that asks for as little access as possible, is open source, and makes no network requests of its own.

We make one that works this way. It installs with no site access and asks for the current site only when you open it:

{{product:cookies}}

## Who this is not for

- If you only need to change a cookie once or twice, DevTools is enough. Do not install an extension you will not use again.
- If you want to manage cookies across a whole team or in automated tests, an extension is the wrong tool; set cookies in your test framework instead.
- Do not paste cookies from someone else's browser into yours unless you own the account. A session cookie works like a password.

## Sources (checked 2026-10-09)

- Chrome for Developers, "View, add, edit, and delete cookies": <https://developer.chrome.com/docs/devtools/application/cookies>
- Chrome for Developers, chrome.cookies API: <https://developer.chrome.com/docs/extensions/reference/api/cookies>
