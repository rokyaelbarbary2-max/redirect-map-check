#!/usr/bin/env python3
"""redirect_map_check.py - verify a redirect map after a URL migration.

usage: python3 redirect_map_check.py redirects.csv [--base https://example.com]

redirects.csv has two columns: old,new (paths or absolute URLs; a header row is allowed).
For every row it checks that:
  - the old URL answers a permanent redirect (301 or 308) in ONE hop,
  - the Location is exactly the new URL,
  - the new URL answers 200 (and is not itself redirected).
Exit code 0 = every row passes, 1 = at least one failure.
"""
import csv
import sys
import urllib.error
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (redirect-map-check)"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def head(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA}, method="GET")
    try:
        with OPENER.open(req, timeout=20) as r:
            return r.status, r.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")
    except Exception as e:
        return type(e).__name__, None


def absolute(base, u):
    return urllib.parse.urljoin(base + "/", u.strip())


def main():
    args = sys.argv[1:]
    base = ""
    if "--base" in args:
        i = args.index("--base")
        base = args[i + 1].rstrip("/")
        del args[i:i + 2]
    rows = [r for r in csv.reader(open(args[0], newline="", encoding="utf-8")) if len(r) >= 2]
    if rows and rows[0][0].strip().lower() in ("old", "from", "source"):
        rows = rows[1:]
    failures = 0
    for old, new in ((absolute(base, r[0]), absolute(base, r[1])) for r in rows):
        st, loc = head(old)
        loc_abs = absolute(old, loc) if loc else None
        problems = []
        if st not in (301, 308):
            problems.append(f"old answers {st}, expected 301/308")
        elif loc_abs != new:
            problems.append(f"redirects to {loc_abs}, expected {new}")
        st_new, loc_new = head(new)
        if st_new != 200:
            problems.append(f"new answers {st_new}" + (f" -> {loc_new}" if loc_new else ""))
        failures += bool(problems)
        print(("FAIL " if problems else "OK   ") + f"{old} -> {new}" + ("  | " + "; ".join(problems) if problems else ""))
    print(f"\n{len(rows) - failures}/{len(rows)} rows pass")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
