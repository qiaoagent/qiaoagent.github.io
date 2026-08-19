#!/usr/bin/env python3
"""Insert (or remove) the Cloudflare Web Analytics beacon across the site.

    python3 tools/add-analytics.py <token>     # install
    python3 tools/add-analytics.py --remove    # take it back out

Idempotent: re-running with a different token updates it in place rather
than stacking a second beacon. Touches index/research/cj plus every deck.
"""
import glob, pathlib, re, sys

MARK = "<!-- Cloudflare Web Analytics -->"
END  = "<!-- End Cloudflare Web Analytics -->"
TPL = (MARK + "<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
       "data-cf-beacon='{\"token\": \"%s\"}'></script>" + END + "\n")
PAT = re.compile(re.escape(MARK) + r".*?" + re.escape(END) + r"\n?", re.S)

def pages():
    return sorted(glob.glob("*.html")) + sorted(glob.glob("paper/*.html"))

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    remove = sys.argv[1] == "--remove"
    token = None if remove else sys.argv[1]
    if token and not re.fullmatch(r"[0-9a-f]{32}", token):
        sys.exit(f"token should be 32 hex chars, got: {token!r}")

    changed = skipped = 0
    for f in pages():
        p = pathlib.Path(f)
        s = p.read_text()
        had = bool(PAT.search(s))
        s2 = PAT.sub("", s)                       # drop any existing beacon
        if not remove:
            if "</body>" not in s2:
                print(f"  !! no </body>, skipped: {f}")
                skipped += 1
                continue
            s2 = s2.replace("</body>", TPL % token + "</body>", 1)
        if s2 != s:
            p.write_text(s2)
            changed += 1
            print(f"  {'removed from' if remove else ('updated' if had else 'added to')} {f}")
    print(f"\n  {changed} file(s) changed, {skipped} skipped, {len(pages())} scanned")

if __name__ == "__main__":
    main()
