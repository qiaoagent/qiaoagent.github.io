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
TINT = {GEN: '#dcf5e6', UTIL: '#dbeaff', GOLD: '#fff0c8'}   # light but clearly green / blue / yellow tints behind the nodes
CX, CY, R = 300, 268, 150          # ring centre and radius
GAP = 24                            # degrees between a node and the nearest arrowhead
START = 54                          # spokes begin this far from the centre (clear of the chip pins)
H, PIN_L, PIN_W, PINS = 32, 10, 4, (-20, 0, 20)
INSET = 19                          # code beads sit this far inside the ring


def set_ring(r):
    """Set the ring radius and everything derived from it (labels, beads, spacing)."""
    global R, LABR, BR, SPREAD, NUDGE, BEAD_FS, P
    R = r
    LABR = R + 24
    BR = max(11, round(R * 0.09))       # bead radius scales with the ring (14 at R=150, 12 at R=130)
    rb = R - INSET
    SPREAD = math.degrees(2 * math.asin((2 * BR + 4) / (2 * rb)))            # pair spacing: a 4px gap between beads
    theta_min = math.degrees(math.asin((BR + 8) / rb))                       # inner bead >= 8px from the spoke
    NUDGE = max(0.0, theta_min + SPREAD / 2 - (90 - 2 * 30) / 2 - (30 - GAP)) # shift a pair away from the joint if needed
    BEAD_FS = round(BR * 0.75, 1)
    P = lambda a, rr=None: (CX + (R if rr is None else rr) * math.cos(rad(a)), CY + (R if rr is None else rr) * math.sin(rad(a)))


set_ring(R)

rad = math.radians

NAME = {'people': 'PEOPLE', 'trials': 'TRIALS', 'evidence': 'EVIDENCE'}
# pairs are named by content: tp = Trials-People, ep = Evidence-People, te = Trials-Evidence
CAP = {('tp', 'people'): 'Matching clinical trials to patients',
       ('tp', 'trials'): 'Matching patients to clinical trials',
       ('ep', 'people'): 'Meeting real-world user|information needs',
       ('ep', 'evidence'): 'Evaluating if and how AI helps people in practice',
       ('te', 'evidence'): 'Agent-enabled living evidence systems',
       ('te', 'trials'): 'Evidence gaps inform future trials'}
CODE = {('tp', 'people'): ['A.1'], ('tp', 'trials'): ['A.1'], ('ep', 'people'): ['B.1', 'B.2'],
        ('ep', 'evidence'): ['C'], ('te', 'evidence'): ['A.2'], ('te', 'trials'): []}
# Layouts: People is always at the top (-90). 'orig' puts Trials lower left (150) with the
# pill rising to the right; 'swap' moves Trials to the lower right so its tilt runs with the
# arc; 'flip' keeps the places and mirrors the pill instead.
EV_DX, EV_DY = 13, -6   # nudge the pyramid up and right so both arrowheads sit at similar distances
LAYOUTS = {'orig': {'trials': 150, 'evidence': 30, 'pill': -35},
           'swap': {'trials': 30, 'evidence': 150, 'pill': -35},
           'flip': {'trials': 150, 'evidence': 30, 'pill': 45}}   # leans with the ring (tangent there is 60)
COLOUR = {'tp': GOLD, 'ep': UTIL, 'te': GEN}


def pairs_for(layout):
    """(id, node at the start angle, node at the end angle, start, end, joint, colour) — clockwise from People."""
    L = LAYOUTS[layout]
    right = 'trials' if L['trials'] == 30 else 'evidence'
    left = 'evidence' if right == 'trials' else 'trials'

    def pid(a, b):
        return {frozenset(['trials', 'people']): 'tp', frozenset(['evidence', 'people']): 'ep',
                frozenset(['trials', 'evidence']): 'te'}[frozenset([a, b])]
    return [(pid('people', right), 'people', right, -90 + GAP, 30 - GAP, -30, COLOUR[pid('people', right)]),
            (pid(right, left), right, left, 30 + GAP, 150 - GAP, 90, COLOUR[pid(right, left)]),
            (pid(left, 'people'), left, 'people', 150 + GAP, 270 - GAP, 210, COLOUR[pid(left, 'people')])]
