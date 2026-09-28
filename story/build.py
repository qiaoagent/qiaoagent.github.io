#!/usr/bin/env python3
"""Render story/index.html from why-i-left-medicine-for-ai.md: a slide-sized block (figure + short text)
that can be screenshotted into a talk, then the essay. `?fig=1|2|3` picks the figure while he chooses."""
import pathlib, re, html

here = pathlib.Path(__file__).parent
md = (here / 'why-i-left-medicine-for-ai.md').read_text().strip().split('\n\n')
title = md[0].lstrip('# ').strip()
if not title.endswith('?'): title += '?'
paras = md[1:]

SLIDE_SUB = 'Reliable medical information is as important as treatment'
PHOTO_LINES = ('Wei Zexi\u2019s parents hold his portrait. He died at 21 in 2016, after a Baidu (China\u2019s Google)',
               'ad led him to an untested \u201cimmunotherapy\u201d that cost about $30,000 and did nothing.')
PHOTO_TEXT = ' '.join(PHOTO_LINES)

BLUE, GOLD, INK, MUTED, FAINT, LINE = '#2c5a8c', '#b89a60', '#222', '#6a655d', '#918b81', '#d8d4cc'

def timeline_svg():
    steps = [('2014', 'Diagnosed with advanced', 'synovial sarcoma, age 19'),
             ('2014–15', 'Chemotherapy and', 'radiotherapy fail'),
             ('Baidu', 'A Baidu ad ranks', 'a Beijing hospital first'),
             ('Untested', '“Immunotherapy”, 4 rounds,', 'about $30,000, no effect'),
             ('April 2016', 'Dies at 21', '')]
    W, H = 960, 230; n = len(steps); x0, x1 = 90, W - 90; y = 110
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="DM Sans, sans-serif">']
    out.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{LINE}" stroke-width="1.5"/>')
    for i, (k, a, b) in enumerate(steps):
        x = x0 + (x1 - x0) * i / (n - 1)
        last = i == n - 1
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="{9 if last else 7}" fill="{GOLD if i == 2 else (INK if last else BLUE)}"/>')
        out.append(f'<text x="{x:.1f}" y="{y - 26}" text-anchor="middle" font-size="12" font-weight="600" letter-spacing=".12em" fill="{GOLD if i == 2 else (INK if last else BLUE)}">{html.escape(k.upper())}</text>')
        out.append(f'<text x="{x:.1f}" y="{y + 40}" text-anchor="middle" font-size="15" fill="{INK}">{html.escape(a)}</text>')
        if b: out.append(f'<text x="{x:.1f}" y="{y + 62}" text-anchor="middle" font-size="15" fill="{MUTED}">{html.escape(b)}</text>')
    out.append('</svg>')
    return '\n'.join(out)

def search_svg():
    W, H = 960, 330
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="DM Sans, sans-serif">']
    # search box
    o.append(f'<rect x="150" y="26" width="660" height="44" rx="22" fill="#fff" stroke="{LINE}" stroke-width="1.5"/>')
    o.append(f'<text x="176" y="54" font-size="16" fill="{INK}">synovial sarcoma treatment</text>')
    o.append(f'<circle cx="784" cy="48" r="7" fill="none" stroke="{MUTED}" stroke-width="2"/><line x1="789" y1="53" x2="795" y2="59" stroke="{MUTED}" stroke-width="2" stroke-linecap="round"/>')
    # result 1: the ad
    o.append(f'<rect x="150" y="96" width="660" height="92" rx="10" fill="#fff6e3" stroke="{GOLD}" stroke-width="1.5"/>')
    o.append(f'<rect x="168" y="112" width="34" height="18" rx="4" fill="{GOLD}"/><text x="185" y="125" text-anchor="middle" font-size="11" font-weight="700" fill="#fff">AD</text>')
    o.append(f'<text x="212" y="126" font-size="17" fill="{INK}">Tumour Biology Centre, a Beijing hospital</text>')
    o.append(f'<text x="168" y="152" font-size="14" fill="{MUTED}">“Biological immunotherapy” · 80–90% effective · developed with Stanford</text>')
    o.append(f'<text x="168" y="174" font-size="14" fill="{GOLD}" font-weight="600">Untested. Trials abroad had stopped. No Stanford partnership existed.</text>')
    # results 2-3: greyed
    for k, (yy, t) in enumerate([(212, 'Synovial sarcoma: overview, diagnosis and treatment options'), (262, 'Clinical trials for soft-tissue sarcoma · patient information')]):
        o.append(f'<text x="168" y="{yy + 18}" font-size="17" fill="{FAINT}">{html.escape(t).replace("&#8212;", "&#x2014;")}</text>')
        o.append(f'<rect x="168" y="{yy + 30}" width="{420 - 60 * k}" height="6" rx="3" fill="#ecebe7"/>')
    o.append('</svg>')
    return '\n'.join(o)

PHOTO = '<img class="photo" src="_wei-zexi-parents-caixin.jpg" alt="Wei Zexi\u2019s parents, holding his portrait, wait outside the funeral home in Xianyang on 13 April 2016">'

