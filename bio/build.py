#!/usr/bin/env python3
"""Generate a plain-text .txt next to every .md in this folder: links become their text, inline HTML is dropped."""
import re, pathlib
here = pathlib.Path(__file__).parent
for md in sorted(here.glob('*.md')):
    if md.name == 'README.md':
        continue
    text = md.read_text()
    text = re.sub(r'\[([^\]]+)\]\((?:[^()]|\([^()]*\))*\)', r'\1', text)   # [text](url) -> text
    text = re.sub(r'<a [^>]*>(.*?)</a>', r'\1', text)                        # <a>text</a> -> text
    text = re.sub(r'\*\*?([^*]+)\*\*?', r'\1', text)                          # *em* / **strong** -> plain
    text = re.sub(r'<[^>]+>', '', text)
    md.with_suffix('.txt').write_text(text.strip() + '\n')
    print(f'{md.name} -> {md.with_suffix(".txt").name}')

# ── bio/index.html: a file list in the site's style, so qiaojin.info/bio/ shows
#    what is here instead of GitHub's default rendering of the README. ──
DESC = {
    'homepage':      'First-person bio shown on the homepage (rendered from the Markdown at load).',
    'academic-long': 'Third-person academic bio for talks, programs, and introductions.',
}
rows = []
for md in sorted(here.glob('*.md')):
    if md.name == 'README.md':
        continue
    stem = md.stem
    words = len(md.with_suffix('.txt').read_text().split())
    rows.append(
        f'      <li><div class="name">{stem}</div>'
        f'<div class="desc">{DESC.get(stem, "")} <span class="meta">{words} words</span></div>'
        f'<div class="links"><a href="{md.name}">Markdown</a><a href="{stem}.txt">Plain text</a></div></li>')
page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qiao Jin — Bios</title>
  <meta name="robots" content="noindex">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;1,9..40,400&family=DM+Serif+Display&display=swap" rel="stylesheet">
  <style>
    html, body {{ margin: 0; background: #f0ede6; color: #222; font-family: "DM Sans", -apple-system, BlinkMacSystemFont, sans-serif; }}
    a {{ color: #666; text-decoration: underline; text-underline-offset: 3px; }}
    a:hover {{ color: #b89a60; }}
    .wrap {{ max-width: 640px; margin: 0 auto; padding: 44px 24px 64px; }}
    .top {{ display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 28px; }}
    .top h1 {{ font-family: "DM Serif Display", Georgia, serif; font-weight: 400; font-size: 1.6rem; margin: 0; }}
    .top a {{ font-size: 0.9rem; text-decoration: none; }}
    p.lead {{ color: #666; font-size: 0.95rem; line-height: 1.5; margin: 0 0 24px; }}
    ul {{ list-style: none; margin: 0; padding: 0; border-top: 1px solid #d8d4cc; }}
    li {{ padding: 16px 0; border-bottom: 1px solid #d8d4cc; }}
    .name {{ font-family: "DM Serif Display", Georgia, serif; font-size: 1.15rem; margin-bottom: 4px; }}
    .desc {{ font-size: 0.92rem; line-height: 1.45; color: #444; }}
    .meta {{ color: #918b81; font-size: 0.82rem; white-space: nowrap; }}
    .links {{ margin-top: 8px; font-size: 0.85rem; }}
    .links a {{ margin-right: 16px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top"><h1>Bios</h1><a href="../">&larr; Home</a></div>
    <p class="lead">Master copies of Qiao Jin’s bios. Each is kept as Markdown, with a plain-text twin that has the links removed.</p>
    <ul>
{chr(10).join(rows)}
    </ul>
  </div>
</body>
</html>
"""
(here / 'index.html').write_text(page)
print('index.html')
