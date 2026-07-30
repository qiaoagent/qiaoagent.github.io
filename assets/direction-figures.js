/* Shared direction figures — the three miniatures used on the research page's
   overview and on the home page's "Research Areas" view. Single source for the
   iceberg contour so the two pages can never drift apart.

   Contour traced from File:Further reading - Wikimedia 20 inspired icon.svg by
   Evelina Bang (WMSE), released under CC0 (a public-domain dedication, so no
   attribution or share-alike is owed). Scaled and recentred only.
   https://commons.wikimedia.org/wiki/File:Further_reading_-_Wikimedia_20_inspired_icon.svg */
(function () {
  var RING = [
  [28,181.3],[37.4,173.1],[46.8,164.9],[56.3,156.8],[65.8,148.7],[75.3,140.4],[84.7,132.3],
  [94.2,124.1],[103.6,116],[113.1,107.7],[120.4,97.6],[127.6,87.5],[134.8,77.3],
  [142.2,67.1],[149.3,56.9],[156.7,46.7],[163.9,36.6],[171.2,26.4],[178.4,16.2],[186.4,16],
  [195.3,24.9],[204,33.7],[212.7,42.7],[221.5,51.6],[230.3,60.4],[239.1,69.4],[247.8,78.3],
  [257.2,86.1],[269.4,88.6],[281.6,91.3],[293.9,93.9],[306.1,96.5],[318.3,99],[328.3,104.7],
  [334.6,115.6],[340.8,126.5],[347,137.2],[353.3,148.1],[359.5,158.9],[365.8,169.8],
  [372,180.5],[368.8,192.4],[364.8,204.2],[360.8,216.1],[356.8,227.8],[352.8,239.7],
  [348.8,251.5],[344.9,263.4],[340.9,275.2],[336.9,287.1],[332.9,299],[328.9,310.8],
  [324.9,322.7],[320.9,334.5],[315.8,345.8],[308.8,356.1],[301.7,366.4],[294.7,376.7],
  [287.7,387.1],[280.6,397.4],[273.9,407.8],[267.3,418.5],[260.7,429.1],[254,439.8],
  [247.6,450.4],[240.9,461],[230.7,468],[220,474.3],[209.2,480.7],[198.5,487.2],
  [187.8,493.6],[177.3,499.2],[171.2,488.3],[165.1,477.3],[158.9,466.5],[152.8,455.6],
  [146.7,444.6],[140.7,433.8],[134.6,422.8],[128.5,411.9],[122.4,401.1],[116.2,390.1],
  [110.1,379.2],[104.5,368.2],[103.4,355.8],[102.5,343.3],[101.5,330.8],[100.5,318.3],
  [99.5,306],[98.5,293.5],[97.5,281],[89.2,272.4],[79.6,264.4],[69.9,256.4],[60.3,248.4],
  [53.3,238.4],[48.2,226.9],[43.2,215.6],[38.1,204.1],[33,192.7]
  ];
  var WL = 148;                                  /* waterline, contour units */

  function svg(inner) {
    return '<svg viewBox="0 0 120 92" preserveAspectRatio="xMidYMid meet">' + inner + '</svg>';
  }

  /* Evidence Generation — the evidence pyramid */
  function pyramid() {
    var N = 5, TOP = 8, H = 76, WTOP = 20, WBOT = 92, GAP = 2.4, s = '';
    for (var i = 0; i < N; i++) {
      var wa = WTOP + (WBOT - WTOP) * i / N, wb = WTOP + (WBOT - WTOP) * (i + 1) / N;
      var y = TOP + i * (H / N), hh = H / N - GAP;
      s += '<polygon points="' + (60 - wa / 2).toFixed(1) + ',' + y.toFixed(1) + ' ' +
           (60 + wa / 2).toFixed(1) + ',' + y.toFixed(1) + ' ' +
           (60 + wb / 2).toFixed(1) + ',' + (y + hh).toFixed(1) + ' ' +
           (60 - wb / 2).toFixed(1) + ',' + (y + hh).toFixed(1) + '" ' +
           'fill="#2f6d5b" opacity="' + (0.94 - i * 0.13).toFixed(2) + '"/>';
    }
    return svg(s);
  }

  /* Evidence Utilization — retrieve → summarize → verify, spelled out */
  function loop() {
    var steps = ['Retrieve', 'Summarize', 'Verify'];
    var X0 = 28, X1 = 110, H = 17, GAP = 9, TOP = 7, s = '';
    steps.forEach(function (t, i) {
      var y = TOP + i * (H + GAP);
      s += '<rect x="' + X0 + '" y="' + y + '" width="' + (X1 - X0) + '" height="' + H +
           '" rx="' + (H / 2) + '" fill="#2c5a8c" opacity="' + (0.94 - i * 0.14).toFixed(2) + '"/>' +
           '<text x="' + ((X0 + X1) / 2) + '" y="' + (y + H / 2 + 3.4) + '" text-anchor="middle" ' +
           'font-size="9.6" font-weight="600" fill="#fff">' + t + '</text>';
      if (i < steps.length - 1) {
        var ay = y + H + 1.4;
        s += '<path d="M' + ((X0 + X1) / 2) + ',' + ay + ' l0,' + (GAP - 3.6) +
             '" stroke="#2c5a8c" stroke-width="1.5" opacity=".55"/>' +
             '<path d="M-3,-2.4 L0,1.4 L3,-2.4 Z" fill="#2c5a8c" opacity=".7" ' +
             'transform="translate(' + ((X0 + X1) / 2) + ',' + (ay + GAP - 3.2) + ')"/>';
      }
    });
    var yTop = TOP + H / 2, yBot = TOP + 2 * (H + GAP) + H / 2;
    s += '<path d="M' + X0 + ',' + yBot + ' C10,' + yBot + ' 10,' + yTop + ' ' + (X0 - 4) + ',' + yTop +
         '" fill="none" stroke="#2c5a8c" stroke-width="1.5" stroke-dasharray="4 3.5" opacity=".5"/>' +
         '<path d="M-2.6,-3.2 L2.2,0 L-2.6,3.2 Z" fill="#2c5a8c" opacity=".7" ' +
         'transform="translate(' + (X0 - 2.2) + ',' + yTop + ')"/>';
    return svg(s);
  }

  /* Medical AI Evaluation — the same contour as the iceberg section */
  function iceberg(uid) {
    var xs = RING.map(function (p) { return p[0]; }), ys = RING.map(function (p) { return p[1]; });
    var x0 = Math.min.apply(null, xs), x1 = Math.max.apply(null, xs);
    var y0 = Math.min.apply(null, ys), y1 = Math.max.apply(null, ys);
    var sc = Math.min(70 / (x1 - x0), 80 / (y1 - y0));
    var ox = 60 - ((x0 + x1) / 2) * sc, oy = 6 - y0 * sc;
    var d = 'M' + RING.map(function (p) {
      return (p[0] * sc + ox).toFixed(1) + ',' + (p[1] * sc + oy).toFixed(1);
    }).join('L') + 'Z';
    var wl = WL * sc + oy, id = 'ovIce' + (uid || '');
    return svg(
      '<defs><clipPath id="' + id + '"><path d="' + d + '"/></clipPath></defs>' +
      '<path d="' + d + '" fill="#6b3f8c" opacity=".22"/>' +
      '<rect x="0" y="' + wl.toFixed(1) + '" width="120" height="92" clip-path="url(#' + id + ')" ' +
      'fill="#6b3f8c" opacity=".42"/>' +
      '<line x1="0" y1="' + wl.toFixed(1) + '" x2="120" y2="' + wl.toFixed(1) +
      '" stroke="#6b3f8c" stroke-width="1.4" opacity=".65"/>');
  }

  window.DirectionFigures = {
    RING: RING,
    WL: WL,
    /* mount(prefix) fills #<prefix>-gen / -util / -eval if present */
    mount: function (prefix) {
      var g = document.getElementById(prefix + '-gen'),
          u = document.getElementById(prefix + '-util'),
          e = document.getElementById(prefix + '-eval');
      if (g) g.innerHTML = pyramid();
      if (u) u.innerHTML = loop();
      if (e) e.innerHTML = iceberg(prefix);
      return !!(g || u || e);
    }
  };
})();
