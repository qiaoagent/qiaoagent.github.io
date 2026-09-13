#!/usr/bin/env python3
"""Generate the future-research cycle figure (People / Trials / Evidence around an AI chip).

Writes the four direction-line proposals (q1-q4) into _future-candidates.html, replacing
any existing proposal sections and the shared figure script. The figure geometry, captions
and project codes live here so the HTML can be regenerated rather than hand-edited.

    python3 tools/gen-future-figure.py
"""
import math
import os
import re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(REPO, '_future-candidates.html')

GEN, UTIL, EVAL, GOLD, FAINT, MUTED = '#2f6d5b', '#2c5a8c', '#6b3f8c', '#b89a60', '#918b81', '#6a655d'
CX, CY, R = 300, 268, 150          # ring centre and radius
GAP = 27                            # degrees between a node and the nearest arrowhead
START = 54                          # spokes begin this far from the centre (clear of the chip pins)
H, PIN_L, PIN_W, PINS = 32, 10, 4, (-20, 0, 20)
LABR = R + 24                       # label anchor radius
BR, INSET, SPREAD, NUDGE = 14, 19, 14, 2   # code beads: radius, inset from the ring, pair spacing, pair nudge

rad = math.radians
P = lambda a, rr=R: (CX + rr * math.cos(rad(a)), CY + rr * math.sin(rad(a)))

NAME = {'people': 'PEOPLE', 'trials': 'TRIALS', 'evidence': 'EVIDENCE'}
CAP = {('lp', 'people'): 'Matching clinical trials to patients',
       ('lp', 'trials'): 'Matching patients to clinical trials',
       ('rp', 'people'): 'Meeting real-world information needs',
       ('rp', 'evidence'): 'Evaluating if and how AI actually helps people',
       ('bp', 'evidence'): 'AI-enabled living evidence synthesis',
       ('bp', 'trials'): 'Evidence-informed clinical trial design'}
CODE = {('lp', 'people'): ['A.1'], ('lp', 'trials'): ['A.1'], ('rp', 'people'): ['B.1', 'B.2'],
        ('rp', 'evidence'): ['C'], ('bp', 'evidence'): ['A.2'], ('bp', 'trials'): []}
# (id, node at the start angle, node at the end angle, start, end, joint, colour)
PAIRS = [('lp', 'trials', 'people', 150 + GAP, 270 - GAP, 210, GOLD),
         ('rp', 'people', 'evidence', -90 + GAP, 30 - GAP, -30, UTIL),
         ('bp', 'evidence', 'trials', 30 + GAP, 150 - GAP, 90, GEN)]
TITLE = 'Connecting people, clinical trials and evidence through trustworthy AI'


def pyramid_g(x, y, scale=0.78):
    """The site's own evidence pyramid (assets/direction-figures.js), placed at (x, y)."""
    n, top, hh, wtop, wbot, g = 5, 8, 76, 20, 92, 2.4
    s = ''
    for i in range(n):
        wa = wtop + (wbot - wtop) * i / n
        wb = wtop + (wbot - wtop) * (i + 1) / n
        yy = top + i * (hh / n)
        h = hh / n - g
        s += (f'<polygon points="{60 - wa / 2:.1f},{yy:.1f} {60 + wa / 2:.1f},{yy:.1f} '
              f'{60 + wb / 2:.1f},{yy + h:.1f} {60 - wb / 2:.1f},{yy + h:.1f}" fill="{GEN}" opacity="{0.94 - i * 0.13:.2f}"/>')
    return f'<g transform="translate({x - 60 * scale:.1f} {y - 46 * scale:.1f}) scale({scale})">{s}</g>'


def person_g(x, y, c=UTIL):
    return (f'<g transform="translate({x:.1f} {y:.1f})"><circle cx="0" cy="-14" r="13" fill="{c}" opacity=".94"/>'
            f'<path d="M-24 34 Q-24 4 0 4 Q24 4 24 34 Z" fill="{c}" opacity=".62"/></g>')


