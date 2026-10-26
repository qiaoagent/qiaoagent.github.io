/* Export the RSV and medical AI evaluation overviews without their controls.
   html2canvas renders the HTML layout. The inline SVG is rasterized separately
   so its labels retain the page's loaded fonts and its arrows retain their color. */
(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var PAINT = [
    'color', 'display', 'visibility', 'opacity', 'fill', 'fill-opacity',
    'fill-rule', 'stroke', 'stroke-width', 'stroke-opacity', 'stroke-linecap',
    'stroke-linejoin', 'stroke-miterlimit', 'stroke-dasharray',
    'stroke-dashoffset', 'paint-order', 'shape-rendering', 'vector-effect'
  ];

  // Inline values hold the intended selection during an opacity/fill transition.
  function targetStyle(element, computed, property) {
    var inline = element.style.getPropertyValue(property);
    if (inline && inline.indexOf('var(') < 0) return inline;
    return computed.getPropertyValue(property);
  }

  function matrixValues(matrix) {
    return [matrix.a, matrix.b, matrix.c, matrix.d, matrix.e, matrix.f];
  }

  function numberAttribute(element, name) {
    var values = element[name] && element[name].baseVal;
    return values && values.numberOfItems ? values.getItem(0).value : 0;
  }

  function snapshot(svg, options) {
    options = options || {};
    var viewBox = svg.viewBox.baseVal;
    var padding = options.padding || 0;
    var box = { x: viewBox.x - padding, y: viewBox.y - padding,
      width: viewBox.width + padding * 2, height: viewBox.height + padding * 2 };
    if (!(viewBox.width > 0 && viewBox.height > 0)) {
      throw new Error('The SVG needs a nonempty viewBox for PNG export.');
    }
    var screen = svg.getScreenCTM();
    if (!screen) throw new Error('The SVG must be visible before exporting.');
    var inverse = screen.inverse();
    var clone = svg.cloneNode(true);
    var originals = [svg].concat([].slice.call(svg.querySelectorAll('*')));
    var copies = [clone].concat([].slice.call(clone.querySelectorAll('*')));
    var styles = new Map();
    var text = [];

    originals.forEach(function (element, index) {
      var computed = getComputedStyle(element);
      var paint = {};
      PAINT.forEach(function (property) {
        var value = targetStyle(element, computed, property);
        // Computed SVG paints can contain a full document URL. The standalone
        // image must reference its own gradient definitions instead.
        if (options.freezeTransforms && value) value = value.replace(/url\(["']?[^)#]*#([^)'"\s]+)["']?\)/g, 'url(#$1)');
        paint[property] = value;
        if (value) copies[index].style.setProperty(property, value);
      });
      if (options.freezeTransforms) {
        ['transform', 'transform-origin', 'transform-box'].forEach(function (property) {
          copies[index].style.setProperty(property, computed.getPropertyValue(property));
        });
      }
      copies[index].style.setProperty('transition', 'none');
      copies[index].style.setProperty('animation', 'none');
      styles.set(element, { computed: computed, paint: paint });
    });

    originals.forEach(function (element, index) {
      if (element.localName !== 'text') return;
      if (element.children.length) {
        throw new Error('PNG export currently supports simple SVG text labels.');
      }
      var saved = styles.get(element);
      var computed = saved.computed;
      var opacity = 1;
      var hidden = false;
      for (var parent = element; parent; parent = parent.parentElement) {
        var parentPaint = styles.get(parent).paint;
        var amount = parseFloat(parentPaint.opacity);
        if (isFinite(amount)) opacity *= amount;
        if (parentPaint.display === 'none' || parentPaint.visibility === 'hidden') hidden = true;
        if (parent === svg) break;
      }
      var textScreen = element.getScreenCTM();
      if (!textScreen) throw new Error('Could not locate an SVG text label.');
      text.push({
        value: element.textContent,
        x: numberAttribute(element, 'x') + numberAttribute(element, 'dx'),
        y: numberAttribute(element, 'y') + numberAttribute(element, 'dy'),
        matrix: matrixValues(inverse.multiply(textScreen)),
        font: computed.fontStyle + ' ' + computed.fontWeight + ' ' + computed.fontSize + ' ' + computed.fontFamily,
        anchor: computed.textAnchor,
        baseline: computed.dominantBaseline,
        direction: computed.direction,
        spacing: computed.letterSpacing,
        fill: saved.paint.fill,
        opacity: hidden ? 0 : opacity * (parseFloat(saved.paint['fill-opacity']) || 0)
      });
      copies[index].remove();
    });

    // A fixed-color copy of each used marker avoids context-stroke differences
    // between inline SVG rendering and an SVG loaded into an Image.
    var definitions = clone.querySelector('defs');
    if (!definitions) {
      definitions = document.createElementNS(NS, 'defs');
      clone.insertBefore(definitions, clone.firstChild);
    }
    var markers = {};
    [].slice.call(clone.querySelectorAll('marker[id]')).forEach(function (marker) {
      markers[marker.id] = marker;
    });
    var markerNumber = 0;
    originals.forEach(function (element, index) {
      ['marker-start', 'marker-mid', 'marker-end'].forEach(function (property) {
        var reference = element.getAttribute(property) || getComputedStyle(element).getPropertyValue(property);
        var match = reference && reference.match(/#([^\s)'"#]+)[)'"\s]*$/);
        if (!match || !markers[match[1]]) return;
        var marker = markers[match[1]].cloneNode(true);
        var id;
        do { id = 'svg-png-marker-' + markerNumber++; } while (clone.querySelector('[id="' + id + '"]'));
        marker.id = id;
        var paint = styles.get(element).paint;
        [marker].concat([].slice.call(marker.querySelectorAll('*'))).forEach(function (part) {
          ['fill', 'stroke'].forEach(function (attribute) {
            var value = part.style.getPropertyValue(attribute);
            var declared = part.getAttribute(attribute);
            if (declared === 'context-stroke' || declared === 'context-fill') value = declared;
            if (value === 'context-stroke' || value === 'context-fill') {
              var explicit = paint[value === 'context-stroke' ? 'stroke' : 'fill'];
              part.style.setProperty(attribute, explicit);
              part.setAttribute(attribute, explicit);
            }
          });
        });
        definitions.appendChild(marker);
        copies[index].setAttribute(property, 'url(#' + id + ')');
        copies[index].style.setProperty(property, 'url(#' + id + ')');
      });
    });
    clone.setAttribute('xmlns', NS);
    clone.setAttribute('viewBox', [box.x, box.y, box.width, box.height].join(' '));
    clone.setAttribute('width', box.width);
    clone.setAttribute('height', box.height);
    clone.style.setProperty('width', box.width + 'px');
    clone.style.setProperty('height', box.height + 'px');
    clone.style.setProperty('max-width', 'none');
    return {
      svg: new XMLSerializer().serializeToString(clone),
      box: { x: box.x, y: box.y, width: box.width, height: box.height },
      text: text
    };
  }

  async function renderSvg(svg, options) {
    options = options || {};
    if (!svg || svg.namespaceURI !== NS || svg.localName !== 'svg') {
      throw new Error('PNG export requires an SVG element.');
    }
    // Freeze the selected appearance before the first await.
    var saved = snapshot(svg, options);
    if (document.fonts) await document.fonts.ready;
    var sourceUrl;
    try {
      sourceUrl = URL.createObjectURL(new Blob([saved.svg], { type: 'image/svg+xml;charset=utf-8' }));
      var image = await new Promise(function (resolve, reject) {
        var loaded = new Image();
        loaded.onload = function () { resolve(loaded); };
        loaded.onerror = function () { reject(new Error('Could not render the SVG for PNG export.')); };
        loaded.src = sourceUrl;
      });
      var scale = 4;
      var canvas = document.createElement('canvas');
      canvas.width = Math.ceil(saved.box.width * scale);
      canvas.height = Math.ceil(saved.box.height * scale);
      var context = canvas.getContext('2d');
      if (!context) throw new Error('Canvas is unavailable.');
      if (!options.transparent) {
        context.fillStyle = '#ffffff';
        context.fillRect(0, 0, canvas.width, canvas.height);
      }
      context.drawImage(image, 0, 0, saved.box.width * scale, saved.box.height * scale);
      saved.text.forEach(function (label) {
        if (label.opacity <= 0 || label.fill === 'none') return;
        context.save();
        context.scale(scale, scale);
        context.translate(-saved.box.x, -saved.box.y);
        context.transform.apply(context, label.matrix);
        context.font = label.font;
        context.fillStyle = label.fill;
        context.globalAlpha = label.opacity;
        context.textAlign = label.anchor === 'middle' ? 'center' : label.anchor === 'end' ? 'right' : 'left';
        context.textBaseline = label.baseline === 'middle' || label.baseline === 'central' ? 'middle' : 'alphabetic';
        context.direction = label.direction;
        if ('letterSpacing' in context) context.letterSpacing = label.spacing === 'normal' ? '0px' : label.spacing;
        context.fillText(label.value, label.x, label.y);
        context.restore();
      });
      return canvas;
    } finally {
      if (sourceUrl) URL.revokeObjectURL(sourceUrl);
    }
  }

  async function downloadCanvas(canvas, filename) {
    var downloadUrl;
    var link;
    try {
      var png = await new Promise(function (resolve, reject) {
        canvas.toBlob(function (blob) {
          if (blob) resolve(blob);
          else reject(new Error('Could not create the PNG.'));
        }, 'image/png');
      });
      downloadUrl = URL.createObjectURL(png);
      link = document.createElement('a');
      link.href = downloadUrl;
      link.download = filename || 'figure.png';
      document.body.appendChild(link);
      link.click();
      // The browser may read the download URL after click() has returned.
      var completedUrl = downloadUrl;
      setTimeout(function () { URL.revokeObjectURL(completedUrl); }, 10000);
      downloadUrl = null;
    } finally {
      if (link) link.remove();
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    }
  }

  async function readyImage(image) {
    if (!image.complete) {
      await new Promise(function (resolve, reject) {
        var timeout;
        function cleanup() {
          image.removeEventListener('load', loaded);
          image.removeEventListener('error', failed);
          clearTimeout(timeout);
        }
        function loaded() { cleanup(); resolve(); }
        function failed() { cleanup(); reject(new Error('A paper cover could not be loaded.')); }
        image.addEventListener('load', loaded);
        image.addEventListener('error', failed);
        timeout = setTimeout(failed, 15000);
      });
    }
    if (!image.naturalWidth || !image.naturalHeight) {
      throw new Error('A paper cover is missing.');
    }
    if (image.decode) await image.decode();
  }

  function coverDataUrl(image, scale) {
    var bounds = image.getBoundingClientRect();
    var canvas = document.createElement('canvas');
    canvas.width = Math.min(image.naturalWidth, Math.ceil(bounds.width * scale));
    canvas.height = Math.ceil(canvas.width * image.naturalHeight / image.naturalWidth);
    var context = canvas.getContext('2d');
    if (!context || !canvas.width || !canvas.height) throw new Error('A paper cover is not visible.');
    context.drawImage(image, 0, 0, canvas.width, canvas.height);
    // Inline images eliminate a second fetch and fail here if a cover is unreadable.
    return canvas.toDataURL('image/png');
  }

  window.exportOverviewPng = async function (root, filename) {
    var grid = root && root.querySelector('.ep3-grid');
    var svg = root && root.querySelector('.ep3-svg');
    if (!grid || !svg) throw new Error('The overview is unavailable.');
    if (typeof window.html2canvas !== 'function') throw new Error('The PNG renderer is unavailable.');
    var selected = root.dataset.activeStage;
    if (selected === 'all') selected = null;
    var covers = [].slice.call(grid.querySelectorAll('img'));
    // renderSvg snapshots paint and label positions synchronously, before awaits.
    var prepared = await Promise.all([renderSvg(svg), Promise.all(covers.map(readyImage))]);
    var diagramData = prepared[0].toDataURL('image/png');
    var scale = 4;
    var coverData = covers.map(function (image) { return coverDataUrl(image, scale); });
    var coverBounds = covers.map(function (image) { return image.getBoundingClientRect(); });
    var gridBounds = grid.getBoundingClientRect();
    var svgBounds = svg.getBoundingClientRect();
    var parts = [root.querySelector('.ep3-left'), svg, root.querySelector('.ep3-right')];
    if (parts.some(function (part) { return !part; })) throw new Error('The overview is incomplete.');
    var bounds = parts.map(function (part) { return part.getBoundingClientRect(); });
    var padding = 12;
    var left = Math.min.apply(null, bounds.map(function (box) { return box.left; })) - padding;
    var top = Math.min.apply(null, bounds.map(function (box) { return box.top; })) - padding;
    var right = Math.max.apply(null, bounds.map(function (box) { return box.right; })) + padding;
    var bottom = Math.max.apply(null, bounds.map(function (box) { return box.bottom; })) + padding;
    if (!(right > left && bottom > top)) throw new Error('The overview must be visible before exporting.');
    var columns = getComputedStyle(grid).gridTemplateColumns;
    var canvas, clonedFrame;
    try {
      canvas = await window.html2canvas(grid, {
        backgroundColor: '#ffffff',
        scale: scale,
        x: left - gridBounds.left,
        y: top - gridBounds.top,
        width: Math.ceil(right - left),
        height: Math.ceil(bottom - top),
        windowWidth: window.innerWidth,
        windowHeight: window.innerHeight,
        scrollX: window.scrollX,
        scrollY: window.scrollY,
        foreignObjectRendering: false,
        allowTaint: false,
        logging: false,
        imageTimeout: 15000,
        removeContainer: true,
        onclone: async function (clonedDocument, copy) {
          clonedFrame = clonedDocument.defaultView.frameElement;
          // Freeze the measured columns while keeping the existing vertical layout.
          copy.style.width = gridBounds.width + 'px';
          copy.style.gridTemplateColumns = columns;
          [copy].concat([].slice.call(copy.querySelectorAll('*'))).forEach(function (element) {
            element.style.transition = 'none';
            element.style.animation = 'none';
          });
          copy.querySelectorAll('.ep3-actions, .ep3-hint, .ep3-export-status').forEach(function (element) {
            element.style.visibility = 'hidden';
          });
          copy.querySelectorAll('.ep3-stage, .ep3-pgroup').forEach(function (element) {
            var active = element.dataset.stage === selected;
            var showStage = selected === 'agents' && element.classList.contains('ep3-stage');
            var dim = !!selected && !active && !showStage;
            element.classList.toggle('act', active);
            element.classList.toggle('dim', dim);
            element.style.opacity = dim ? '0.3' : '1';
          });
          var copiedCovers = [].slice.call(copy.querySelectorAll('img'));
          if (copiedCovers.length !== coverData.length) throw new Error('The paper covers changed during export.');
          copiedCovers.forEach(function (image, index) {
            image.removeAttribute('srcset');
            image.src = coverData[index];
            image.style.width = coverBounds[index].width + 'px';
            image.style.height = coverBounds[index].height + 'px';
          });
          var replacement = clonedDocument.createElement('img');
          replacement.className = 'ep3-svg';
          replacement.alt = 'Retrieve, Summarize, Verify diagram';
          replacement.src = diagramData;
          replacement.style.cssText = 'display:block;flex-shrink:0;margin:0 auto;max-width:none;width:' + svgBounds.width + 'px;height:' + svgBounds.height + 'px;';
          copy.querySelector('.ep3-svg').replaceWith(replacement);
          // Capturing the overview must work even when it extends below the screen.
          for (var ancestor = copy.parentElement; ancestor; ancestor = ancestor.parentElement) {
            ancestor.style.overflow = 'visible';
            ancestor.style.clipPath = 'none';
            ancestor.style.contain = 'none';
          }
          await Promise.all([replacement].concat(copiedCovers).map(readyImage));
          if (clonedDocument.fonts) await clonedDocument.fonts.ready;
        }
      });
    } finally {
      // html2canvas only removes its clone automatically on successful renders.
      if (clonedFrame) clonedFrame.remove();
    }
    await downloadCanvas(canvas, filename || 'retrieve-summarize-verify-overview.png');
  };

  window.exportEvaluationPng = async function (section, filename) {
    var stage = section && section.querySelector('.ib-stage');
    var svg = section && section.querySelector('.ib-svg');
    if (!stage || !svg) throw new Error('The evaluation figure is unavailable.');
    if (typeof window.html2canvas !== 'function') throw new Error('The PNG renderer is unavailable.');
    var covers = [].slice.call(stage.querySelectorAll('img'));
    if (document.fonts) await document.fonts.ready;
    await Promise.all(covers.map(readyImage));
    var svgPadding = 24;
    var diagram = await renderSvg(svg, { transparent: true, freezeTransforms: true, padding: svgPadding });
    var diagramData = diagram.toDataURL('image/png');
    var scale = 4;
    var coverData = covers.map(function (image) { return coverDataUrl(image, scale); });
    var coverBounds = covers.map(function (image) { return image.getBoundingClientRect(); });
    var sectionBounds = section.getBoundingClientRect();
    var stageBounds = stage.getBoundingClientRect();
    var svgBounds = svg.getBoundingClientRect();
    var viewBox = svg.viewBox.baseVal;
    var unit = Math.min(svgBounds.width / viewBox.width, svgBounds.height / viewBox.height);
    var columns = getComputedStyle(stage).gridTemplateColumns;
    var parts = [svg, stage.querySelector('.ib-panel')].concat([].slice.call(stage.querySelectorAll('.ib-wlab')));
    var bounds = parts.filter(function (part) { return part && part.getClientRects().length; })
      .map(function (part) { return part.getBoundingClientRect(); });
    // The water spans the screen, so crop to content, never its decorative bounds.
    var padding = 24;
    var left = Math.min.apply(null, bounds.map(function (box) { return box.left; })) - padding;
    var top = Math.min.apply(null, bounds.map(function (box) { return box.top; })) - padding;
    var right = Math.max.apply(null, bounds.map(function (box) { return box.right; })) + padding;
    var bottom = Math.max.apply(null, bounds.map(function (box) { return box.bottom; })) + padding;
    var selected = stage.dataset.highlight;
    var canvas, clonedFrame;
    try {
      canvas = await window.html2canvas(section, {
        backgroundColor: '#f9fbfd', scale: scale,
        x: left - sectionBounds.left, y: top - sectionBounds.top,
        width: Math.ceil(right - left), height: Math.ceil(bottom - top),
        windowWidth: window.innerWidth, windowHeight: window.innerHeight,
        scrollX: window.scrollX, scrollY: window.scrollY,
        foreignObjectRendering: false, allowTaint: false, logging: false,
        imageTimeout: 15000, removeContainer: true,
        onclone: async function (clonedDocument, copy) {
          clonedFrame = clonedDocument.defaultView.frameElement;
          copy.style.width = sectionBounds.width + 'px';
          copy.style.height = sectionBounds.height + 'px';
          var copiedStage = copy.querySelector('.ib-stage');
          copiedStage.style.width = stageBounds.width + 'px';
          copiedStage.style.gridTemplateColumns = columns;
          [copy].concat([].slice.call(copy.querySelectorAll('*'))).forEach(function (element) {
            element.style.transition = 'none';
            element.style.animation = 'none';
            element.style.outline = 'none';
          });
          copy.querySelector('.ib-tools').style.visibility = 'hidden';
          copy.querySelector('.wrap').style.visibility = 'hidden';
          copiedStage.querySelectorAll('.ib-group').forEach(function (group) {
            group.style.opacity = selected && group.dataset.key !== selected ? '0.34' : '1';
          });
          var copiedCovers = [].slice.call(copiedStage.querySelectorAll('img'));
          copiedCovers.forEach(function (image, index) {
            image.removeAttribute('srcset');
            image.src = coverData[index];
            image.style.width = coverBounds[index].width + 'px';
            image.style.height = coverBounds[index].height + 'px';
          });
          // Keep the SVG's layout box while allowing the expanded slices to
          // extend into a transparent raster margin without clipping the apex.
          var frame = clonedDocument.createElement('div');
          frame.className = 'ib-svg';
          frame.style.width = svgBounds.width + 'px';
          frame.style.height = svgBounds.height + 'px';
          var replacement = clonedDocument.createElement('img');
          replacement.src = diagramData;
          replacement.style.cssText = 'position:absolute;max-width:none;left:' + ((svgBounds.width - viewBox.width * unit) / 2 - svgPadding * unit) +
            'px;top:' + ((svgBounds.height - viewBox.height * unit) / 2 - svgPadding * unit) +
            'px;width:' + ((viewBox.width + svgPadding * 2) * unit) + 'px;height:' + ((viewBox.height + svgPadding * 2) * unit) + 'px;';
          frame.appendChild(replacement);
          copiedStage.querySelector('.ib-svg').replaceWith(frame);
          for (var ancestor = copy; ancestor; ancestor = ancestor.parentElement) {
            ancestor.style.overflow = 'visible';
            ancestor.style.clipPath = 'none';
            ancestor.style.contain = 'none';
          }
          await Promise.all([replacement].concat(copiedCovers).map(readyImage));
          if (clonedDocument.fonts) await clonedDocument.fonts.ready;
        }
      });
    } finally {
      if (clonedFrame) clonedFrame.remove();
    }
    await downloadCanvas(canvas, filename || 'medical-ai-evaluation-overview.png');
  };
})();
