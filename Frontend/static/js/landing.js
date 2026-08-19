/* ==========================================================================
   SolarSage — landing page motion.

   The signature is the array itself: a canvas of photovoltaic modules whose
   soiling is the real dust coverage from the database, cleared by a spray pass
   that runs the same way the hardware does — left to right, once.
   ========================================================================== */

(function () {
  'use strict';

  var SS = window.SS || {};
  var gsap = window.gsap;
  var reduced = SS.reduced;

  /* ------------------------------------------------------------- the array */

  var WAFER = '#1c2a63';
  var WAFER_DEEP = '#0e1740';
  var BUSBAR = 'rgba(198, 208, 228, 0.3)';

  function dustPattern() {
    // Soiling is grain, not a wash of colour, so it gets a real noise tile.
    var tile = document.createElement('canvas');
    tile.width = tile.height = 72;
    var tctx = tile.getContext('2d');
    var image = tctx.createImageData(72, 72);
    for (var i = 0; i < image.data.length; i += 4) {
      var grain = Math.random();
      image.data[i] = 198 + grain * 34;
      image.data[i + 1] = 140 + grain * 40;
      image.data[i + 2] = 78 + grain * 34;
      // Sparse: soiling reads as a veil with texture, not a coat of paint.
      image.data[i + 3] = grain > 0.86 ? 130 : grain > 0.62 ? 46 : 12;
    }
    tctx.putImageData(image, 0, 0);
    return tile;
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  function Array2D(canvas, panels) {
    var ctx = canvas.getContext('2d');
    var grain = dustPattern();
    var pattern = ctx.createPattern(grain, 'repeat');
    var state = { sweep: -0.4, recover: 1, glint: 0 };
    var box = { w: 0, h: 0 };

    function resize() {
      var rect = canvas.getBoundingClientRect();
      var dpr = Math.min(window.devicePixelRatio || 1, 2);
      box.w = rect.width;
      box.h = rect.height;
      canvas.width = Math.max(1, Math.round(rect.width * dpr));
      canvas.height = Math.max(1, Math.round(rect.height * dpr));
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function drawModule(x, y, w, h, dust, index) {
      var cols = 6;
      var rows = 3;
      var pad = Math.max(4, w * 0.022);
      var cellW = (w - pad * (cols + 1)) / cols;
      var cellH = (h - pad * (rows + 1)) / rows;

      ctx.save();
      // frame
      ctx.fillStyle = 'rgba(6, 11, 28, 0.92)';
      roundRect(ctx, x, y, w, h, 6);
      ctx.fill();
      ctx.strokeStyle = 'rgba(198, 208, 228, 0.16)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // cells + busbars
      for (var r = 0; r < rows; r++) {
        for (var c = 0; c < cols; c++) {
          var cx = x + pad + c * (cellW + pad);
          var cy = y + pad + r * (cellH + pad);
          var grad = ctx.createLinearGradient(cx, cy, cx + cellW, cy + cellH);
          grad.addColorStop(0, WAFER);
          grad.addColorStop(1, WAFER_DEEP);
          ctx.fillStyle = grad;
          roundRect(ctx, cx, cy, cellW, cellH, 2);
          ctx.fill();

          ctx.strokeStyle = BUSBAR;
          ctx.lineWidth = 0.6;
          ctx.beginPath();
          ctx.moveTo(cx + cellW * 0.33, cy + 2);
          ctx.lineTo(cx + cellW * 0.33, cy + cellH - 2);
          ctx.moveTo(cx + cellW * 0.66, cy + 2);
          ctx.lineTo(cx + cellW * 0.66, cy + cellH - 2);
          ctx.moveTo(cx + 2, cy + cellH / 2);
          ctx.lineTo(cx + cellW - 2, cy + cellH / 2);
          ctx.stroke();
        }
      }

      // Dust, only ahead of the spray pass: a flat ochre veil for the loss of
      // contrast, grain on top for the texture. Both scale with real coverage.
      var sweepX = state.sweep * box.w;
      if (dust > 0.01) {
        // Two bands: still-dirty glass ahead of the nozzle, and glass behind it
        // that is clean now and soiling again at state.recover.
        [[x, Math.min(sweepX, x + w), state.recover], [Math.max(x, sweepX), x + w, 1]].forEach(
          function (band) {
            var from = band[0];
            var to = band[1];
            var strength = band[2];
            if (to - from <= 0.5 || strength <= 0.01) return;

            ctx.save();
            roundRect(ctx, x, y, w, h, 6);
            ctx.clip();
            ctx.beginPath();
            ctx.rect(from, y, to - from, h);
            ctx.clip();

            ctx.globalAlpha = Math.min(0.34, dust * 0.36) * strength;
            ctx.fillStyle = '#c4813c';
            ctx.fillRect(x, y, w, h);

            ctx.globalAlpha = Math.min(0.5, dust * 0.55) * strength;
            ctx.fillStyle = pattern;
            ctx.fillRect(x, y, w, h);
            ctx.restore();
          }
        );
      }

      // a low sheen that drifts, so the glass reads as glass
      ctx.save();
      roundRect(ctx, x, y, w, h, 6);
      ctx.clip();
      var edge = ctx.createLinearGradient(x, y, x, y + h * 0.35);
      edge.addColorStop(0, 'rgba(226, 236, 255, 0.14)');
      edge.addColorStop(1, 'rgba(226, 236, 255, 0)');
      ctx.fillStyle = edge;
      ctx.fillRect(x, y, w, h * 0.35);
      ctx.restore();

      ctx.save();
      roundRect(ctx, x, y, w, h, 6);
      ctx.clip();
      var sheenX = x + ((state.glint + index * 0.17) % 1.4 - 0.2) * w;
      var sheen = ctx.createLinearGradient(sheenX, y, sheenX + w * 0.42, y + h);
      sheen.addColorStop(0, 'rgba(255, 211, 122, 0)');
      sheen.addColorStop(0.5, 'rgba(255, 211, 122, 0.07)');
      sheen.addColorStop(1, 'rgba(255, 211, 122, 0)');
      ctx.fillStyle = sheen;
      ctx.fillRect(x, y, w, h);
      ctx.restore();

      ctx.restore();
    }

    function drawSpray() {
      var x = state.sweep * box.w;
      if (x < 0 || x > box.w) return;
      var band = ctx.createLinearGradient(x - 60, 0, x + 20, 0);
      band.addColorStop(0, 'rgba(53, 214, 195, 0)');
      band.addColorStop(0.7, 'rgba(53, 214, 195, 0.16)');
      band.addColorStop(1, 'rgba(233, 255, 252, 0.5)');
      ctx.fillStyle = band;
      ctx.fillRect(x - 60, 0, 62, box.h);
    }

    function render() {
      ctx.clearRect(0, 0, box.w, box.h);
      if (box.w < 10) return;

      // Two rows of two modules, weighted to the right of the viewport so the
      // headline keeps the left third to itself.
      var wide = box.w > 900;
      var left = box.w * (wide ? 0.54 : 0.08);
      var right = box.w * (wide ? 0.96 : 0.92);
      var width = right - left;
      var gap = width * 0.045;
      var modW = (width - gap) / 2;
      var modH = modW * 0.54;
      var top = box.h * (wide ? 0.16 : 0.3);

      ctx.save();
      ctx.translate(left + width / 2, top + modH);
      ctx.rotate(-0.035);
      ctx.translate(-(left + width / 2), -(top + modH));

      // The far row is drawn smaller and inset, so the array has depth without
      // needing a real perspective transform.
      for (var i = 0; i < 4; i++) {
        var col = i % 2;
        var row = Math.floor(i / 2);
        var shrink = row === 0 ? 0.88 : 1;
        var w = modW * shrink;
        var h = modH * shrink;
        ctx.globalAlpha = row === 0 ? 0.62 : 1;
        drawModule(
          left + col * (modW + gap) + (modW - w) / 2,
          top + row * (modH + gap),
          w,
          h,
          panels[i] == null ? 0.3 : panels[i],
          i
        );
        ctx.globalAlpha = 1;
      }
      drawSpray();
      ctx.restore();
    }

    return {
      resize: resize,
      render: render,
      state: state,
    };
  }

  function startArray() {
    var canvas = document.getElementById('wafer');
    if (!canvas) return null;

    var rows = SS.data('panel-data', []) || [];
    var dust = rows.map(function (row) {
      return row.dust_level == null ? 0.32 : Math.min(1, row.dust_level);
    });
    while (dust.length < 4) dust.push(0.28);

    var array = Array2D(canvas, dust);
    array.resize();
    array.render();

    if (reduced || !gsap) return { replay: function () {} };

    var visible = true;
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        visible = entries[0].isIntersecting;
      }).observe(canvas);
    }

    gsap.ticker.add(function () {
      if (!visible || document.hidden) return;
      array.state.glint += 0.0016;
      array.render();
    });

    var resizeTimer;
    window.addEventListener('resize', function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        array.resize();
        array.render();
      }, 120);
    });

    /** One honest cycle: the nozzle crosses, the glass is clean behind it, and
        then it starts soiling again — because that is what actually happens. */
    var cycle;
    function replay() {
      if (cycle) cycle.kill();
      cycle = gsap
        .timeline()
        .set(array.state, { recover: 0, sweep: -0.35 })
        .to(array.state, { sweep: 1.35, duration: 2.6, ease: 'power1.inOut' })
        .to(array.state, { recover: 1, duration: 3.4, ease: 'power1.in' }, '+=1.1')
        .set(array.state, { sweep: -0.4 });
    }

    gsap.delayedCall(1.1, replay);
    return { replay: replay };
  }

  /* ---------------------------------------------------------------- scenes */

  function heroIntro() {
    if (!gsap || reduced) return;
    var title = document.querySelector('.hero__title');

    // Built inside run(): a timeline created before the fonts resolve would have
    // played itself out before the tweens were ever added to it.
    var run = function () {
      var timeline = gsap.timeline({ defaults: { ease: 'power3.out' } });
      if (window.SplitText && title) {
        var split = new window.SplitText(title, { type: 'lines', mask: 'lines' });
        timeline.from(split.lines, { yPercent: 115, duration: 1.1, stagger: 0.09 }, 0);
      } else if (title) {
        timeline.from(title, { opacity: 0, y: 30 }, 0);
      }
      timeline
        .from('.hero__eyebrow', { opacity: 0, y: 12, duration: 0.8 }, 0.1)
        .from('.hero__lede', { opacity: 0, y: 18, duration: 0.9 }, 0.45)
        .from('.hero__actions > *', { opacity: 0, y: 16, duration: 0.7, stagger: 0.08, clearProps: 'transform' }, 0.6)
        .from('.readout', { opacity: 0, y: 20, duration: 0.8, stagger: 0.06, clearProps: 'transform' }, 0.75)
        .from('.hero__scroll', { opacity: 0, duration: 0.6 }, 1.1);
    };

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(run);
    } else {
      run();
    }
  }

  function stickyHeader() {
    var header = document.querySelector('.topline');
    if (!header) return;
    var apply = function () {
      header.classList.toggle('topline--stuck', window.scrollY > 40);
    };
    apply();
    window.addEventListener('scroll', apply, { passive: true });
  }

  function heroParallax() {
    if (!gsap || reduced) return;
    gsap.to('.hero__field', {
      yPercent: 14,
      ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
    gsap.to('.hero__inner', {
      yPercent: -6,
      opacity: 0.15,
      ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true },
    });
  }

  /** The two curves draw themselves, then the loss between them fills in. */
  function curveScene() {
    var figure = document.querySelector('.curve');
    if (!figure || !gsap || reduced) return;
    var clean = figure.querySelector('.curve__clean');
    var soiled = figure.querySelector('.curve__soiled');
    var loss = figure.querySelector('.curve__loss');

    var timeline = gsap.timeline({
      scrollTrigger: { trigger: figure, start: 'top 78%', once: true },
    });

    if (window.DrawSVGPlugin) {
      timeline
        .from(clean, { drawSVG: '0%', duration: 1.5, ease: 'power2.inOut' })
        .from(soiled, { drawSVG: '0%', duration: 1.5, ease: 'power2.inOut' }, 0.35);
    } else {
      timeline.from([clean, soiled], { opacity: 0, duration: 1, stagger: 0.3 });
    }
    timeline.to(loss, { opacity: 1, duration: 0.9 }, 1.1);
  }

  /** Each stage of the loop arrives as the reader gets to it. */
  function loopScene() {
    if (!gsap || reduced) return;
    gsap.from('.stage', {
      opacity: 0,
      y: 34,
      duration: 0.9,
      stagger: 0.12,
      scrollTrigger: { trigger: '.loop', start: 'top 80%', once: true },
    });
  }

  /** Efficiency rings fill from empty once they are on screen. */
  function ringScene() {
    var rings = document.querySelectorAll('.reading__arc');
    if (!rings.length || !gsap || reduced) return;
    rings.forEach(function (ring) {
      var target = ring.style.strokeDashoffset;
      ring.style.strokeDashoffset = '264';
      window.ScrollTrigger.create({
        trigger: ring,
        start: 'top 92%',
        once: true,
        onEnter: function () {
          ring.style.strokeDashoffset = target;
        },
      });
    });
  }

  /* ------------------------------------------------------------------ boot */

  function boot() {
    var array = startArray();
    heroIntro();
    stickyHeader();
    heroParallax();
    curveScene();
    loopScene();
    ringScene();

    var replayButton = document.getElementById('replay-cycle');
    if (replayButton && array) {
      replayButton.addEventListener('click', function () {
        array.replay();
        window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' });
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