def pill_g(x, y, c=GOLD):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate(-35)">'
            f'<path d="M-30 -13 H0 V13 H-30 A13 13 0 0 1 -30 -13 Z" fill="{c}" opacity=".94"/>'
            f'<path d="M0 -13 H30 A13 13 0 0 1 30 13 H0 Z" fill="{c}" opacity=".55"/></g>')


def fillet(theta, c, h=22, delta=10):
    """Filled web where a radial spoke meets the ring: tangent-continuous with both."""
    t = rad(theta)
    ux, uy = math.cos(t), math.sin(t)
    m = P(theta)
    a = (m[0] - h * ux, m[1] - h * uy)

    def side(sign):
        b = rad(theta + sign * delta)
        bp = (CX + R * math.cos(b), CY + R * math.sin(b))
        tx, ty = -math.sin(b), math.cos(b)
        det = ux * (-ty) - uy * (-tx)
        s = ((bp[0] - a[0]) * (-ty) - (bp[1] - a[1]) * (-tx)) / det
        return bp, (a[0] + s * ux, a[1] + s * uy)

    b1, c1 = side(-1)
    b2, c2 = side(+1)
    return (f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {b1[0]:.1f} {b1[1]:.1f} A{R} {R} 0 0 1 '
            f'{b2[0]:.1f} {b2[1]:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {a[0]:.1f} {a[1]:.1f} Z" fill="{c}"/>')


def spoke_unit(pair, theta, c):
    s, m = P(theta, START), P(theta)
    return (f'<g class="unit sp-{pair}"><path d="M{s[0]:.1f} {s[1]:.1f} L{m[0]:.1f} {m[1]:.1f}" fill="none" '
            f'stroke="{c}" stroke-width="2"/>{fillet(theta, c)}</g>')


def arcpath(a1, a2):
    x1, y1 = P(a1)
    x2, y2 = P(a2)
    return f'M{x1:.1f} {y1:.1f} A{R} {R} 0 0 1 {x2:.1f} {y2:.1f}'


def head(a, sign, cls, c):
    tx, ty = -math.sin(rad(a)) * sign, math.cos(rad(a)) * sign
    nx, ny = -ty, tx
    t = P(a)
    b = (t[0] - 7 * tx, t[1] - 7 * ty)
    return (f'<path class="unit {cls}" d="M{t[0]:.1f} {t[1]:.1f} L{b[0] + 3.5 * nx:.1f} {b[1] + 3.5 * ny:.1f} '
            f'L{b[0] - 3.5 * nx:.1f} {b[1] - 3.5 * ny:.1f} Z" fill="{c}"/>')


def dlabel(style, pair, frm, to, mid, c):
    x, y = P(mid, LABR)
    sn = math.sin(rad(mid))
    mode = 'below' if sn > 0.5 else ('above' if sn < -0.5 else 'side')
    a = mid % 360
    anchor = 'start' if (a < 90 or a > 270) else 'end'
    muted = ' muted' if not CODE[(pair, to)] else ''
    note = (f'<text class="note" x="{x:.0f}" y="0" text-anchor="{anchor}" font-size="11" font-style="italic" '
            f'fill="{FAINT}">(not covered by this proposal)</text>') if muted else ''
    return (f'<g class="unit dlab dlab-{pair}-{to}{muted}" data-pair="{pair}" data-to="{to}" data-from="{frm}" '
            f'data-mode="{mode}" data-x="{x:.0f}" data-y="{y:.0f}" style="--c:{c};cursor:pointer">'
            f'<g class="dir" data-style="{style}" data-anchor="{anchor}" data-from="{NAME[frm]}" data-to="{NAME[to]}" '
            f'data-x="{x:.0f}" fill="{c}" font-size="11" font-weight="700" letter-spacing=".08em"></g>'
            f'<text class="cap" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="13" fill="{MUTED}" '
            f'data-text="{CAP[(pair, to)]}"></text>{note}</g>')