def slide():
    cap = '<p class="stext eq">' + ' '.join('<span class="ln">' + html.escape(l) + '</span>' for l in PHOTO_LINES) + '</p>'
    return ('<section class="opener">\n  <div class="slide"><p class="sline">' + html.escape(SLIDE_SUB) + '</p>'
            '<div class="fig">' + PHOTO + '<div class="credit">Photo: Wan Jia / Caixin, 2016</div></div>' + cap + '</div>\n</section>')

def figure(svg, caption):
    return '    <figure class="efig">' + svg + '<figcaption>' + html.escape(caption) + '</figcaption></figure>'

FIGS_AFTER = {   # paragraph index -> figure placed after it
    0: figure(timeline_svg(), 'From diagnosis to death: the step that found the hospital was an advertisement.'),
    1: figure(search_svg(), 'What the family saw: a paid listing ranked first, its claims untrue.'),
}

essay = '\n'.join(f'    <p>{html.escape(p)}</p>' + ('\n' + FIGS_AFTER[k] if k in FIGS_AFTER else '') for k, p in enumerate(paras))
page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)} — Qiao Jin</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">
<style>
  :root{{--bg:#fff;--ink:#222;--muted:#6a655d;--faint:#918b81;--border:#e6e5e1;--gold:#b89a60;}}
  *{{box-sizing:border-box;}}
  body{{margin:0;background:var(--bg);color:var(--ink);font-family:"DM Sans",-apple-system,BlinkMacSystemFont,sans-serif;line-height:1.68;-webkit-font-smoothing:antialiased;}}
  a{{color:inherit;}}
  .nav{{position:sticky;top:0;z-index:10;background:rgba(255,255,255,0.9);backdrop-filter:blur(8px);border-bottom:1px solid var(--border);}}
  .nav .wrap{{max-width:820px;margin:0 auto;padding:0 30px;display:flex;align-items:center;justify-content:space-between;height:56px;}}
  .nav .brand{{font-family:"DM Serif Display",Georgia,serif;font-size:1.05rem;text-decoration:none;}}
  .nav .back{{font-size:0.86rem;color:var(--muted);text-decoration:none;}} .nav .back:hover{{color:var(--gold);}}
  .wrap-main{{max-width:820px;margin:0 auto;padding:0 30px 70px;}}
  h1{{font-family:"DM Serif Display",Georgia,serif;font-weight:400;font-size:2.3rem;line-height:1.16;margin:52px 0 26px;letter-spacing:-0.01em;}}
  /* the slide: a 16:9 frame that screenshots straight into a deck */
  .opener{{margin:0 0 40px;}}
  .slide{{aspect-ratio:16/9;background:#fff;border:1px solid var(--border);border-radius:6px;padding:34px 44px 30px;display:flex;flex-direction:column;justify-content:space-between;}}
  /* the statement line is set like the vision line on future.html */
  .slide .sline{{font-family:"DM Serif Display",Georgia,serif;font-size:1.25rem;line-height:1.4;text-align:center;margin:0 0 16px;}}
  .slide .fig{{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;overflow:hidden;padding-bottom:16px;}}
  .slide .fig svg{{width:100%;height:100%;}}
  .slide .fig{{position:relative;}} .slide .fig img.photo{{max-height:100%;max-width:100%;object-fit:contain;filter:grayscale(1);}}
  .slide .credit{{position:absolute;right:0;bottom:0;font-size:0.68rem;color:var(--faint);letter-spacing:.02em;}}
  .slide .stext{{margin:6px auto 0;max-width:600px;text-align:center;font-size:0.98rem;line-height:1.5;color:var(--ink);text-wrap:balance;}}   /* lines of near-equal length */
  /* photo slide: three pre-split lines justified to one width, so they are exactly equal */
  .slide .stext.eq{{width:632px;max-width:100%;text-align:justify;text-align-last:justify;text-wrap:wrap;}}
  .slide .stext.eq .ln{{display:block;}}
  .efig{{margin:6px 0 26px;}} .efig svg{{width:100%;height:auto;display:block;}}
  .efig figcaption{{font-size:0.82rem;color:var(--faint);text-align:center;margin-top:4px;}}
  .essay{{max-width:640px;margin-top:16px;}}
  .essay p{{font-size:1.04rem;margin:0 0 18px;}}
  footer{{padding:34px 0 0;color:var(--faint);font-size:0.85rem;}}
  @media (max-width:660px){{h1{{font-size:1.85rem;margin-top:36px;}} .opener{{margin-top:0;}} .slide{{padding:18px 20px 16px;aspect-ratio:auto;}} .slide .sline{{font-size:1.1rem;}} .slide .fig{{height:236px;}} .slide .stext{{font-size:0.95rem;}} .slide .stext.eq{{width:auto;text-align:center;text-align-last:auto;}} .slide .stext.eq .ln{{display:inline;}}}}
</style></head>
<body>
  <nav class="nav"><div class="wrap"><a class="brand" href="../index.html">Qiao Jin</a><a class="back" href="../index.html">&larr; Home</a></div></nav>
  <main class="wrap-main">
    <h1>{html.escape(title)}</h1>
{slide()}
    <div class="essay">
{essay}
    </div>
    <footer>Qiao Jin · NIH/NLM</footer>
  </main>

</body></html>
'''
(here / 'index.html').write_text(page)
print('story/index.html written;', len(paras), 'paragraphs')
