#!/usr/bin/env python3
"""Audit every paper deck against the agreed house rules.

Static checks only — layout rules that need a browser (one-page fit, rendered
figure width) are covered separately by the browser probe.

    python3 tools/audit-decks.py
"""
import glob
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRONOUN_START = ('It ', 'They ', 'And ', 'But ', 'Its ', 'Their ', 'This ', 'These ', 'That ')
MID_START = ('using', 'rewarding', 'verifying', 'training', 'detecting', 'learning',
             'scaling', 'better', 'more', 'from', 'where', 'what', 'which', 'why',
             'how', 'and', 'but', 'so', 'toward', 'towards')
DISPLAY = r'(<figure class="fig|<div class="tbl-wrap"|<div class="stats">|<div class="chart-wrap")'

# Deliberate exceptions, agreed with the author rather than silently ignored.
# PubMedQA carries extra hero links (Hugging Face, Leaderboard) by request.
ACCEPTED_EXTRA_HERO_LINKS = {'PubMedQA.html'}
# AgentMD's MIMIC-III slide states a scaling result without reproducing a figure.
ACCEPTED_NO_DISPLAY = {('AgentMD.html', 'result-4')}



def strip(s):
    return re.sub(r'<[^>]+>', '', s).replace('&rsquo;', "'").replace('&mdash;', '—').strip()


def audit(path):
    h = open(path).read()
    name = os.path.basename(path)
    issues = []

    # deck-level
    if 'help of AI' not in h:
        issues.append(('disclaimer', 'hero is missing the AI disclaimer'))
    links = re.search(r'<div class="links">(.*?)</div>', h, re.S)
    if links:
        labels = [strip(x) for x in re.findall(r'<a[^>]*>(.*?)</a>', links.group(1))]
        if len(labels) != 2 and name not in ACCEPTED_EXTRA_HERO_LINKS:
            issues.append(('hero-links', f'{len(labels)} hero links {labels}, expected PDF + Journal/arXiv'))
        elif labels[0] != 'PDF' or (labels[1] not in ('Journal', 'arXiv', 'Proceedings')
                                    and name not in ACCEPTED_EXTRA_HERO_LINKS):
            issues.append(('hero-links', f'hero links are {labels}'))
    if re.search(r'\b(cited|citations?)\s+\d{2,}|\d{2,}\s+citations\b', h, re.I):
        issues.append(('citation-count', 'a citation count appears in the text'))
    if 'class="back"' in h:
        issues.append(('back-link', 'research.html back-link present while research.html is unpublished'))
    if re.search(r'(src|href)="\.\./[^"]*\?v=', h):
        issues.append(('cache-buster', 'asset URL carries a ?v= cache-buster'))

    # slide-level
    for s in re.findall(r'<section class="slide".*?</section>', h, re.S):
        sid = (re.search(r'id="([^"]+)"', s) or [None, '?'])[1]
        kick = re.search(r'<span class="n">\d+</span>([\w ]+)</div>', s)
        kind = kick.group(1).strip() if kick else ''
        title = strip((re.search(r'<h2>(.*?)</h2>', s, re.S) or [None, ''])[1])
        body = (re.search(r'<div class="body">(.*)</div></section>', s, re.S) or [None, ''])[1]

        if title.startswith(PRONOUN_START):
            issues.append((f'{sid} title', f'starts with a pronoun: "{title[:52]}"'))
        elif title.split() and title.split()[0].lower() in MID_START:
            issues.append((f'{sid} title', f'no subject: "{title[:52]}"'))

        if 'class="lead"' in s:
            issues.append((f'{sid} lead', 'uses a grey .lead subtitle'))

        ul = re.search(r'<ul class="highlights">(.*?)</ul>', body, re.S)
        nb = len(re.findall(r'<li[ >]', ul.group(1))) if ul else 0
        # `nobul` renders without a marker, so a single one reads as a plain
        # lead-in sentence rather than a stray bullet — that is the agreed use,
        # whether or not it introduces sub-bullets
        unmarked = bool(ul and 'class="nobul"' in ul.group(1))
        if nb == 1 and not unmarked:
            issues.append((f'{sid} bullets', 'single bullet — needs at least two'))

        disp = re.search(DISPLAY, body)
        if kind.lower().startswith('result') and not disp and (name, sid) not in ACCEPTED_NO_DISPLAY:
            issues.append((f'{sid} display', 'Result slide with no figure/table/stats'))
        if ul and disp and re.search(r'<ul class="highlights">', body).start() > disp.start():
            issues.append((f'{sid} order', 'bullets sit below the display'))
    return name, issues


def main():
    decks = sorted(glob.glob(os.path.join(REPO, 'paper', '*.html')))
    total = 0
    for d in decks:
        name, issues = audit(d)
        if issues:
            total += len(issues)
            print(f'--- {name} ---')
            for where, what in issues:
                print(f'    {where:<22} {what}')
    print(f'\n{len(decks)} decks audited, {total} issues')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(main())