TITLE = 'Connecting people, clinical trials and evidence through trustworthy AI'
# future.html only: one two-way label for the Trials-People arc; the People->Trials label is dropped.
# 'dir' is rendered verbatim (AI in purple); 'lines' fixes the caption break; 'also' makes the label
# light up when either half of the arc is hovered.
OVERRIDES = {('tp', 'people'): {'dir': 'TRIALS \u2190 AI \u2192 PEOPLE',
                                'lines': ('Workflow-integrated AI for', 'clinical trial recruitment'),
                                'also': ('tp', 'trials')},
             ('tp', 'trials'): None}


def solid(hex_colour, alpha):
    """The colour a translucent fill would show on white — as an opaque hex, so icons stay solid over shading."""
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    mix = lambda v: round(v * alpha + 255 * (1 - alpha))
    return '#%02x%02x%02x' % (mix(r), mix(g), mix(b))


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
              f'{60 + wb / 2:.1f},{yy + h:.1f} {60 - wb / 2:.1f},{yy + h:.1f}" fill="{solid(GEN, 0.94 - i * 0.13)}"/>')
    return f'<g transform="translate({x - 60 * scale:.1f} {y - 46 * scale:.1f}) scale({scale})">{s}</g>'


def person_g(x, y, c=UTIL):
    return (f'<g transform="translate({x:.1f} {y:.1f})"><circle cx="0" cy="-14" r="13" fill="{solid(c, 0.94)}"/>'
            f'<path d="M-24 34 Q-24 4 0 4 Q24 4 24 34 Z" fill="{solid(c, 0.62)}"/></g>')


PILL_SCALE = 0.8


def pill_g(x, y, c=GOLD, rot=-35):
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot}) scale({PILL_SCALE})">'
            f'<path d="M-30 -13 H0 V13 H-30 A13 13 0 0 1 -30 -13 Z" fill="{solid(c, 0.94)}"/>'
            f'<path d="M0 -13 H30 A13 13 0 0 1 30 13 H0 Z" fill="{solid(c, 0.55)}"/></g>')


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


def dlabel(style, pair, frm, to, mid, c, codes=True, big=False, stack=False, overrides=False):
    dir_fs, cap_fs = (13, 15) if big else (11, 13)
    stack_attr = ' data-stack="1"' if stack else ''
    ov = OVERRIDES.get((pair, to), False) if overrides else False
    if ov is None:
        return ''                                   # this half carries no label
    extra_cls = (' dlab-%s-%s' % ov['also']) if ov and ov.get('also') else ''
    custom_attr = (' data-custom="%s"' % ov['dir']) if ov and ov.get('dir') else ''
    base = CAP[(pair, to)]
    if ov and ov.get('lines'):
        lines_attr, cap_text = ' data-lines="%s"' % '|'.join(ov['lines']), ' '.join(ov['lines'])
    elif '|' in base:
        lines_attr, cap_text = ' data-lines="%s"' % base, base.replace('|', ' ')
    else:
        lines_attr, cap_text = '', base
    x, y = P(mid, LABR)
    sn = math.sin(rad(mid))
    mode = 'below' if sn > 0.5 else ('above' if sn < -0.5 else 'side')
    a = mid % 360
    anchor = 'start' if (a < 90 or a > 270) else 'end'
    muted = ' muted' if (codes and not CODE[(pair, to)]) else ''
    # an uncoded half carries only a light caption: no direction line, no code bead
    dirline = '' if muted else (
        f'<g class="dir" data-style="{style}" data-anchor="{anchor}" data-from="{NAME[frm]}" data-to="{NAME[to]}" '
        f'data-x="{x:.0f}"{stack_attr} fill="{c}" font-size="{dir_fs}" font-weight="700" letter-spacing=".08em"></g>')
    dirline = dirline.replace('<g class="dir" ', '<g class="dir"' + custom_attr + ' ', 1) if dirline else dirline
    return (f'<g class="unit dlab dlab-{pair}-{to}{extra_cls}{muted}" data-pair="{pair}" data-to="{to}" data-from="{frm}" '
            f'data-mode="{mode}" data-x="{x:.0f}" data-y="{y:.0f}" style="--c:{c};cursor:pointer">{dirline}'
            f'<text class="cap" x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{cap_fs}" fill="{MUTED}" '
            f'data-text="{cap_text}"{lines_attr}></text></g>')


