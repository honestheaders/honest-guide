---
title: PHP 8.5.12, 8.4.27, 8.3.36 and 8.2.35: check which PHP version your site runs
description: php.net released fixes for two critical PHP bugs on 21 October 2026. Which versions fix them, three ways to see the version your web server really runs, and the interim settings php.net lists.
updated: 2026-10-22
---

If your site runs PHP 8.5, 8.4, 8.3 or 8.2, update to 8.5.12, 8.4.27, 8.3.36 or 8.2.35 (or newer). Those are the releases php.net announced on 21 October 2026 for two critical remote code execution bugs, CVE-2026-109618 and CVE-2026-109619. This page shows how to find the version your web server actually uses. It is defensive only and contains no attack details.

## What php.net says

The php.net security advisory dated 21 October 2026 describes both bugs as critical. It names the fixed releases and says all PHP installations that serve web requests are at risk. It lists PHP-FPM, Apache with mod_php, php-cgi, FrankenPHP and LiteSpeed, and says the risk is highest for mod_php.

| Your branch | Fixed release |
|---|---|
| PHP 8.5 | 8.5.12 |
| PHP 8.4 | 8.4.27 |
| PHP 8.3 | 8.3.36 |
| PHP 8.2 | 8.2.35 |

The advisory also says PHP 8.6.0 RC4 includes the fixes. PHP 8.1 and older no longer get updates from the project; the security team published minimal backports for 7.4, 8.0 and 8.1 on GitHub branches. If you are on one of those, ask your vendor or plan an upgrade to a supported branch.

## Find the version your web server really runs

The command line and the web server can use different PHP builds, so check the one that serves your pages.

1. **On the server:** run `php -v`. This shows the command-line PHP, which may not be the one behind your site.
2. **From outside:** run `curl -sI https://your-site.example` and look for an `X-Powered-By: PHP/...` line. It only appears if the server sends that header, and many sites hide it.
3. **Ask your host or package manager:** Linux distributions may ship a fix under an older version number, so a "lower" number does not always mean unpatched. Check your vendor's security notice for these two CVE IDs.

If you want a quick answer in the browser, the [PHP version checker](/honest-guide/en/tools/php-version-checker/) compares a pasted `php -v` output or header with the fixed releases. It runs locally and sends nothing anywhere. You can also see which headers your own site sends with the [security headers checklist](/honest-guide/en/security-headers-checklist/).

## Interim settings (only an update is a complete fix)

php.net says plainly that only an update is a complete solution, and that these measures "reduce exposure to specific attack paths but do not make an installation safe". The ones it lists:

- `memory_limit=-1`, set where applications cannot change it back (for example `php_admin_value` in the FPM pool or Apache config).
- A low `post_max_size`: `8M` if you do not need uploads, `32M` if you do, with `upload_max_filesize` kept below it.
- `session.upload_progress.enabled=0` in `php.ini`, an FPM pool or server configuration, then restart every worker. php.net says not to rely on `ini_set()` or FPM `.user.ini` for this.
- On PHP 8.5 only, `fatal_error_backtraces=0`, then restart every worker.
- Request-size limits at the web server or proxy, and a container or cgroup limit as an availability boundary.

## Who this is not for

If a host manages PHP for you (a managed platform that updates itself), your job may be only to confirm with them. This page does not cover older PHP branches beyond what php.net states, does not describe how the bugs work, and is not a full server security review. Check your own vendor's advisory for exact package versions.

## Sources (checked 2026-10-22)

- PHP security advisory, October 2026 (8.5.12, 8.4.27, 8.3.36, 8.2.35): <https://www.php.net/archive/2026.php#2026-10-21-5>
- php.net front page, where the same release announcement is listed: <https://www.php.net/>
