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
