#!/usr/bin/env python3
"""Detect truncated figure crops.

A figure cropped from a PDF is truncated when the crop box cuts through content
instead of falling in the surrounding whitespace. That shows up as ink touching
the edge of the image: a correctly cropped figure has a clean margin on all four
sides.

For every PNG referenced by a deck, this measures the fraction of non-white
pixels in a thin band along each edge. Anything above the threshold is reported
so it can be re-cropped or inspected.

    python3 tools/check-figure-crops.py             # figures used by decks
    python3 tools/check-figure-crops.py --all       # every png in figures/auto
    python3 tools/check-figure-crops.py --strict    # tighter threshold

Exits non-zero when a figure looks truncated.
"""
import os
import re
import sys
import glob

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print('needs pillow and numpy')
    sys.exit(2)

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAND = 3          # pixels inspected along each edge
WHITE = 240       # brighter than this counts as background
THRESHOLD = 0.05  # fraction of edge pixels that may be ink before flagging


def looks_like_border(ink, which):
    """A drawn frame is a thin, near-continuous line hugging the edge; a cut
    leaves irregular content. Compare the outermost lines to the ones just
    inside: a border is dense at the very edge and empty immediately after."""
    if which in ('top', 'bottom'):
        lines = ink[:6, :] if which == 'top' else ink[-6:, :][::-1]
        prof = [lines[i, :].mean() for i in range(min(6, lines.shape[0]))]
    else:
        lines = ink[:, :6] if which == 'left' else ink[:, -6:][:, ::-1]
        prof = [lines[:, i].mean() for i in range(min(6, lines.shape[1]))]
    if not prof:
        return False
    outer = max(prof[:3])
    inner = max(prof[3:]) if len(prof) > 3 else 0.0
    # dense line at the edge, clear space just inside it
    return outer > 0.5 and inner < outer * 0.35


def edge_ink(path):
    """Ink fraction on each edge, plus whether that edge looks like a border."""
    im = Image.open(path).convert('L')
    a = np.array(im)
    if a.shape[0] < BAND * 2 or a.shape[1] < BAND * 2:
        return None
    ink = a < WHITE
    out = {}
    for which, band in (('top', ink[:BAND, :]), ('bottom', ink[-BAND:, :]),
                        ('left', ink[:, :BAND]), ('right', ink[:, -BAND:])):
        out[which] = (band.mean(), looks_like_border(ink, which))
    return out


def figures_used():
    used = {}
    for deck in sorted(glob.glob(os.path.join(REPO, 'paper', '*.html'))):
        html = open(deck).read()
        for rel in set(re.findall(r'src="\.\./(assets/figures/[^"#?]+)"', html)):
            used.setdefault(rel, []).append(os.path.basename(deck))
    return used


def main():
    strict = '--strict' in sys.argv
    threshold = 0.02 if strict else THRESHOLD

    if '--all' in sys.argv:
        targets = {os.path.relpath(p, REPO): [] for p in
                   sorted(glob.glob(os.path.join(REPO, 'assets/figures/auto/*.png')))}
    else:
        targets = figures_used()

    flagged, checked = [], 0
    for rel, decks in sorted(targets.items()):
        path = os.path.join(REPO, rel)
        if not os.path.exists(path):
            flagged.append((rel, 'MISSING FILE', decks))
            continue
        e = edge_ink(path)
        if e is None:
            continue
        checked += 1
        # ignore edges that are a drawn frame rather than cut-off content
        hot = {k: v for k, (v, is_border) in e.items()
               if v > threshold and not is_border}
        if hot:
            desc = ', '.join(f'{k} {v*100:.0f}% ink' for k, v in sorted(
                hot.items(), key=lambda kv: -kv[1]))
            flagged.append((rel, desc, decks))

    print(f'checked {checked} figures (threshold {threshold*100:.0f}% ink on a '
          f'{BAND}px edge band)\n')
    if not flagged:
        print('OK — no figure has content touching its edge.')
        return 0

    print('POSSIBLY TRUNCATED — content runs to the edge:\n')
    for rel, desc, decks in flagged:
        where = f"  [{', '.join(decks)}]" if decks else ''
        print(f'  {os.path.basename(rel):<34} {desc}{where}')
    print('\nRe-crop these, or confirm by eye that the bleed is intentional '
          '(e.g. a full-bleed screenshot).')
    return 1


if __name__ == '__main__':
    sys.exit(main())