def bead(pair, to, mid, c, away):
    codes = CODE[(pair, to)]
    n = len(codes)
    centre = mid + (away * NUDGE if n > 1 else 0)
    out = ''
    for i, cd in enumerate(codes):
        a = centre + (i - (n - 1) / 2) * SPREAD
        bx, by = P(a, R - INSET)
        out += (f'<g class="unit dlab-{pair}-{to}"><circle cx="{bx:.1f}" cy="{by:.1f}" r="{BR}" fill="{c}"/>'
                f'<text x="{bx:.1f}" y="{by + 3.8:.1f}" text-anchor="middle" font-size="10.5" font-weight="700" fill="#fff">{cd}</text></g>')
    return out


def cycle(key):
    style = STYLE[key]
    arcs = heads = hits = spokes = dlabs = beads = ''
    eps = math.degrees(7 / R)
    for pid, n1, n2, a1, a2, mid, c in PAIRS:
        arcs += (f'<path class="unit arc arc-{pid}" style="--c:{c}" d="{arcpath(a1 + eps, a2 - eps)}" '
                 f'fill="none" stroke="{c}" stroke-width="2"/>')
        heads += head(a1, -1, f'ah ah-{pid}-{n1}', c) + head(a2, +1, f'ah ah-{pid}-{n2}', c)
        spokes += spoke_unit(pid, mid, c)
        hits += (f'<path class="hit" data-pair="{pid}" data-to="{n1}" data-from="{n2}" d="{arcpath(a1, mid)}"/>'
                 f'<path class="hit" data-pair="{pid}" data-to="{n2}" data-from="{n1}" d="{arcpath(mid, a2)}"/>')
        dlabs += dlabel(style, pid, n2, n1, (a1 + mid) / 2, c) + dlabel(style, pid, n1, n2, (mid + a2) / 2, c)
        beads += bead(pid, n1, (a1 + mid) / 2, c, -1) + bead(pid, n2, (mid + a2) / 2, c, +1)
    pins = ''
    for o in PINS:
        pins += (f'<rect x="{CX + o - PIN_W / 2:.1f}" y="{CY - H - PIN_L}" width="{PIN_W}" height="{PIN_L}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX + o - PIN_W / 2:.1f}" y="{CY + H}" width="{PIN_W}" height="{PIN_L}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX - H - PIN_L}" y="{CY + o - PIN_W / 2:.1f}" width="{PIN_L}" height="{PIN_W}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX + H}" y="{CY + o - PIN_W / 2:.1f}" width="{PIN_L}" height="{PIN_W}" rx="2" fill="{EVAL}" opacity=".5"/>')
    px, py = P(-90)
    tx, ty = P(150)
    ex, ey = P(30)

    def node_name(x, y, t, anchor='middle'):
        return (f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-family="DM Serif Display, Georgia, serif" '
                f'font-size="21" fill="#222">{t}</text>')

    return f'''<svg class="cycle" id="cycle-{key}" viewBox="-40 40 680 510" xmlns="http://www.w3.org/2000/svg" font-family="DM Sans, sans-serif">
{arcs}{heads}{spokes}{beads}
<g class="unit ai"><g class="chip">{pins}<rect x="{CX - H}" y="{CY - H}" width="{2 * H}" height="{2 * H}" rx="9" fill="{EVAL}" opacity=".16"/><rect x="{CX - H + 9}" y="{CY - H + 9}" width="{2 * H - 18}" height="{2 * H - 18}" rx="5" fill="{EVAL}" opacity=".10"/></g>
<text x="{CX}" y="{CY + 10}" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="30" fill="{EVAL}">AI</text></g>
<g class="unit node node-people">{person_g(px, py)}{node_name(px, py - 46, 'People')}</g>
<g class="unit node node-trials">{pill_g(tx - 2, ty)}{node_name(tx - 20, ty + 58, 'Trials', 'end')}</g>
<g class="unit node node-evidence">{pyramid_g(ex, ey + 4)}{node_name(ex + 20, ey + 58, 'Evidence', 'start')}</g>
{hits}
{dlabs}
<text class="figtitle" x="300" y="538" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="17" fill="#222">{TITLE}</text>
</svg>'''


