#!/usr/bin/env python3
"""Pre-publish guard for the paper decks.

Every deck references its cover, figures and PDF with relative paths like
`../assets/figures/auto/X.png`. If such a file exists locally but was never
committed, the deck still publishes fine and the asset 404s in production —
which is exactly how 28 assets ended up broken on qiaojin.info.

Run this before pushing any deck:

    python3 tools/check-deck-assets.py            # check decks tracked in git
    python3 tools/check-deck-assets.py --all      # also check unpublished decks

Exits non-zero if a deck references an asset that is not tracked.
"""
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(['git'] + list(args), capture_output=True, text=True,
                          cwd=REPO).stdout


def main():
    check_all = '--all' in sys.argv
    tracked = set(git('ls-files').split('\n'))

    if check_all:
        decks = sorted(f'paper/{f}' for f in os.listdir(os.path.join(REPO, 'paper'))
                       if f.endswith('.html'))
    else:
        decks = [d for d in git('ls-files', 'paper/').split() if d.endswith('.html')]

    problems, missing_locally = {}, {}
    for deck in decks:
        path = os.path.join(REPO, deck)
        if not os.path.exists(path):
            continue
        html = open(path).read()
        # relative (../assets/x.png) and root-absolute (/assets/x.js) references,
        # ignoring any ?v= cache-buster or #fragment
        refs = set(re.findall(r'(?:src|href)="\.\./([^"#?]+?)(?:[?#][^"]*)?"', html))
        refs |= set(re.findall(r'(?:src|href)="/([^"#?/][^"#?]*?)(?:[?#][^"]*)?"', html))
        untracked = sorted(r for r in refs if r not in tracked)
        if untracked:
            problems[deck] = untracked
        absent = sorted(r for r in refs if not os.path.exists(os.path.join(REPO, r)))
        if absent:
            missing_locally[deck] = absent

    # a deck that links a sibling deck which is not itself published
    dangling = {}
    for deck in decks:
        html = open(os.path.join(REPO, deck)).read()
        for sib in set(re.findall(r'href="([A-Za-z0-9_.-]+\.html)"', html)):
            rel = f'paper/{sib}'
            if rel != deck and rel not in tracked:
                dangling.setdefault(deck, []).append(sib)

    if missing_locally:
        print('MISSING ON DISK (broken even locally):')
        for d, xs in missing_locally.items():
            print(f'  {d}')
            for x in xs:
                print(f'      {x}')
        print()

    if problems:
        print('NOT COMMITTED (will 404 once the deck is live):')
        for d, xs in problems.items():
            print(f'  {d}  ({len(xs)})')
            for x in xs:
                print(f'      {x}')
        print()

    if dangling:
        print('LINKS TO AN UNPUBLISHED DECK (will 404 for visitors):')
        for d, xs in dangling.items():
            print(f'  {d} -> {", ".join(xs)}')
        print()

    if not (problems or missing_locally or dangling):
        print(f'OK — {len(decks)} decks checked, every referenced asset is tracked '
              f'and every linked deck is published.')
        return 0
    return 1


if __name__ == '__main__':
    sys.exit(main())