CODE_OVERRIDES = {('ep', 'people'): ['B']}     # future.html: one bead for both B projects


def bead(pair, to, mid, c, away, overrides=False):
    codes = CODE_OVERRIDES.get((pair, to), CODE[(pair, to)]) if overrides else CODE[(pair, to)]
    n = len(codes)
    centre = mid + (away * NUDGE if n > 1 else 0)
    out = ''
    for i, cd in enumerate(codes):
        a = centre + (i - (n - 1) / 2) * SPREAD
        bx, by = P(a, R - INSET)
        out += (f'<g class="unit dlab-{pair}-{to}"><circle cx="{bx:.1f}" cy="{by:.1f}" r="{BR}" fill="{c}"/>'
                f'<text x="{bx:.1f}" y="{by + 3.8:.1f}" text-anchor="middle" font-size="{BEAD_FS}" font-weight="700" fill="#fff">{cd}</text></g>')
    return out


def shading(layout):
    """Three faint wedges behind the nodes, each blending its two neighbouring arc colours,
    fading toward the centre so the chip stays clean."""
    L = LAYOUTS[layout]
    right = 'trials' if L['trials'] == 30 else 'evidence'
    pairs = {(a, b): c for a, x, y, _1, _2, _3, c in pairs_for(layout) for (a, b) in ((x, y), (y, x))}
    # wedge for the node at angle `at` spans the 120 degrees between its two joints
    left = 'evidence' if right == 'trials' else 'trials'
    wedges = [('people', -90, pairs[('people', left)], pairs[('people', right)]),
              (right, 30, pairs[(right, 'people')], pairs[(right, left)]),
              (left, 150, pairs[(left, right)], pairs[(left, 'people')])]
    defs, body = '', ''
    for name, at, c1, c2 in wedges:
        a1, a2 = at - 60, at + 60
        x1, y1 = P(a1)
        x2, y2 = P(a2)
        defs += (f'<linearGradient id="wg-{name}" gradientUnits="userSpaceOnUse" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}">'
                 f'<stop offset="0" stop-color="{TINT[c1]}"/><stop offset="1" stop-color="{TINT[c2]}"/></linearGradient>')
        body += (f'<path class="wedge" d="M{CX} {CY} L{x1:.1f} {y1:.1f} A{R} {R} 0 0 1 {x2:.1f} {y2:.1f} Z" '
                 f'fill="url(#wg-{name})" mask="url(#wfade)"/>')
    defs += (f'<radialGradient id="wfg" gradientUnits="userSpaceOnUse" cx="{CX}" cy="{CY}" r="{R}">'
             f'<stop offset="0.3" stop-color="#000"/><stop offset="1" stop-color="#fff"/></radialGradient>'
             f'<mask id="wfade"><circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#wfg)"/></mask>')
    return f'<defs>{defs}</defs>{body}'