STYLE = {'q1': 'chain', 'q2': 'above', 'q3': 'dot', 'q4': 'chip', 'q5': 'badge'}   # proposal key -> compose() style
PROPOSALS = [
    ("q1", "AI as co-input",
     "AI as a partner, not a gate: TRIALS + AI → PEOPLE, with AI in the hub's purple. Wider titles, so the captions gain room too."),
    ("q2", "AI over the arrow",
     "Chemistry notation — the catalyst sits above the arrow. A small purple AI rides on a drawn arrow between the two words."),
    ("q3", "AI on the arrow",
     "The arrow passes through a purple dot: the flow goes via AI. The quietest option — no extra text at all."),
    ("q4", "Chip over the arrow",
     "Same as 2, but the hub's chip in miniature instead of the letters — the icon does the talking."),
    ("q5", "AI chip as a leading badge",
     "The hub's chip, shrunk to a badge with AI inside, leads the line: [AI] TRIALS → PEOPLE. The arrow stays plain; the chip says who does the connecting."),
]

SCRIPT = r'''<script>
(function(){
  var LH=15, EVAL='#6b3f8c', NS='http://www.w3.org/2000/svg';
  function el(n,attrs,txt){var e=document.createElementNS(NS,n);for(var k in attrs)e.setAttribute(k,attrs[k]);if(txt!=null)e.textContent=txt;return e;}
  /* Compose a direction line in place; returns its width. Children sit on a y=0 baseline;
     the group is translated to the row afterwards. */
  function compose(g){
    var st=g.dataset.style, from=g.dataset.from, to=g.dataset.to, anchor=g.dataset.anchor, x=+g.dataset.x, c=g.getAttribute('fill');
    while(g.firstChild)g.removeChild(g.firstChild);
    if(st==='chain'){
      var t=el('text',{x:x,y:0,'text-anchor':anchor});
      t.appendChild(el('tspan',{},from+' + '));t.appendChild(el('tspan',{fill:EVAL},'AI'));t.appendChild(el('tspan',{},' → '+to));
      g.appendChild(t);return t.getComputedTextLength();
    }
    if(st==='badge'){
      var BW=24, BH=14, PL=2.4, GAPB=7;
      var td=el('text',{y:0,'text-anchor':'start'},from+' → '+to); g.appendChild(td);
      var wd=td.getComputedTextLength(), Wb=PL+BW+PL+GAPB+wd;
      var x0= anchor==='start'? x : anchor==='end'? x-Wb : x-Wb/2;
      var bx=x0+PL, by=-BH+2.2;                       /* badge sits on the text baseline */
      [0.28,0.5,0.72].forEach(function(f){var px=bx+BW*f-0.8;
        g.appendChild(el('rect',{x:px,y:by-PL,width:1.6,height:PL,rx:.6,fill:EVAL,opacity:.55}));
        g.appendChild(el('rect',{x:px,y:by+BH,width:1.6,height:PL,rx:.6,fill:EVAL,opacity:.55}));});
      [0.32,0.68].forEach(function(f){var py=by+BH*f-0.8;
        g.appendChild(el('rect',{x:bx-PL,y:py,width:PL,height:1.6,rx:.6,fill:EVAL,opacity:.55}));
        g.appendChild(el('rect',{x:bx+BW,y:py,width:PL,height:1.6,rx:.6,fill:EVAL,opacity:.55}));});
      g.appendChild(el('rect',{x:bx,y:by,width:BW,height:BH,rx:3,fill:EVAL,opacity:.16}));
      g.appendChild(el('text',{x:bx+BW/2,y:by+BH-3.6,'text-anchor':'middle','font-family':'DM Serif Display, Georgia, serif','font-size':9.5,'font-weight':400,'letter-spacing':0,fill:EVAL},'AI'));
      td.setAttribute('x',(bx+BW+PL+GAPB).toFixed(1));
      return Wb;
    }
    var L=30, PAD=6;
    var tf=el('text',{y:0,'text-anchor':'start'},from), tt=el('text',{y:0,'text-anchor':'start'},to);
    g.appendChild(tf);g.appendChild(tt);
    var wf=tf.getComputedTextLength(), wt=tt.getComputedTextLength(), W=wf+PAD+L+PAD+wt;
    var xs= anchor==='start'? x : anchor==='end'? x-W : x-W/2;
    tf.setAttribute('x',xs.toFixed(1)); tt.setAttribute('x',(xs+wf+PAD+L+PAD).toFixed(1));
    var ax=xs+wf+PAD, ay=-3.8, mx=ax+L/2, col= st==='dot'? EVAL : c;
    g.appendChild(el('line',{x1:ax,y1:ay,x2:ax+L-5,y2:ay,stroke:col,'stroke-width':1.4}));
    g.appendChild(el('path',{d:'M'+(ax+L-6)+' '+(ay-3.2)+' L'+(ax+L)+' '+ay+' L'+(ax+L-6)+' '+(ay+3.2)+' Z',fill:col}));
    if(st==='dot'){g.appendChild(el('circle',{cx:mx-2,cy:ay,r:4.2,fill:EVAL}));}
    if(st==='above'){g.appendChild(el('text',{x:mx-2,y:ay-5.5,'text-anchor':'middle','font-size':8.5,fill:EVAL,'letter-spacing':'.04em'},'AI'));}
    if(st==='chip'){var s=9, cxp=mx-2, top=ay-6-s;
      [-2.6,2.6].forEach(function(o){
        g.appendChild(el('rect',{x:cxp+o-0.8,y:top-2.6,width:1.6,height:2.6,fill:EVAL,opacity:.7}));
        g.appendChild(el('rect',{x:cxp+o-0.8,y:top+s,width:1.6,height:2.6,fill:EVAL,opacity:.7}));
        g.appendChild(el('rect',{x:cxp-s/2-2.6,y:top+s/2+o-0.8,width:2.6,height:1.6,fill:EVAL,opacity:.7}));
        g.appendChild(el('rect',{x:cxp+s/2,y:top+s/2+o-0.8,width:2.6,height:1.6,fill:EVAL,opacity:.7}));});
      g.appendChild(el('rect',{x:cxp-s/2,y:top,width:s,height:s,rx:2,fill:EVAL,opacity:.9}));}
    return W;
  }
  function init(){ document.querySelectorAll('svg.cycle').forEach(function(svg){
    function clear(){svg.classList.remove('off');svg.querySelectorAll('.on').forEach(function(e){e.classList.remove('on')});}
    function light(p,to,from){clear();['.arc-'+p,'.ah-'+p+'-'+to,'.sp-'+p,'.ai','.node-'+to,'.node-'+from,'.dlab-'+p+'-'+to].forEach(function(sel){svg.querySelectorAll(sel).forEach(function(e){e.classList.add('on')});});svg.classList.add('off');}
    svg.querySelectorAll('.hit, .dlab').forEach(function(h){h.addEventListener('mouseenter',function(){light(h.dataset.pair,h.dataset.to,h.dataset.from)});h.addEventListener('mouseleave',clear);});
    function layout(){
      svg.querySelectorAll('.dlab').forEach(function(g){
        var dir=g.querySelector('.dir'), cap=g.querySelector('.cap'), note=g.querySelector('.note'), x=+g.dataset.x, y=+g.dataset.y;
        var isG=dir.tagName.toLowerCase()==='g';
        var maxW=isG?compose(dir):dir.getComputedTextLength();
        var words=cap.dataset.text.split(' '), lines=[]; cap.textContent='';
        var probe=el('tspan',{}); cap.appendChild(probe); function w(t){probe.textContent=t;return probe.getComputedTextLength()}
        if(words.length<2){lines=[words.join(' ')];}else{var best=null;for(var i=1;i<words.length;i++){var a=words.slice(0,i).join(' '),b=words.slice(i).join(' ');var m=Math.max(w(a),w(b));if(best===null||m<best.m)best={m:m,a:a,b:b};}lines=[best.a,best.b];}
        cap.removeChild(probe);
        var rows=1+lines.length+(note?1:0), hgt=LH*rows;
        var top= g.dataset.mode==='below'? y+4 : g.dataset.mode==='above'? y-hgt-2 : y-hgt/2;
        var yy=top+9;
        if(isG){dir.setAttribute('transform','translate(0 '+yy.toFixed(1)+')');}else{dir.setAttribute('y',yy.toFixed(1));}
        lines.forEach(function(l,i){cap.appendChild(el('tspan',{x:x,y:(yy+LH*(i+1)).toFixed(1)},l));});
        if(note)note.setAttribute('y',(yy+LH*(lines.length+1)).toFixed(1));
        g.dataset.titlew=Math.round(maxW);
      });
    }
    if(document.fonts&&document.fonts.ready){document.fonts.ready.then(layout);} layout();
  }); }
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',init);}else{init();}
})();
</script>'''


