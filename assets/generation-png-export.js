/* Export the visible evidence-generation diagram, including its selected state.
   Paper cards use html2canvas. Pyramid faces are projected by the browser and
   rasterized separately because html2canvas cannot render CSS 3D or clip-path. */
(function () {
  'use strict';

  var SCALE = 4;
  var PADDING = 12;

  function number(value, fallback) {
    var parsed = parseFloat(value);
    return isFinite(parsed) ? parsed : (fallback || 0);
  }

  function boundsOf(points) {
    return {
      left: Math.min.apply(null, points.map(function (p) { return p.x; })),
      top: Math.min.apply(null, points.map(function (p) { return p.y; })),
      right: Math.max.apply(null, points.map(function (p) { return p.x; })),
      bottom: Math.max.apply(null, points.map(function (p) { return p.y; }))
    };
  }

  function rectPoints(rect) {
    return [
      { x: rect.left, y: rect.top }, { x: rect.right, y: rect.top },
      { x: rect.right, y: rect.bottom }, { x: rect.left, y: rect.bottom }
    ];
  }

  function sizeOf(element, style) {
    var width = number(style.width, element.offsetWidth);
    var height = number(style.height, element.offsetHeight);
    if (style.boxSizing !== 'border-box') {
      width += number(style.paddingLeft) + number(style.paddingRight) + number(style.borderLeftWidth) + number(style.borderRightWidth);
      height += number(style.paddingTop) + number(style.paddingBottom) + number(style.borderTopWidth) + number(style.borderBottomWidth);
    }
    return { width: width, height: height };
  }

  // Zero-size probes expose the exact transformed points, including perspective.
  // They have no layout effect and are removed before the first asynchronous step.
  function projectedCorners(element, size, origin) {
    var style = getComputedStyle(element);
    var bx = number(style.borderLeftWidth), by = number(style.borderTopWidth);
    var points = [[0, 0], [size.width, 0], [size.width, size.height], [0, size.height]];
    var probes = points.map(function (point) {
      var probe = document.createElement('span');
      probe.style.cssText = 'position:absolute!important;display:block!important;width:0!important;height:0!important;margin:0!important;padding:0!important;border:0!important;transform:none!important;pointer-events:none!important;';
      probe.style.setProperty('left', (point[0] - bx) + 'px', 'important');
      probe.style.setProperty('top', (point[1] - by) + 'px', 'important');
      element.appendChild(probe);
      return probe;
    });
    try {
      return probes.map(function (probe) {
        var rect = probe.getBoundingClientRect();
        return { x: rect.left - origin.left, y: rect.top - origin.top };
      });
    } finally {
      probes.forEach(function (probe) { probe.remove(); });
    }
  }

  function projection(quad) {
    var p0 = quad[0], p1 = quad[1], p2 = quad[2], p3 = quad[3];
    var dx1 = p1.x - p2.x, dx2 = p3.x - p2.x;
    var dy1 = p1.y - p2.y, dy2 = p3.y - p2.y;
    var dx3 = p0.x - p1.x + p2.x - p3.x;
    var dy3 = p0.y - p1.y + p2.y - p3.y;
    var denominator = dx1 * dy2 - dx2 * dy1;
    var g = Math.abs(denominator) > 1e-9 ? (dx3 * dy2 - dx2 * dy3) / denominator : 0;
    var h = Math.abs(denominator) > 1e-9 ? (dx1 * dy3 - dx3 * dy1) / denominator : 0;
    var a = p1.x - p0.x + g * p1.x, b = p3.x - p0.x + h * p3.x;
    var d = p1.y - p0.y + g * p1.y, e = p3.y - p0.y + h * p3.y;
    return function (u, v) {
      var divisor = g * u + h * v + 1;
      return { x: (a * u + b * v + p0.x) / divisor, y: (d * u + e * v + p0.y) / divisor };
    };
  }

  function signedArea(quad) {
    return quad.reduce(function (sum, point, i) {
      var next = quad[(i + 1) % quad.length];
      return sum + point.x * next.y - next.x * point.y;
    }, 0) / 2;
  }

  function opacityUntil(element, stop) {
    var opacity = 1;
    for (var node = element; node && node !== stop; node = node.parentElement) {
      var style = getComputedStyle(node);
      if (style.display === 'none' || style.visibility === 'hidden') return 0;
      opacity *= number(style.opacity, 1);
    }
    return opacity;
  }

  function clipPoints(style, size) {
    var clip = style.clipPath || style.webkitClipPath;
    if (!clip || clip === 'none') return [[0, 0], [1, 0], [1, 1], [0, 1]];
    var match = clip.match(/^polygon\((.*)\)$/);
    if (!match) throw new Error('Unsupported pyramid clipping shape.');
    return match[1].split(',').map(function (pair) {
      var values = pair.trim().split(/\s+/);
      return values.map(function (value, axis) {
        return value.indexOf('%') >= 0 ? number(value) / 100 : number(value) / (axis ? size.height : size.width);
      });
    });
  }

  // Only used to sort overlapping 3D planes. Screen geometry comes from probes.
  function depthOf(element, scene, size) {
    var matrix = new DOMMatrix();
    for (var node = element; node && node !== scene; node = node.parentElement) {
      var style = getComputedStyle(node);
      var origin = style.transformOrigin.split(/\s+/).map(function (value) { return number(value); });
      var transform = style.transform === 'none' ? new DOMMatrix() : new DOMMatrix(style.transform);
      var placement = new DOMMatrix().translate(node.offsetLeft, node.offsetTop)
        .translate(origin[0], origin[1], origin[2] || 0).multiply(transform)
        .translate(-origin[0], -origin[1], -(origin[2] || 0));
      matrix = placement.multiply(matrix);
    }
    return matrix.transformPoint(new DOMPoint(size.width / 2, size.height / 2, 0)).z;
  }

  function labelSnapshot(label, faceStyle, size) {
    if (!label) return null;
    var style = getComputedStyle(label), labelSize = sizeOf(label, style);
    var width = labelSize.width, height = labelSize.height;
    var left = number(faceStyle.borderLeftWidth) + number(faceStyle.paddingLeft);
    var top = number(faceStyle.borderTopWidth) + number(faceStyle.paddingTop);
    var innerWidth = size.width - left - number(faceStyle.borderRightWidth) - number(faceStyle.paddingRight);
    var innerHeight = size.height - top - number(faceStyle.borderBottomWidth) - number(faceStyle.paddingBottom);
    var x = left + (innerWidth - width) / 2;
    var y = top + (faceStyle.alignItems === 'flex-end' ? innerHeight - height : (innerHeight - height) / 2);
    var font = style.fontStyle + ' ' + style.fontWeight + ' ' + style.fontSize + ' ' + style.fontFamily;
    // Let the browser determine line breaks in the same untransformed text box.
    var probe = document.createElement('span');
    probe.style.cssText = 'position:fixed;display:block;left:-10000px;top:0;margin:0;padding:0;border:0;visibility:hidden;white-space:normal;text-align:center;';
    probe.style.width = width + 'px';
    probe.style.font = font;
    probe.style.lineHeight = style.lineHeight;
    probe.style.letterSpacing = style.letterSpacing;
    probe.style.wordSpacing = style.wordSpacing;
    probe.textContent = label.textContent;
    document.body.appendChild(probe);
    var lines = [];
    try {
      var textNode = probe.firstChild, word, pattern = /\S+/g;
      while ((word = pattern.exec(probe.textContent))) {
        var range = document.createRange();
        range.setStart(textNode, word.index);
        range.setEnd(textNode, word.index + word[0].length);
        var rect = range.getBoundingClientRect();
        var previous = lines[lines.length - 1];
        if (previous && Math.abs(previous.top - rect.top) < 0.5) previous.text += ' ' + word[0];
        else lines.push({ text: word[0], top: rect.top });
      }
    } finally {
      probe.remove();
    }
    return {
      x: x, y: y, width: width, height: height, lines: lines,
      lineHeight: number(style.lineHeight, number(style.fontSize) * 1.12),
      fontSize: number(style.fontSize), font: font, color: style.color,
      spacing: style.letterSpacing === 'normal' ? '0px' : style.letterSpacing,
      opacity: number(style.opacity, 1)
    };
  }

  function snapshotPyramid(root, origin) {
    var scene = root.querySelector('#ep2-scene'), flat = root.querySelector('#ep2-flat');
    var threeD = scene && getComputedStyle(scene).display !== 'none';
    var host = threeD ? scene : flat;
    if (!host) throw new Error('The pyramid is unavailable.');
    var selector = threeD ? '.ep-sface, .ep-cap' : '.ep-ftier';
    var faces = [];
    host.querySelectorAll(selector).forEach(function (element) {
      var style = getComputedStyle(element), opacity = opacityUntil(element, root);
      if (opacity <= 0.001) return;
      var size = sizeOf(element, style);
      if (!(size.width > 0 && size.height > 0)) return;
      var quad = projectedCorners(element, size, origin);
      var cap = element.classList.contains('ep-cap');
      if (threeD && !cap && signedArea(quad) <= 0.01) return;
      if (Math.abs(signedArea(quad)) <= 0.01) return;
      var project = projection(quad);
      var polygon = clipPoints(style, size).map(function (point) { return project(point[0], point[1]); });
      faces.push({
        quad: quad, polygon: polygon, size: size, opacity: opacity,
        color: style.backgroundColor, filter: style.filter,
        border: number(style.borderTopWidth), borderColor: style.borderTopColor,
        shadow: cap, label: labelSnapshot(element.querySelector('.ep-plab, .ep-flab'), style, size),
        depth: threeD ? depthOf(element, scene, size) : 0
      });
    });
    if (!faces.length) throw new Error('The pyramid must be visible before exporting.');
    faces.sort(function (a, b) { return a.depth - b.depth; });
    return faces;
  }

  function faceTexture(face) {
    var canvas = document.createElement('canvas');
    canvas.width = Math.max(1, Math.ceil(face.size.width * SCALE));
    canvas.height = Math.max(1, Math.ceil(face.size.height * SCALE));
    var context = canvas.getContext('2d');
    context.scale(canvas.width / face.size.width, canvas.height / face.size.height);
    context.fillStyle = face.color;
    context.fillRect(0, 0, face.size.width, face.size.height);
    if (face.shadow) {
      // Match the exposed caps' soft inset shading without affecting geometry.
      [[0, 0, 22, 0], [face.size.width, 0, face.size.width - 22, 0],
        [0, 0, 0, 22], [0, face.size.height, 0, face.size.height - 22]].forEach(function (edge) {
        var gradient = context.createLinearGradient.apply(context, edge);
        gradient.addColorStop(0, 'rgba(0,0,0,0.18)');
        gradient.addColorStop(1, 'rgba(0,0,0,0)');
        context.fillStyle = gradient;
        context.fillRect(0, 0, face.size.width, face.size.height);
      });
    }
    if (face.border) {
      context.fillStyle = face.borderColor;
      context.fillRect(0, 0, face.size.width, face.border);
    }
    var label = face.label;
    if (label) {
      context.font = label.font;
      context.fillStyle = label.color;
      context.globalAlpha = label.opacity;
      context.textAlign = 'center';
      context.textBaseline = 'alphabetic';
      if ('letterSpacing' in context) context.letterSpacing = label.spacing;
      var metrics = context.measureText('Mg');
      var ascent = metrics.fontBoundingBoxAscent || label.fontSize * 0.8;
      var descent = metrics.fontBoundingBoxDescent || label.fontSize * 0.2;
      var baseline = (label.lineHeight - ascent - descent) / 2 + ascent;
      label.lines.forEach(function (line, index) {
        context.fillText(line.text, label.x + label.width / 2, label.y + index * label.lineHeight + baseline);
      });
    }
    if (face.filter && face.filter !== 'none') {
      var filtered = document.createElement('canvas');
      filtered.width = canvas.width; filtered.height = canvas.height;
      var filteredContext = filtered.getContext('2d');
      filteredContext.filter = face.filter;
      filteredContext.drawImage(canvas, 0, 0);
      return filtered;
    }
    return canvas;
  }

  function triangle(context, image, source, target) {
    var s0 = source[0], s1 = source[1], s2 = source[2];
    var t0 = target[0], t1 = target[1], t2 = target[2];
    var dx1 = s1.x - s0.x, dy1 = s1.y - s0.y, dx2 = s2.x - s0.x, dy2 = s2.y - s0.y;
    var determinant = dx1 * dy2 - dx2 * dy1;
    if (Math.abs(determinant) < 1e-9) return;
    var a = ((t1.x - t0.x) * dy2 - (t2.x - t0.x) * dy1) / determinant;
    var b = ((t1.y - t0.y) * dy2 - (t2.y - t0.y) * dy1) / determinant;
    var c = (dx1 * (t2.x - t0.x) - dx2 * (t1.x - t0.x)) / determinant;
    var d = (dx1 * (t2.y - t0.y) - dx2 * (t1.y - t0.y)) / determinant;
    var center = { x: (t0.x + t1.x + t2.x) / 3, y: (t0.y + t1.y + t2.y) / 3 };
    context.save();
    context.beginPath();
    target.forEach(function (point, index) {
      var dx = point.x - center.x, dy = point.y - center.y, length = Math.hypot(dx, dy);
      // Subpixel overlap prevents hairline seams between mesh triangles.
      var x = point.x + dx / length * 0.3, y = point.y + dy / length * 0.3;
      if (index) context.lineTo(x, y); else context.moveTo(x, y);
    });
    context.closePath(); context.clip();
    context.transform(a, b, c, d, t0.x - a * s0.x - c * s0.y, t0.y - b * s0.x - d * s0.y);
    context.drawImage(image, 0, 0);
    context.restore();
  }

  function drawFace(context, face) {
    var texture = faceTexture(face), bounds = boundsOf(face.polygon);
    var left = Math.floor(bounds.left * SCALE) - 2, top = Math.floor(bounds.top * SCALE) - 2;
    var layer = document.createElement('canvas');
    layer.width = Math.ceil(bounds.right * SCALE) - left + 2;
    layer.height = Math.ceil(bounds.bottom * SCALE) - top + 2;
    var paint = layer.getContext('2d');
    paint.beginPath();
    face.polygon.forEach(function (point, index) {
      var x = point.x * SCALE - left, y = point.y * SCALE - top;
      if (index) paint.lineTo(x, y); else paint.moveTo(x, y);
    });
    paint.closePath(); paint.clip();
    var quad = face.quad;
    var affine = Math.abs(quad[0].x + quad[2].x - quad[1].x - quad[3].x) < 0.001 &&
      Math.abs(quad[0].y + quad[2].y - quad[1].y - quad[3].y) < 0.001;
    if (affine) {
      // The flat pyramid needs no mesh at all: keep every glyph pixel exact.
      paint.save();
      paint.transform((quad[1].x - quad[0].x) * SCALE / texture.width,
        (quad[1].y - quad[0].y) * SCALE / texture.width,
        (quad[3].x - quad[0].x) * SCALE / texture.height,
        (quad[3].y - quad[0].y) * SCALE / texture.height,
        quad[0].x * SCALE - left, quad[0].y * SCALE - top);
      paint.drawImage(texture, 0, 0); paint.restore();
    }
    var project = projection(face.quad), columns = 16, rows = affine ? 0 : 8;
    function vertex(u, v) {
      var point = project(u, v);
      return { source: { x: u * texture.width, y: v * texture.height }, target: { x: point.x * SCALE - left, y: point.y * SCALE - top } };
    }
    for (var row = 0; row < rows; row++) {
      for (var col = 0; col < columns; col++) {
        var tl = vertex(col / columns, row / rows), tr = vertex((col + 1) / columns, row / rows);
        var br = vertex((col + 1) / columns, (row + 1) / rows), bl = vertex(col / columns, (row + 1) / rows);
        triangle(paint, texture, [tl.source, tr.source, br.source], [tl.target, tr.target, br.target]);
        triangle(paint, texture, [tl.source, br.source, bl.source], [tl.target, br.target, bl.target]);
      }
    }
    // Apply face/ancestor opacity once, after the opaque mesh has been assembled.
    context.save(); context.globalAlpha = face.opacity;
    context.drawImage(layer, left, top); context.restore();
  }

  function snapshotArrows(root) {
    var svg = root.querySelector('.ep2-arrows');
    if (!svg || getComputedStyle(svg).display === 'none') return [];
    return [].slice.call(svg.querySelectorAll('.ep2-arrow')).map(function (path) {
      var style = getComputedStyle(path), length = path.getTotalLength();
      var end = path.getPointAtLength(length), previous = path.getPointAtLength(Math.max(0, length - 0.1));
      var bounds = path.getBBox();
      return {
        d: path.getAttribute('d'), color: style.stroke, width: number(style.strokeWidth, 1.4),
        opacity: opacityUntil(path, root), linecap: style.strokeLinecap,
        end: { x: end.x, y: end.y }, angle: Math.atan2(end.y - previous.y, end.x - previous.x),
        bounds: { left: bounds.x, top: bounds.y, right: bounds.x + bounds.width, bottom: bounds.y + bounds.height }
      };
    });
  }

  function drawArrows(context, arrows) {
    arrows.forEach(function (arrow) {
      context.save(); context.scale(SCALE, SCALE);
      context.globalAlpha = arrow.opacity; context.strokeStyle = arrow.color;
      context.lineWidth = arrow.width; context.lineCap = arrow.linecap;
      context.stroke(new Path2D(arrow.d));
      context.translate(arrow.end.x, arrow.end.y); context.rotate(arrow.angle);
      context.scale(arrow.width, arrow.width); context.translate(-5.5, -3.5);
      context.beginPath(); context.moveTo(0, 0); context.lineTo(6, 3.5); context.lineTo(0, 7); context.closePath();
      context.fillStyle = arrow.color; context.fill(); context.restore();
    });
  }

  async function readyImage(image) {
    if (!image.complete) await new Promise(function (resolve, reject) {
      var timeout;
      function clean() { clearTimeout(timeout); image.removeEventListener('load', loaded); image.removeEventListener('error', failed); }
      function loaded() { clean(); resolve(); }
      function failed() { clean(); reject(new Error('A paper cover could not be loaded.')); }
      image.addEventListener('load', loaded); image.addEventListener('error', failed);
      timeout = setTimeout(failed, 15000);
    });
    if (!image.naturalWidth) throw new Error('A paper cover is missing.');
    if (image.decode) await image.decode();
  }

  function imageData(image, bounds) {
    var canvas = document.createElement('canvas');
    canvas.width = Math.min(image.naturalWidth, Math.ceil(bounds.width * SCALE));
    canvas.height = Math.ceil(canvas.width * image.naturalHeight / image.naturalWidth);
    canvas.getContext('2d').drawImage(image, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/png');
  }

  async function download(canvas, filename) {
    var blob = await new Promise(function (resolve, reject) {
      canvas.toBlob(function (result) { if (result) resolve(result); else reject(new Error('Could not create the PNG.')); }, 'image/png');
    });
    var url = URL.createObjectURL(blob), link = document.createElement('a');
    try {
      link.href = url; link.download = filename || 'evidence-generation.png';
      document.body.appendChild(link); link.click();
    } finally {
      link.remove(); setTimeout(function () { URL.revokeObjectURL(url); }, 10000);
    }
  }

  window.exportGenerationPng = async function (root, filename) {
    if (!root || !root.matches('.ep2-layout')) throw new Error('The evidence-generation diagram is unavailable.');
    if (typeof window.html2canvas !== 'function') throw new Error('The PNG renderer is unavailable.');
    var origin = root.getBoundingClientRect();
    var cards = [].slice.call(root.querySelectorAll('.ep2-deck'));
    if (!cards.length || origin.width <= 0) throw new Error('The evidence-generation diagram must be visible.');
    var cardStates = cards.map(function (card) {
      var image = card.querySelector('img');
      return { bounds: card.getBoundingClientRect(), opacity: opacityUntil(card, root), image: image, imageBounds: image.getBoundingClientRect() };
    });
    // Capture geometry and paint before asynchronous image loading or user input.
    var faces = snapshotPyramid(root, origin), arrows = snapshotArrows(root);
    var points = [];
    cardStates.forEach(function (card) {
      rectPoints(card.bounds).forEach(function (point) { points.push({ x: point.x - origin.left, y: point.y - origin.top }); });
    });
    faces.forEach(function (face) { points = points.concat(face.polygon); });
    arrows.forEach(function (arrow) { points = points.concat(rectPoints(arrow.bounds)); });
    var extent = boundsOf(points);
    var left = Math.floor(extent.left - PADDING), top = Math.floor(extent.top - PADDING);
    var width = Math.ceil(extent.right + PADDING) - left, height = Math.ceil(extent.bottom + PADDING) - top;
    if (document.fonts) await document.fonts.ready;
    await Promise.all(cardStates.map(function (card) { return readyImage(card.image); }));
    var coverData = cardStates.map(function (card) { return imageData(card.image, card.imageBounds); });
    var diagram = document.createElement('canvas');
    diagram.width = Math.ceil(origin.width * SCALE); diagram.height = Math.ceil(origin.height * SCALE);
    var paint = diagram.getContext('2d');
    drawArrows(paint, arrows);
    faces.forEach(function (face) { drawFace(paint, face); });
    var diagramData = diagram.toDataURL('image/png');
    var frame, canvas;
    try {
      canvas = await window.html2canvas(root, {
        backgroundColor: '#ffffff', scale: SCALE, x: left, y: top, width: width, height: height,
        windowWidth: window.innerWidth, windowHeight: window.innerHeight,
        scrollX: window.scrollX, scrollY: window.scrollY,
        foreignObjectRendering: false, allowTaint: false, logging: false, imageTimeout: 15000, removeContainer: true,
        onclone: async function (clonedDocument, copy) {
          frame = clonedDocument.defaultView.frameElement;
          var copiedCards = [].slice.call(copy.querySelectorAll('.ep2-deck'));
          if (copiedCards.length !== cardStates.length) throw new Error('The paper cards changed during export.');
          // Flatten only the cloned diagram. This avoids display:contents/grid
          // differences and removes every title, toggle, button and hint.
          copy.replaceChildren();
          copy.style.cssText = 'position:relative;display:block;box-sizing:border-box;margin:0;padding:0;border:0;overflow:visible;transform:none;background:transparent;max-width:none;width:' + origin.width + 'px;height:' + origin.height + 'px;';
          var replacement = clonedDocument.createElement('img');
          replacement.alt = ''; replacement.src = diagramData;
          replacement.style.cssText = 'position:absolute;left:0;top:0;display:block;max-width:none;margin:0;border:0;width:' + origin.width + 'px;height:' + origin.height + 'px;z-index:0;';
          copy.appendChild(replacement);
          var copiedImages = [];
          copiedCards.forEach(function (card, index) {
            var saved = cardStates[index], rect = saved.bounds;
            card.classList.remove('dim', 'act');
            card.style.cssText = 'position:absolute;display:flex;box-sizing:border-box;align-items:center;gap:9px;min-width:0;max-width:none;grid-column:auto;grid-row:auto;margin:0;padding:0;transform:none;transition:none;animation:none;z-index:1;left:' + (rect.left - origin.left) + 'px;top:' + (rect.top - origin.top) + 'px;width:' + rect.width + 'px;height:' + rect.height + 'px;opacity:' + saved.opacity + ';';
            card.querySelectorAll('*').forEach(function (element) { element.style.transition = 'none'; element.style.animation = 'none'; });
            var image = card.querySelector('img');
            image.removeAttribute('srcset'); image.src = coverData[index];
            image.style.width = saved.imageBounds.width + 'px'; image.style.height = saved.imageBounds.height + 'px';
            copiedImages.push(image); copy.appendChild(card);
          });
          for (var ancestor = copy.parentElement; ancestor; ancestor = ancestor.parentElement) {
            ancestor.style.overflow = 'visible'; ancestor.style.clipPath = 'none'; ancestor.style.contain = 'none';
          }
          await Promise.all([replacement].concat(copiedImages).map(readyImage));
          if (clonedDocument.fonts) await clonedDocument.fonts.ready;
        }
      });
    } finally {
      if (frame) frame.remove();
    }
    await download(canvas, filename);
  };
})();