def cycle(key, layout='orig', codes=True, title=True, big=False, stack=False, overrides=False, shade=False):
    style = STYLE[key]
    L = LAYOUTS[layout]
    arcs = heads = hits = spokes = dlabs = beads = ''
    eps = math.degrees(7 / R)
    for pid, n1, n2, a1, a2, mid, c in pairs_for(layout):
        arcs += (f'<path class="unit arc arc-{pid}" style="--c:{c}" d="{arcpath(a1 + eps, a2 - eps)}" '
                 f'fill="none" stroke="{c}" stroke-width="2"/>')
        heads += head(a1, -1, f'ah ah-{pid}-{n1}', c) + head(a2, +1, f'ah ah-{pid}-{n2}', c)
        spokes += spoke_unit(pid, mid, c)
        hits += (f'<path class="hit" data-pair="{pid}" data-to="{n1}" data-from="{n2}" d="{arcpath(a1, mid)}"/>'
                 f'<path class="hit" data-pair="{pid}" data-to="{n2}" data-from="{n1}" d="{arcpath(mid, a2)}"/>')
        dlabs += dlabel(style, pid, n2, n1, (a1 + mid) / 2, c, codes, big, stack, overrides) + dlabel(style, pid, n1, n2, (mid + a2) / 2, c, codes, big, stack, overrides)
        if codes:
            beads += bead(pid, n1, (a1 + mid) / 2, c, -1, overrides) + bead(pid, n2, (mid + a2) / 2, c, +1, overrides)
    pins = ''
    for o in PINS:
        pins += (f'<rect x="{CX + o - PIN_W / 2:.1f}" y="{CY - H - PIN_L}" width="{PIN_W}" height="{PIN_L}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX + o - PIN_W / 2:.1f}" y="{CY + H}" width="{PIN_W}" height="{PIN_L}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX - H - PIN_L}" y="{CY + o - PIN_W / 2:.1f}" width="{PIN_L}" height="{PIN_W}" rx="2" fill="{EVAL}" opacity=".5"/>'
                 f'<rect x="{CX + H}" y="{CY + o - PIN_W / 2:.1f}" width="{PIN_L}" height="{PIN_W}" rx="2" fill="{EVAL}" opacity=".5"/>')
    px, py = P(-90)
    tx, ty = P(L['trials'])
    ex, ey = P(L['evidence'])
    t_right = L['trials'] == 30
    flipped = L['pill'] > 0                          # a pill leaning with the ring reaches down toward its label
    t_lab_dx, t_lab_dy = (10, 0) if flipped else (0, 0)   # same baseline as Evidence; clear of the low end-cap sideways

    def node_name(x, y, t, anchor='middle'):
        return (f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-family="DM Serif Display, Georgia, serif" '
                f'font-size="21" fill="currentColor">{t}</text>')

    mx, my = (230, 96) if big else (190, 78)
    lh, rows = (18, 4) if (big and stack) else ((18, 3) if big else (15, 3))
    bottom = 24 + 4 + rows * lh + 12 + (60 if title else 0)      # room for the labels below the ring (+ the in-figure title)
    vx, vy, vw, vh = CX - R - mx, CY - R - my, 2 * R + 2 * mx, 2 * R + my + bottom
    title_y = CY + R + 120
    title_svg = (f'<text class="figtitle" x="{CX}" y="{title_y}" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" '
                 f'font-size="17" fill="#222">{TITLE}</text>') if title else ''
    shade_svg = shading(layout) if shade else ''
    return f'''<svg class="cycle" id="cycle-{key}-{layout}" data-lh="{18 if big else 15}" viewBox="{vx} {vy} {vw} {vh}" xmlns="http://www.w3.org/2000/svg" font-family="DM Sans, sans-serif">
{shade_svg}{arcs}{heads}{spokes}{beads}
<g class="unit ai"><g class="chip">{pins}<rect x="{CX - H}" y="{CY - H}" width="{2 * H}" height="{2 * H}" rx="9" fill="{EVAL}" opacity=".16"/><rect x="{CX - H + 9}" y="{CY - H + 9}" width="{2 * H - 18}" height="{2 * H - 18}" rx="5" fill="{EVAL}" opacity=".10"/></g>
<text x="{CX}" y="{CY + 10}" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="30" fill="{EVAL}">AI</text></g>
<g class="unit node node-people">{person_g(px, py)}{node_name(px, py - 46, 'People')}</g>
<g class="unit node node-trials">{pill_g(tx + (2 if t_right else -2), ty, rot=L['pill'])}{node_name(tx + (20 if t_right else -20) + (0 if t_right else -t_lab_dx), ty + 58 + t_lab_dy, 'Trials', 'start' if t_right else 'end')}</g>
<g class="unit node node-evidence">{pyramid_g(ex + EV_DX, ey + 4 + EV_DY)}{node_name(ex + (-20 if t_right else 20) + EV_DX, ey + 58, 'Evidence', 'end' if t_right else 'start')}</g>
{hits}
{dlabs}
{title_svg}
</svg>'''