FONTS = ('<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;'
         '0,9..40,600;1,9..40,400&family=DM+Serif+Display:ital@0;1&display=swap" rel="stylesheet">')
ANALYTICS = ("<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
             "data-cf-beacon='{\"token\": \"7e881bced2fd414ca3b32881bd2ea36e\"}'></script>")
PAGE_CSS = """    html, body { margin: 0; background: #fff; color: #222; font-family: "DM Sans", -apple-system, BlinkMacSystemFont, sans-serif; }
    .stage { max-width: 760px; margin: 0 auto; padding: 40px 20px 48px; }
    .stage svg { width: 100%; height: auto; display: block; }
    svg.cycle .unit { transition: opacity .22s, stroke .22s, fill .22s; }
    svg.cycle.off > .unit:not(.on) { opacity: .22; }
    svg.cycle .arc.on { stroke-width: 2.6; }
    svg.cycle .dlab.on .cap { fill: #222; }
    svg.cycle .dlab.muted { opacity: .5; }
    svg.cycle .dlab.muted.on { opacity: 1; }
    svg.cycle .hit { fill: none; stroke: transparent; stroke-width: 28; pointer-events: stroke; cursor: pointer; }"""


def write_page(key='q1'):
    """future.html: the figure alone on a white page. Unlinked and noindex until he says otherwise."""
    parts = ['<!DOCTYPE html>', '<html lang="en">', '<head>',
             '  <meta charset="UTF-8">',
             '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '  <title>Qiao Jin — Future Directions</title>',
             '  <meta name="robots" content="noindex">',
             '  <link rel="preconnect" href="https://fonts.googleapis.com">',
             '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
             '  ' + FONTS,
             '  <style>', PAGE_CSS, '  </style>',
             '</head>', '<body>', '  <main class="stage">', cycle(key), '  </main>',
             SCRIPT, ANALYTICS, '</body>', '</html>', '']
    out = os.path.join(REPO, 'future.html')
    open(out, 'w').write('\n'.join(parts))
    print(f'wrote {os.path.relpath(out, REPO)} ({key})')


def main():
    h = open(PAGE).read()
    sections = ''.join(
        f'<section class="sec" id="prop-{k}"><div class="wrap"><div class="kick">Proposal {i + 1}</div><h2>{t}</h2>'
        f'<p class="why">{d}</p><div class="stage">{cycle(k)}</div></div></section>\n'
        for i, (k, t, d) in enumerate(PROPOSALS))
    h = re.sub(r'<section class="sec" id="prop-[a-z0-9]+">.*?</section>\s*', '', h, flags=re.S)
    h, n = re.subn(r'<script>\n\(function\(\)\{\n  var LH=15.*?</script>', lambda m: SCRIPT, h, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('shared figure script not found — page layout changed')
    first = h.index('<section class="sec"')
    h = h[:first] + sections + h[first:]
    open(PAGE, 'w').write(h)
    print(f'wrote {len(PROPOSALS)} proposals into {os.path.relpath(PAGE, REPO)}')
    write_page('q1')


if __name__ == '__main__':
    main()
