---
title: Cookie editor export to cookies.txt: the 7 fields curl expects
description: If your cookie editor gave you a JSON list, curl still wants a tab-separated file with seven fields. How each Chrome cookie property maps to them, with a small script.
updated: 2026-10-14
---

curl reads cookies from a plain text file with one cookie per line and seven fields separated by TAB characters. Most cookie editors for Chrome export JSON instead, using the property names from Chrome's `chrome.cookies` API. This page shows how the two line up, so you can carry cookies from a retired or replaced editor into `curl -b cookies.txt`.

We have not found an official statement about any particular editor's export format, so nothing here assumes one. The mapping below starts from Chrome's own cookie properties, which many editors reuse. Open your export and check that the field names match before you run anything.

## What curl expects

The curl documentation describes the file like this: it is text based, one cookie per line, and lines starting with `#` are comments. The exception is a line starting with `#HttpOnly_`, which is the prefix for a cookie that has the `HttpOnly` attribute. Each cookie line has seven fields separated by TABs, and a valid line must end with a newline.

| Position | Field | Example from curl's docs |
|---|---|---|
| 0 | Domain name | `example.com` |
| 1 | Include subdomains (TRUE/FALSE) | `FALSE` |
| 2 | Path | `/foobar/` |
| 3 | HTTPS only (TRUE/FALSE) | `TRUE` |
| 4 | Expiry, seconds since Jan 1st 1970, or 0 | `0` |
| 5 | Cookie name | `person` |
| 6 | Cookie value | `daniel` |

curl's `--cookie` option takes a file name when the argument has no `=` in it, and says the file should be in the Netscape/Mozilla format. It discourages the HTTP-header style. `--cookie-jar` writes the same Netscape format.

## What Chrome's cookie properties look like

Chrome's `chrome.cookies` documentation lists these properties on a cookie: `domain`, `name`, `value`, `path`, `hostOnly`, `httpOnly`, `secure`, `session`, `expirationDate`, `sameSite` and `storeId`, plus `partitionKey` in Chrome 119 and later. `expirationDate` is in seconds since the UNIX epoch and is not provided for session cookies. `hostOnly` is `true` if a request's host must exactly match the cookie's domain.

## The mapping we use

| curl field | From the JSON | Note |
|---|---|---|
| Domain | `domain` | Written as it appears in the export |
| Include subdomains | `NOT hostOnly` | Our reading: a host-only cookie does not apply to subdomains |
| Path | `path` | |
| HTTPS only | `secure` | |
| Expiry | `expirationDate`, or `0` | Session cookies have no `expirationDate` |
| Name, value | `name`, `value` | |
| `#HttpOnly_` prefix | `httpOnly` is `true` | Put the prefix at the start of the line |

Two points are not covered by the curl page we checked: whether a leading dot on the domain matters, and what an expiry of `0` means beyond the wording "or 0". Treat our handling of both as a starting point and test against a server you control.

## A small converter

This Python script reads a JSON list of cookies with the properties above and writes a curl-style file. It uses only the standard library.

```python
import json, sys

cookies = json.load(open(sys.argv[1]))
out = ["# Netscape HTTP Cookie File"]
for c in cookies:
    domain = c["domain"]
    if c.get("httpOnly"):
        domain = "#HttpOnly_" + domain
    sub = "FALSE" if c.get("hostOnly") else "TRUE"
    secure = "TRUE" if c.get("secure") else "FALSE"
    expiry = str(int(c["expirationDate"])) if "expirationDate" in c else "0"
    out.append("\t".join([domain, sub, c["path"], secure, expiry, c["name"], c["value"]]))
open(sys.argv[2], "w", newline="\n").write("\n".join(out) + "\n")
```

Run it as `python3 convert.py cookies.json cookies.txt`, then try `curl -v -b cookies.txt https://your-test-site.example/`. With `-v`, curl prints the request it sends, so you can see whether the `Cookie:` header is there.

If the export does not have these property names, rename them in the script rather than guessing.

## Keep the file private

The file holds live session values. Anyone who has a logged-in session cookie can usually act as you on that site until it expires or is revoked. Store the file outside any Git repository, do not paste it into a bug report, and delete it when the test is done.

For viewing and editing a cookie in the browser first, see [how to view and edit cookies in Chrome](/honest-guide/en/edit-cookies-in-chrome/). To understand why a cookie is or is not sent, read [the SameSite attribute explained](/honest-guide/en/samesite-cookie-attribute/).

{{product:cookies}}

## Who this is not for

If you only need to look at one cookie, Chrome DevTools can show it without any export. If you need cookies for a site you do not own or have no permission to test, do not export them; follow that site's terms. And if your goal is to automate a login, a cookie file is a fragile way to do it, because session cookies expire. Use an API token meant for scripts where the service offers one.

## Sources (checked 2026-10-14)

- curl, HTTP cookies (file structure and the seven fields): <https://curl.se/docs/http-cookies.html>
- curl, command line manual (`--cookie`, `--cookie-jar`): <https://curl.se/docs/manpage.html>
- curl, CURLOPT_COOKIEFILE (Netscape or Set-Cookie style data): <https://curl.se/libcurl/c/CURLOPT_COOKIEFILE.html>
- Chrome for Developers, `chrome.cookies` (cookie properties): <https://developer.chrome.com/docs/extensions/reference/api/cookies>