STYLE = {'q1': 'chain', 'q2': 'above', 'q3': 'dot', 'q4': 'chip', 'q5': 'badge'}   # proposal key -> compose() style
PROPOSALS = [
    ("orig", "Current layout", "Trials lower left with the pill rising to the right — its tilt runs against the arc there."),
    ("swap", "Swap the places", "Trials moves to the lower right; the pill's tilt now runs with its arc. Pairs, codes and captions travel with the nodes."),
    ("flip", "Flip the pill", "Places unchanged; the pill is mirrored so it falls to the right, matching the left-hand arc."),
]

SCRIPT = r'''<script>
(function(){
  var EVAL='#6b3f8c', NS='http://www.w3.org/2000/svg';
  function el(n,attrs,txt){var e=document.createElementNS(NS,n);for(var k in attrs)e.setAttribute(k,attrs[k]);if(txt!=null)e.textContent=txt;return e;}
  /* Compose a direction line in place; returns its width. Children sit on a y=0 baseline;
     the group is translated to the row afterwards. */
  function compose(g){
    var st=g.dataset.style, from=g.dataset.from, to=g.dataset.to, anchor=g.dataset.anchor, x=+g.dataset.x, c=g.getAttribute('fill');
    while(g.firstChild)g.removeChild(g.firstChild);
    if(g.dataset.custom){
      var tc=el('text',{x:x,y:0,'text-anchor':anchor});
      g.dataset.custom.split(/(AI)/).forEach(function(part){if(!part)return;tc.appendChild(el('tspan',part==='AI'?{fill:EVAL}:{},part));});
      g.appendChild(tc);return tc.getComputedTextLength();
    }
    if(st==='chain'){
      if(g.dataset.stack){
        var LHs=+(g.ownerSVGElement.dataset.lh||15);
        var t1=el('text',{x:x,y:0,'text-anchor':anchor}), t2=el('text',{x:x,y:LHs,'text-anchor':anchor});
        t1.appendChild(el('tspan',{},from+' + '));t1.appendChild(el('tspan',{fill:EVAL},'AI'));
        t2.textContent='→ '+to;
        g.appendChild(t1);g.appendChild(t2);g.dataset.rows=2;
        return Math.max(t1.getComputedTextLength(),t2.getComputedTextLength());
      }
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
      var LH=+(svg.dataset.lh||15);
      svg.querySelectorAll('.dlab').forEach(function(g){
        var dir=g.querySelector('.dir'), cap=g.querySelector('.cap'), note=g.querySelector('.note'), x=+g.dataset.x, y=+g.dataset.y;
        var isG=!!dir&&dir.tagName.toLowerCase()==='g';
        var maxW=dir?(isG?compose(dir):dir.getComputedTextLength()):0;
        var words=cap.dataset.text.split(' '), lines=[]; cap.textContent='';
        var probe=el('tspan',{}); cap.appendChild(probe); function w(t){probe.textContent=t;return probe.getComputedTextLength()}
        if(cap.dataset.lines){lines=cap.dataset.lines.split('|');}
        else if(words.length<2){lines=[words.join(' ')];}else{var best=null;for(var i=1;i<words.length;i++){var a=words.slice(0,i).join(' '),b=words.slice(i).join(' ');var m=Math.max(w(a),w(b));if(best===null||m<best.m)best={m:m,a:a,b:b};}lines=[best.a,best.b];}
        cap.removeChild(probe);
        var titleRows=dir?(+(dir.dataset.rows)||1):0;
        var rows=titleRows+lines.length+(note?1:0), hgt=LH*rows;
        var top= g.dataset.mode==='below'? y+4 : g.dataset.mode==='above'? y-hgt-2 : y-hgt/2;
        var yy=top+9, off=titleRows;
        if(dir){ if(isG){dir.setAttribute('transform','translate(0 '+yy.toFixed(1)+')');}else{dir.setAttribute('y',yy.toFixed(1));} }
        lines.forEach(function(l,i){cap.appendChild(el('tspan',{x:x,y:(yy+LH*(i+off)).toFixed(1)},l));});
        if(note)note.setAttribute('y',(yy+LH*(lines.length+1)).toFixed(1));
        g.dataset.titlew=Math.round(maxW);
      });
    }
    svg.addEventListener('relayout',layout);
    if(document.fonts&&document.fonts.ready){document.fonts.ready.then(layout);} layout();
  }); }
  window.FutureFigureLayout=function(){document.querySelectorAll('svg.cycle').forEach(function(svg){svg.dispatchEvent(new Event('relayout'));});};
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
    svg.cycle .hit { fill: none; stroke: transparent; stroke-width: 28; pointer-events: stroke; cursor: pointer; }
    .vision-line { font-family: "DM Serif Display", Georgia, serif; font-size: 1.05rem; line-height: 1.45; text-align: center; margin: 14px auto 0; max-width: 560px; }"""


def write_page(key='q1', layout='orig', ring=150):
    """future.html: the figure alone on a white page. Unlinked and noindex until he says otherwise."""
    set_ring(ring)
    parts = ['<!DOCTYPE html>', '<html lang="en">', '<head>',
             '  <meta charset="UTF-8">',
             '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
             '  <title>Qiao Jin — Future Directions</title>',
             '  <meta name="robots" content="noindex">',
             '  <link rel="preconnect" href="https://fonts.googleapis.com">',
             '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
             '  ' + FONTS,
             '  <style>', PAGE_CSS, '  </style>',
             '</head>', '<body>', '  <main class="stage">', cycle(key, layout, title=False, big=True, stack=False, overrides=True, shade=True),
             '    <p class="vision-line">' + VISION + '</p>', '  </main>',
             SCRIPT, ANALYTICS, '</body>', '</html>', '']
    out = os.path.join(REPO, 'future.html')
    open(out, 'w').write('\n'.join(parts))
    set_ring(150)
    print(f'wrote {os.path.relpath(out, REPO)} ({key}, {layout}, r={ring})')


INDEX = os.path.join(REPO, 'index.html')


def mini():
    """Abstract emblem for the homepage sidebar: ring, chip, icons and names only."""
    cx, cy, r, gap, start = 100, 104, 62, 24, 24
    h, pin_l, pin_w, pins = 13, 4, 1.8, (-8, 0, 8)
    Pm = lambda a, rr=r: (cx + rr * math.cos(rad(a)), cy + rr * math.sin(rad(a)))
    L = LAYOUTS['flip']

    def fil(theta, c, hh=9, delta=10):
        t = rad(theta)
        ux, uy = math.cos(t), math.sin(t)
        m = Pm(theta)
        a = (m[0] - hh * ux, m[1] - hh * uy)

        def side(sign):
            b = rad(theta + sign * delta)
            bp = (cx + r * math.cos(b), cy + r * math.sin(b))
            tx, ty = -math.sin(b), math.cos(b)
            det = ux * (-ty) - uy * (-tx)
            sc = ((bp[0] - a[0]) * (-ty) - (bp[1] - a[1]) * (-tx)) / det
            return bp, (a[0] + sc * ux, a[1] + sc * uy)
        b1, c1 = side(-1)
        b2, c2 = side(+1)
        return (f'<path d="M{a[0]:.1f} {a[1]:.1f} Q{c1[0]:.1f} {c1[1]:.1f} {b1[0]:.1f} {b1[1]:.1f} A{r} {r} 0 0 1 '
                f'{b2[0]:.1f} {b2[1]:.1f} Q{c2[0]:.1f} {c2[1]:.1f} {a[0]:.1f} {a[1]:.1f} Z" fill="{c}"/>')

    def hd(a, sign, c):
        tx, ty = -math.sin(rad(a)) * sign, math.cos(rad(a)) * sign
        nx, ny = -ty, tx
        t = Pm(a)
        b = (t[0] - 4 * tx, t[1] - 4 * ty)
        return (f'<path d="M{t[0]:.1f} {t[1]:.1f} L{b[0] + 2 * nx:.1f} {b[1] + 2 * ny:.1f} '
                f'L{b[0] - 2 * nx:.1f} {b[1] - 2 * ny:.1f} Z" fill="{c}"/>')
    eps = math.degrees(4 / r)
    out = ''
    for pid, n1, n2, a1, a2, mid, c in pairs_for('flip'):
        x1, y1 = Pm(a1 + eps)
        x2, y2 = Pm(a2 - eps)
        out += f'<path d="M{x1:.1f} {y1:.1f} A{r} {r} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" stroke="{c}" stroke-width="1.3"/>'
        out += hd(a1, -1, c) + hd(a2, +1, c)
        s0, m0 = Pm(mid, start), Pm(mid)
        out += f'<path d="M{s0[0]:.1f} {s0[1]:.1f} L{m0[0]:.1f} {m0[1]:.1f}" fill="none" stroke="{c}" stroke-width="1.3"/>' + fil(mid, c)
    for o in pins:
        out += (f'<rect x="{cx + o - pin_w / 2:.1f}" y="{cy - h - pin_l}" width="{pin_w}" height="{pin_l}" rx="0.8" fill="{EVAL}" opacity=".5"/>'
                f'<rect x="{cx + o - pin_w / 2:.1f}" y="{cy + h}" width="{pin_w}" height="{pin_l}" rx="0.8" fill="{EVAL}" opacity=".5"/>'
                f'<rect x="{cx - h - pin_l}" y="{cy + o - pin_w / 2:.1f}" width="{pin_l}" height="{pin_w}" rx="0.8" fill="{EVAL}" opacity=".5"/>'
                f'<rect x="{cx + h}" y="{cy + o - pin_w / 2:.1f}" width="{pin_l}" height="{pin_w}" rx="0.8" fill="{EVAL}" opacity=".5"/>')
    out += (f'<rect x="{cx - h}" y="{cy - h}" width="{2 * h}" height="{2 * h}" rx="4" fill="{EVAL}" opacity=".16"/>'
            f'<rect x="{cx - h + 4}" y="{cy - h + 4}" width="{2 * h - 8}" height="{2 * h - 8}" rx="2.5" fill="{EVAL}" opacity=".10"/>'
            f'<text class="ai-text" x="{cx}" y="{cy + 4.5}" text-anchor="middle" font-family="DM Serif Display, Georgia, serif" font-size="13" fill="{EVAL}">AI</text>')
    px, py = Pm(-90)
    tx, ty = Pm(L['trials'])
    ex, ey = Pm(L['evidence'])
    k = 0.42
    nm = lambda x, y, t, anchor='middle': (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-family="DM Serif Display, Georgia, serif" '
                                          f'font-size="10" fill="currentColor">{t}</text>')
    out += f'<g transform="translate({px:.1f} {py + 2:.1f}) scale({k})">{person_g(0, 0)}</g>' + nm(px, py - 17, 'People')
    out += f'<g transform="translate({tx:.1f} {ty:.1f}) scale({k})">{pill_g(0, 0, rot=L["pill"])}</g>' + nm(tx - 4, ty + 22, 'Trials')
    out += f'<g transform="translate({ex:.1f} {ey + 1:.1f}) scale({k})">{pyramid_g(0, 0)}</g>' + nm(ex + 4, ey + 22, 'Evidence')
    return (f'<svg class="future-mini" viewBox="14 18 172 172" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="People, clinical trials and evidence connected through AI">{out}</svg>')


def inject_home():
    """Place the emblem in index.html between its markers (added once, then replaced on every run)."""
    h = open(INDEX).read()
    block = '<!-- future-mini -->\n          <div class="side-fig">' + mini() + '</div>\n          <!-- /future-mini -->'
    if '<!-- future-mini -->' in h:
        h = re.sub(r'<!-- future-mini -->.*?<!-- /future-mini -->', lambda m: block, h, count=1, flags=re.S)
    else:
        anchor = '          <hr class="sidebar-rule">\n          <ul class="editorial-list">'
        if h.count(anchor) != 1:
            raise SystemExit('sidebar anchor not found in index.html')
        h = h.replace(anchor, '          ' + block + '\n' + anchor, 1)
    open(INDEX, 'w').write(h)
    print('placed the emblem in index.html')


VISION = ('Building an open infrastructure that connects evolving medical evidence, '
          'real-world information needs, and trustworthy AI agents.')


def inject_vision_tab():
    """Research Vision tab on the homepage: the figure without project codes, the vision line beneath."""
    h = open(INDEX).read()
    svg = cycle('q1', 'flip', codes=False, title=False, shade=True)
    panel = ('<!-- vision-panel -->\n        <div class="deck-view" id="view-vision">\n          <div class="vision-wrap">\n'
             + svg + '\n            <p class="vision-line">' + VISION + '</p>\n          </div>\n        </div>\n        <!-- /vision-panel -->')
    if '<!-- vision-panel -->' in h:
        h = re.sub(r'<!-- vision-panel -->.*?<!-- /vision-panel -->', lambda m: panel, h, count=1, flags=re.S)
    else:
        i = h.index('id="view-areas"')
        j = h.index('</section>', i)
        h = h[:j] + panel + '\n      ' + h[j:]
    btn = ('<span class="ds-sep" aria-hidden="true">/</span>\n            '
           '<button type="button" class="ds-btn" data-view="vision" role="tab" aria-selected="false">Vision</button>')
    if 'data-view="vision"' not in h:
        anchor = '<button type="button" class="ds-btn" data-view="areas" role="tab" aria-selected="false">Research Areas</button>'
        assert h.count(anchor) == 1
        h = h.replace(anchor, anchor + '\n            ' + btn, 1)
    old_views = "    var views = { papers: document.getElementById('view-papers'),\n                  areas:  document.getElementById('view-areas') };"
    new_views = ("    var views = { papers: document.getElementById('view-papers'),\n                  areas:  document.getElementById('view-areas'),\n"
                 "                  vision: document.getElementById('view-vision') };")
    if 'vision: document.getElementById' not in h:
        assert h.count(old_views) == 1
        h = h.replace(old_views, new_views, 1)
    hook = "        if (v === 'vision' && window.FutureFigureLayout) window.FutureFigureLayout();   /* text can't be measured while hidden */\n"
    if 'FutureFigureLayout' not in h:
        anchor2 = "        if (v === 'areas') armTilt();\n"
        assert h.count(anchor2) == 1
        h = h.replace(anchor2, anchor2 + hook, 1)
    if '<!-- vision-script -->' in h:
        h = re.sub(r'<!-- vision-script -->.*?<!-- /vision-script -->', lambda m: '<!-- vision-script -->\n' + SCRIPT + '\n<!-- /vision-script -->', h, count=1, flags=re.S)
    else:
        anchor3 = '<script src="assets/direction-figures.js?v=1"></script>'
        assert h.count(anchor3) == 1
        h = h.replace(anchor3, anchor3 + '\n<!-- vision-script -->\n' + SCRIPT + '\n<!-- /vision-script -->', 1)
    open(INDEX, 'w').write(h)
    print('placed the Research Vision tab in index.html')


def main():
    h = open(PAGE).read()
    sections = ''.join(
        f'<section class="sec" id="prop-{k}"><div class="wrap"><div class="kick">Layout {i + 1}</div><h2>{t}</h2>'
        f'<p class="why">{d}</p><div class="stage">{cycle("q1", k)}</div></div></section>\n'
        for i, (k, t, d) in enumerate(PROPOSALS))
    h = re.sub(r'<section class="sec" id="prop-[a-z0-9]+">.*?</section>\s*', '', h, flags=re.S)
    h, n = re.subn(r'<script>\n\(function\(\)\{\n  var (?:LH=15|EVAL=).*?</script>', lambda m: SCRIPT, h, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('shared figure script not found — page layout changed')
    first = h.index('<section class="sec"')
    h = h[:first] + sections + h[first:]
    open(PAGE, 'w').write(h)
    print(f'wrote {len(PROPOSALS)} layouts into {os.path.relpath(PAGE, REPO)}')
    write_page('q1', 'flip', ring=130)
    # inject_home() is kept for reference but not run: he decided against the homepage emblem (2026-09-13)
    inject_vision_tab()


if __name__ == '__main__':
    main()
