/* Shared "AI for Evidence Utilization" — Retrieve → Summarize → Verify loop.
   Single source of truth: rendered inline (full interactive figure, not a link) into any
   page that has <div id="ep3-mount"></div> + <script src="/assets/ep3-rsv-loop.js"></script>.
   Used by research.html and paper/RSV.html. Edit here → both update.
   Asset URLs are root-absolute (/assets/…) so covers/PDFs resolve from / and from /paper/. */
(function () {
  var CSS = `
  .ep3-grid { display: grid; grid-template-columns: 202px 1fr 322px; gap: 30px; align-items: center; margin-top: 22px; }
  .ep3-center { display: flex; justify-content: center; }
  .ep3-svg { width: 100%; max-width: 468px; height: auto; display: block; margin: 0 auto; }
  .ep3-cap { font-size: 14px; font-style: italic; fill: var(--muted); }
  .ep3-pill-t { font-size: 16px; font-weight: 600; fill: var(--util); }
  .ep3-left { display: flex; flex-direction: column; gap: 20px; }
  .ep3-persp { display: flex; gap: 11px; align-items: center; text-decoration: none; padding: 10px 11px; border: 1px solid var(--border); border-radius: 9px; background: var(--panel); }
  .ep3-persp img { width: 52px; height: auto; border: 1px solid var(--border); border-radius: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.12); flex-shrink: 0; }
  .ep3-persp .pl { font-size: 0.58rem; font-weight: 700; letter-spacing: 0.07em; text-transform: uppercase; color: var(--util); margin-bottom: 3px; }
  .ep3-persp .pn { font-family: "DM Serif Display", Georgia, serif; font-size: 0.92rem; color: var(--ink); line-height: 1.12; }
  .ep3-persp .pv { font-size: 0.68rem; color: var(--muted); font-style: italic; margin-top: 2px; }
  .ep3-stage .st { font-family: "DM Serif Display", Georgia, serif; font-size: 1.05rem; color: var(--util); margin-bottom: 3px; }
  .ep3-stage p { font-size: 0.83rem; color: var(--muted); line-height: 1.5; margin: 0; }
  .ep3-right { display: flex; flex-direction: column; gap: 13px; }
  .ep3-pgroup { display: grid; grid-template-columns: 1fr 1fr; column-gap: 14px; row-gap: 11px; align-items: center; }
  .ep3-pgroup .glabel { grid-column: 1 / -1; font-size: 0.62rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: var(--util); margin-bottom: -5px; }
  .ep3-paper { display: flex; gap: 9px; align-items: center; text-decoration: none; }
  .ep3-paper img { width: 51px; height: auto; border: 1px solid var(--border); border-radius: 3px; box-shadow: 0 2px 6px rgba(0,0,0,0.12); flex-shrink: 0; }
  .ep3-paper .d-role { font-size: 0.6rem; font-weight: 600; color: var(--util); line-height: 1.12; margin-bottom: 1px; }
  .ep3-paper .pn { font-family: "DM Serif Display", Georgia, serif; font-size: 0.85rem; color: var(--ink); line-height: 1.06; }
  .ep3-paper .pv { font-size: 0.64rem; color: var(--muted); font-style: italic; margin-top: 2px; }
  .ep3-paper:hover .pn { color: var(--util); }
  .ep3-svg g, .ep3-svg line { transition: opacity 0.22s ease; }
  .ep3-pill rect, .ep3-pill text { transition: fill 0.22s ease; }
  .ep3-stage, .ep3-pgroup { transition: opacity 0.2s ease; cursor: pointer; }
  .ep3-stage.dim, .ep3-pgroup.dim { opacity: 0.3; }
  .ep3-stage.act .st { text-decoration: underline; text-underline-offset: 3px; }
  .ep3-stage.act p { color: var(--ink); }
  .ep3-stage[data-stage="retrieve"] .st, .ep3-pgroup[data-stage="retrieve"] .glabel, .ep3-pgroup[data-stage="retrieve"] .d-role { color: var(--gen); }
  .ep3-stage[data-stage="summarize"] .st, .ep3-pgroup[data-stage="summarize"] .glabel, .ep3-pgroup[data-stage="summarize"] .d-role { color: var(--util); }
  .ep3-stage[data-stage="verify"] .st, .ep3-pgroup[data-stage="verify"] .glabel, .ep3-pgroup[data-stage="verify"] .d-role { color: var(--eval); }
  .ep3-pgroup[data-stage="retrieve"] .ep3-paper:hover .pn { color: var(--gen); }
  .ep3-pgroup[data-stage="summarize"] .ep3-paper:hover .pn { color: var(--util); }
  .ep3-pgroup[data-stage="verify"] .ep3-paper:hover .pn { color: var(--eval); }
  /* compact 3-col that fits the 900px deck slide — opt in with class "ep3-compact" on the mount; research.html keeps the full-width layout */
  #ep3-mount.ep3-compact .ep3-grid { grid-template-columns: 178px 1fr 292px; gap: 20px; margin-top: 0; }
  #ep3-mount.ep3-compact .ep3-svg { max-width: 340px; }
  #ep3-mount.ep3-compact .ep3-left { gap: 14px; }
  #ep3-mount.ep3-compact .ep3-right { gap: 10px; }
  #ep3-mount.ep3-compact .ep3-pgroup { row-gap: 9px; }
  @media (max-width: 900px) {
    .ep3-grid { grid-template-columns: 1fr; }
    .ep3-left, .ep3-right { max-width: 440px; margin: 0 auto; }
  }`;

  function paper(href, cover, alt, role, name, venue) {
    return '<a class="ep3-paper" href="' + href + '" target="_blank" rel="noopener"><img src="' + cover + '" alt="' + alt + '"><div class="pmeta"><div class="d-role">' + role + '</div><div class="pn">' + name + '</div><div class="pv">' + venue + '</div></div></a>';
  }
  var HTML =
    '<div class="ep3-grid">' +
      '<div class="ep3-side ep3-left">' +
        '<a class="ep3-persp" href="/assets/papers/Retrieve-Summarize-Verify.pdf" target="_blank" rel="noopener">' +
          '<img src="/assets/covers/Retrieve-Summarize-Verify.png" alt="Retrieve, Summarize, and Verify">' +
          '<div><div class="pl">The perspective</div><div class="pn"><span style="color:var(--gen)">Retrieve</span>, <span style="color:var(--util)">Summarize</span> &amp; <span style="color:var(--eval)">Verify</span></div><div class="pv">JASN, 2023</div></div>' +
        '</a>' +
        '<div class="ep3-stage" data-stage="retrieve"><div class="st">Retrieve</div><p>Search the evidence base for the pieces that actually answer the clinical question.</p></div>' +
        '<div class="ep3-stage" data-stage="summarize"><div class="st">Summarize</div><p>Condense the retrieved evidence into a single, grounded answer.</p></div>' +
        '<div class="ep3-stage" data-stage="verify"><div class="st">Verify</div><p>Check every claim in the answer against the source it cites.</p></div>' +
      '</div>' +
      '<div class="ep3-center">' +
        '<svg class="ep3-svg" id="ep3-svg" viewBox="145 108 610 614" xmlns="http://www.w3.org/2000/svg"></svg>' +
      '</div>' +
      '<div class="ep3-side ep3-right">' +
        '<div class="ep3-pgroup" data-stage="retrieve"><div class="glabel">Retrieve</div>' +
          paper('/assets/papers/LADER.pdf', '/assets/covers/LADER.png', 'LADER', 'Log-augmented dense retrieval', 'LADER', 'SIGIR, 2023') +
          paper('/assets/papers/PubMed-and-Beyond.pdf', '/assets/covers/PubMed-and-Beyond.png', 'PubMed and Beyond', 'Survey of AI search tools', 'PubMed and Beyond', 'eBioMedicine, 2024') +
          paper('/assets/papers/MedCPT.pdf', '/assets/covers/MedCPT.png', 'MedCPT', 'Zero-shot PubMed retriever', 'MedCPT', 'Bioinformatics, 2023') +
        '</div>' +
        '<div class="ep3-pgroup" data-stage="summarize"><div class="glabel">Summarize</div>' +
          paper('/assets/papers/MedRAG.pdf', '/assets/covers/MedRAG.png', 'MedRAG', 'Benchmarking medical RAG', 'MedRAG', 'ACL Findings, 2024') +
          paper('/assets/papers/i-MedRAG.pdf', '/assets/covers/i-MedRAG.png', 'i-MedRAG', 'Iterative follow-up RAG', 'i-MedRAG', 'PSB, 2025') +
          paper('/assets/papers/MedReview.pdf', '/assets/covers/MedReview.png', 'MedReview', 'Summarizing systematic reviews', 'MedReview', 'npj Digit Med, 2025') +
          paper('/assets/papers/MedCite.pdf', '/assets/covers/MedCite.png', 'MedCite', 'Verifiable answer citations', 'MedCite', 'ACL Findings, 2025') +
        '</div>' +
        '<div class="ep3-pgroup" data-stage="verify"><div class="glabel">Verify</div>' +
          paper('/assets/papers/Med-V1.pdf', '/assets/covers/Med-V1.png', 'Med-V1', 'Scalable evidence attribution', 'Med-V1', 'arXiv, 2026') +
          paper('/assets/papers/GeneAgent.pdf', '/assets/covers/GeneAgent.png', 'GeneAgent', 'Self-verifying gene-set agent', 'GeneAgent', 'Nature Methods, 2025') +
        '</div>' +
      '</div>' +
    '</div>';

  function draw(root) {
    var NS = 'http://www.w3.org/2000/svg';
    var svg = root.querySelector('.ep3-svg');
    var UTIL = '#2c5a8c';
    var STAGE_COLOR = { retrieve: '#2f6d5b', summarize: '#2c5a8c', verify: '#6b3f8c' };
    var ITEMS = [], PILLS = [];
    function el(name, attrs, parent) {
      var e = document.createElementNS(NS, name);
      for (var k in attrs) e.setAttribute(k, attrs[k]);
      (parent || svg).appendChild(e);
      return e;
    }
    var CX = 450, CY = 380, R = 240, V = [];
    for (var i = 0; i < 6; i++) {
      var a = Math.PI / 180 * (-90 + 60 * i);
      V.push({ x: CX + R * Math.cos(a), y: CY + R * Math.sin(a) });
    }
    var defs = el('defs');
    var mk = el('marker', { id: 'ep3ah', markerWidth: 9, markerHeight: 9, refX: 6.5, refY: 4, orient: 'auto' }, defs);
    el('path', { d: 'M0,0 L7,4 L0,8 Z', fill: 'context-stroke' }, mk);
    var STA = [
      { t: 'r', a: 60, b: 22 }, { t: 'p', a: 86, b: 74 }, { t: 'r', a: 65, b: 22 },
      { t: 'r', a: 102, b: 64 }, { t: 'r', a: 50, b: 22 }, { t: 'p', a: 86, b: 74 }
    ];
    var AGAP = 12;
    function reach(i, ux, uy) {
      var s = STA[i], a = s.a, b = s.b;
      if (s.t === 'r') return Math.min(Math.abs(ux) < 1e-6 ? 1e9 : a / Math.abs(ux), Math.abs(uy) < 1e-6 ? 1e9 : b / Math.abs(uy));
      var pts = [[0, -b], [-a, b], [a, b]], best = 1e9;
      for (var k = 0; k < 3; k++) {
        var A = pts[k], B = pts[(k + 1) % 3], Dx = B[0] - A[0], Dy = B[1] - A[1];
        var det = -ux * Dy + Dx * uy; if (Math.abs(det) < 1e-9) continue;
        var tt = (-A[0] * Dy + Dx * A[1]) / det, ss = (ux * A[1] - A[0] * uy) / det;
        if (tt > 0 && ss >= -0.01 && ss <= 1.01 && tt < best) best = tt;
      }
      if (uy > 0.25) best += 32;
      else if (uy < -0.25) best += 30;
      return best;
    }
    [[5, 0, 'retrieve'], [0, 1, 'retrieve'], [1, 2, 'summarize'], [2, 3, 'summarize'], [3, 4, 'verify'], [4, 5, 'verify']].forEach(function (e2) {
      var A2 = V[e2[0]], B2 = V[e2[1]];
      var dx = B2.x - A2.x, dy = B2.y - A2.y, L = Math.sqrt(dx * dx + dy * dy), ux = dx / L, uy = dy / L;
      var ln = el('line', {
        x1: A2.x + ux * (reach(e2[0], ux, uy) + AGAP), y1: A2.y + uy * (reach(e2[0], ux, uy) + AGAP),
        x2: B2.x - ux * (reach(e2[1], -ux, -uy) + AGAP), y2: B2.y - uy * (reach(e2[1], -ux, -uy) + AGAP),
        stroke: STAGE_COLOR[e2[2]], 'stroke-width': 1.7, 'marker-end': 'url(#ep3ah)'
      });
      ITEMS.push({ el: ln, stages: [e2[2]] });
    });
    function mulberry32(a) {
      return function () {
        a |= 0; a = a + 0x6D2B79F5 | 0;
        var t = Math.imul(a ^ a >>> 15, 1 | a);
        t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
        return ((t ^ t >>> 14) >>> 0) / 4294967296;
      };
    }
    function hexPts(cx, cy, r) {
      var p = [];
      for (var i = 0; i < 6; i++) { var a = Math.PI / 180 * (60 * i - 30); p.push((cx + r * Math.cos(a)).toFixed(1) + ',' + (cy + r * Math.sin(a)).toFixed(1)); }
      return p.join(' ');
    }
    var PH = 148, PHW = 86, HR = 6;
    var rng = mulberry32(20260703), pts = [], guard = 0;
    while (pts.length < 13 && guard++ < 4000) {
      var t = Math.sqrt(rng());
      if (t < 0.32) continue;
      var y = -PH / 2 + PH * t, hw = PHW * t - (HR + 5);
      if (hw < HR || y > PH / 2 - (HR + 3)) continue;
      var x = (rng() * 2 - 1) * hw, ok = true;
      for (var j = 0; j < pts.length; j++) { var ddx = pts[j].x - x, ddy = pts[j].y - y; if (ddx * ddx + ddy * ddy < 19 * 19) { ok = false; break; } }
      if (ok) pts.push({ x: x, y: y });
    }
    pts.sort(function (a, b) { return a.y - b.y; });
    var REL = { 1: 1, 4: 1, 7: 1, 10: 1 };
    var F = [0, 0.34, 0.48, 0.61, 0.74, 0.87, 1.0];
    var BANDS = ['#3d4f68', '#3a6389', '#4d7ba6', '#7ba4c9', '#aecae1', '#dcdbd3'];
    function pyramid(cx, cy, highlighted, caption) {
      var g = el('g', { transform: 'translate(' + cx + ',' + cy + ')' });
      for (var k = 0; k < 6; k++) {
        var hwT = PHW * F[k], hwB = PHW * F[k + 1], yT = -PH / 2 + PH * F[k], yB = -PH / 2 + PH * F[k + 1];
        el('polygon', { points: (-hwT) + ',' + yT + ' ' + hwT + ',' + yT + ' ' + hwB + ',' + yB + ' ' + (-hwB) + ',' + yB, fill: BANDS[k], opacity: highlighted ? 0.08 : 0.18 }, g);
      }
      el('polygon', { points: '0,' + (-PH / 2) + ' ' + PHW + ',' + PH / 2 + ' ' + (-PHW) + ',' + PH / 2, fill: 'none', stroke: '#b9c4d0', 'stroke-width': 1.2 }, g);
      pts.forEach(function (p, i) {
        var rel = REL[i];
        el('polygon', {
          points: hexPts(p.x, p.y, rel && highlighted ? HR + 1.4 : HR),
          fill: rel && highlighted ? '#dce9f7' : '#ffffff',
          stroke: rel && highlighted ? UTIL : '#8fa3b8', 'stroke-width': rel && highlighted ? 1.7 : 1,
          opacity: highlighted && !rel ? 0.25 : 0.95
        }, g);
      });
      el('text', { x: 0, y: PH / 2 + 24, 'text-anchor': 'middle', 'class': 'ep3-cap' }, g).textContent = caption;
      return g;
    }
    function pill(cx, cy, label, color) {
      var g = el('g', { transform: 'translate(' + cx + ',' + cy + ')', 'class': 'ep3-pill' });
      var w = label.length * 9.4 + 44;
      var rect = el('rect', { x: -w / 2, y: -21, width: w, height: 42, rx: 21, fill: '#ffffff', stroke: color, 'stroke-width': 1.5 }, g);
      var text = el('text', { x: 0, y: 6, 'text-anchor': 'middle', 'class': 'ep3-pill-t' }, g);
      text.style.fill = color;
      text.textContent = label;
      return { g: g, rect: rect, text: text, color: color };
    }
    function answer(cx, cy) {
      var g = el('g', { transform: 'translate(' + cx + ',' + cy + ')' });
      el('rect', { x: -102, y: -64, width: 204, height: 128, rx: 11, fill: '#ffffff', stroke: '#cfd6de', 'stroke-width': 1.3 }, g);
      [{ y: -42, w: 164 }, { y: -20, w: 128, cite: true }, { y: 2, w: 164 }, { y: 24, w: 108, cite: true }, { y: 46, w: 144 }].forEach(function (ln) {
        el('rect', { x: -82, y: ln.y - 4, width: ln.w, height: 8, rx: 4, fill: '#d9dde3' }, g);
        if (ln.cite) el('polygon', { points: hexPts(-82 + ln.w + 13, ln.y, 6), fill: '#dce9f7', stroke: UTIL, 'stroke-width': 1.4 }, g);
      });
      el('text', { x: 0, y: 90, 'text-anchor': 'middle', 'class': 'ep3-cap' }, g).textContent = 'Answer';
      return g;
    }
    var pRetrieve = pill(V[0].x, V[0].y, 'Retrieve', STAGE_COLOR.retrieve);
    var pyRelevant = pyramid(V[1].x, V[1].y, true, 'Relevant evidence');
    var pSummarize = pill(V[2].x, V[2].y, 'Summarize', STAGE_COLOR.summarize);
    var gAnswer = answer(V[3].x, V[3].y);
    var pVerify = pill(V[4].x, V[4].y, 'Verify', STAGE_COLOR.verify);
    var pyBase = pyramid(V[5].x, V[5].y, false, 'Evidence base');
    ITEMS.push(
      { el: pyBase, stages: ['retrieve', 'verify'] },
      { el: pyRelevant, stages: ['retrieve', 'summarize'] },
      { el: gAnswer, stages: ['summarize', 'verify'] }
    );
    PILLS.push(
      { stage: 'retrieve', g: pRetrieve.g, rect: pRetrieve.rect, text: pRetrieve.text, color: pRetrieve.color },
      { stage: 'summarize', g: pSummarize.g, rect: pSummarize.rect, text: pSummarize.text, color: pSummarize.color },
      { stage: 'verify', g: pVerify.g, rect: pVerify.rect, text: pVerify.text, color: pVerify.color }
    );
    PILLS.forEach(function (p) { ITEMS.push({ el: p.g, stages: [p.stage] }); });
    var stagesEls = [].slice.call(root.querySelectorAll('.ep3-stage'));
    var groupsEls = [].slice.call(root.querySelectorAll('.ep3-pgroup'));
    function highlight(stage) {
      ITEMS.forEach(function (it) {
        it.el.style.opacity = (!stage || it.stages.indexOf(stage) >= 0) ? '' : '0.4';
      });
      PILLS.forEach(function (p) {
        var act = p.stage === stage;
        p.rect.style.fill = act ? p.color : '#ffffff';
        p.text.style.fill = act ? '#ffffff' : p.color;
      });
      [].concat(stagesEls, groupsEls).forEach(function (e) {
        e.classList.toggle('act', e.dataset.stage === stage);
        e.classList.toggle('dim', !!stage && e.dataset.stage !== stage);
      });
    }
    var reset = function () { highlight(null); };
    PILLS.forEach(function (p) { p.g.style.cursor = 'pointer'; p.g.addEventListener('mouseenter', function () { highlight(p.stage); }); });
    stagesEls.forEach(function (s) { s.addEventListener('mouseenter', function () { highlight(s.dataset.stage); }); });
    groupsEls.forEach(function (grp) { grp.addEventListener('mouseenter', function () { highlight(grp.dataset.stage); }); });
    root.querySelector('.ep3-grid').addEventListener('mouseleave', reset);
  }

  function init() {
    var mount = document.getElementById('ep3-mount') || document.querySelector('.ep3-mount');
    if (!mount || mount.dataset.ep3Done) return;
    if (!document.getElementById('ep3-rsv-css')) {
      var st = document.createElement('style'); st.id = 'ep3-rsv-css'; st.textContent = CSS; document.head.appendChild(st);
    }
    mount.innerHTML = HTML;
    mount.dataset.ep3Done = '1';
    draw(mount);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
