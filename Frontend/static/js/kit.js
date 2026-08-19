/* ==========================================================================
   SolarSage — shared front-end runtime.

   GSAP + ScrollTrigger choreograph anything tied to scroll position; Motion
   (Framer Motion's vanilla build) drives the spring-based micro-interactions,
   because pointer-following wants a spring and not a tween. Everything degrades
   to a plain, readable page when JavaScript or motion is unavailable.
   ========================================================================== */

(function () {
  'use strict';

  var gsap = window.gsap;
  var Motion = window.Motion;
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  if (gsap) {
    gsap.registerPlugin.apply(
      gsap,
      [window.ScrollTrigger, window.SplitText, window.DrawSVGPlugin].filter(Boolean)
    );
    gsap.defaults({ ease: 'power3.out', duration: 0.9 });
  }

  var SS = (window.SS = {
    gsap: gsap,
    Motion: Motion,
    reduced: reduced,
  });

  /* ---------------------------------------------------------------- utils */

  SS.esc = function (value) {
    return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  };

  SS.data = function (id, fallback) {
    var node = document.getElementById(id);
    if (!node) return fallback;
    try {
      return JSON.parse(node.textContent);
    } catch (e) {
      return fallback;
    }
  };

  SS.fmt = {
    pct: function (fraction, digits) {
      return fraction == null ? '—' : (fraction * 100).toFixed(digits == null ? 1 : digits) + '%';
    },
    ml: function (value) {
      return value == null ? '—' : Math.round(value).toLocaleString() + ' ml';
    },
    stamp: function (iso) {
      return !iso ? 'never' : String(iso).slice(0, 19).replace('T', ' ');
    },
    words: function (value) {
      return String(value == null ? '' : value).replace(/_/g, ' ');
    },
  };

  /* -------------------------------------------------------------- requests */

  SS.request = function (url, options) {
    options = options || {};
    var init = {
      method: options.method || 'GET',
      headers: { 'X-Requested-With': 'fetch', Accept: 'application/json' },
    };
    if (options.body) {
      init.headers['Content-Type'] = 'application/json';
      init.body = JSON.stringify(options.body);
    }
    return fetch(url, init)
      .then(function (response) {
        return response
          .json()
          .catch(function () {
            return {};
          })
          .then(function (data) {
            return { ok: response.ok, status: response.status, data: data };
          });
      })
      .catch(function (error) {
        return { ok: false, status: 0, data: { error: error.message || 'Network request failed' } };
      });
  };

  /** Runs an async action with the button locked and labelled. */
  SS.busy = function (button, label, run) {
    if (!button) return run();
    var original = button.innerHTML;
    var iconOnly = button.classList.contains('btn--icon');
    button.setAttribute('aria-busy', 'true');
    button.innerHTML =
      '<span class="spinner" aria-hidden="true"></span>' + (iconOnly ? '' : SS.esc(label));
    return Promise.resolve(run()).finally(function () {
      button.removeAttribute('aria-busy');
      button.innerHTML = original;
    });
  };

  /* ---------------------------------------------------------------- toasts */

  function toastLayer() {
    var layer = document.querySelector('.toasts');
    if (!layer) {
      layer = document.createElement('div');
      layer.className = 'toasts';
      layer.setAttribute('role', 'status');
      layer.setAttribute('aria-live', 'polite');
      document.body.appendChild(layer);
    }
    return layer;
  }

  SS.toast = function (message, options) {
    options = options || {};
    var kind = options.type || 'success';
    var titles = { success: 'Done', error: 'Not done', info: 'Note' };
    var node = document.createElement('div');
    node.className = 'toast toast--' + kind;
    node.innerHTML =
      '<div class="toast__body"><div class="toast__title">' +
      SS.esc(options.title || titles[kind] || 'Note') +
      '</div><div>' +
      SS.esc(message) +
      '</div></div><button class="toast__close" type="button" aria-label="Dismiss">&times;</button>';

    toastLayer().appendChild(node);

    var dismiss = function () {
      if (!node.isConnected) return;
      if (Motion && !reduced) {
        Motion.animate(node, { opacity: 0, x: 24 }, { duration: 0.25 }).finished.then(function () {
          node.remove();
        });
      } else {
        node.remove();
      }
    };

    node.querySelector('.toast__close').addEventListener('click', dismiss);

    if (Motion && !reduced) {
      Motion.animate(
        node,
        { opacity: [0, 1], x: [40, 0], scale: [0.96, 1] },
        { type: 'spring', stiffness: 420, damping: 32 }
      );
    }
    setTimeout(dismiss, options.duration || (kind === 'error' ? 8000 : 5000));
    return node;
  };

  /* --------------------------------------------------------------- confirm */

  /** window.confirm, replaced by something that matches the rest of the console. */
  SS.confirm = function (options) {
    return new Promise(function (resolve) {
      var dialog = document.createElement('dialog');
      dialog.className = 'dialog dialog--ask';
      dialog.innerHTML =
        '<div class="dialog__head"><h2 class="panel__title">' +
        SS.esc(options.title) +
        '</h2></div><div class="dialog__body"><p class="lede" style="font-size:1rem">' +
        SS.esc(options.message) +
        '</p><div class="row row--end" style="margin-top:1.75rem;justify-content:flex-end">' +
        '<button class="btn btn--sm" data-act="cancel" type="button">Cancel</button>' +
        '<button class="btn btn--sm ' +
        (options.danger ? 'btn--danger' : 'btn--sun') +
        '" data-act="go" type="button">' +
        SS.esc(options.confirmLabel || 'Continue') +
        '</button></div></div>';

      document.body.appendChild(dialog);
      dialog.showModal();
      dialog.querySelector('[data-act="go"]').focus();

      if (Motion && !reduced) {
        Motion.animate(
          dialog,
          { opacity: [0, 1], y: [12, 0], scale: [0.98, 1] },
          { type: 'spring', stiffness: 400, damping: 34 }
        );
      }

      var finish = function (value) {
        dialog.close();
        dialog.remove();
        resolve(value);
      };
      dialog.querySelector('[data-act="cancel"]').addEventListener('click', function () {
        finish(false);
      });
      dialog.querySelector('[data-act="go"]').addEventListener('click', function () {
        finish(true);
      });
      dialog.addEventListener('cancel', function (event) {
        event.preventDefault();
        finish(false);
      });
    });
  };

  /* ---------------------------------------------------------------- reveal */

  /** Sections arrive as the scroll reaches them: a short rise, never a bounce. */
  SS.reveal = function (root) {
    var targets = (root || document).querySelectorAll('[data-reveal]');
    if (!targets.length) return;
    if (!gsap || reduced) {
      targets.forEach(function (el) {
        el.style.opacity = 1;
      });
      return;
    }

    targets.forEach(function (el) {
      var mode = el.getAttribute('data-reveal') || 'up';
      var delay = parseFloat(el.getAttribute('data-reveal-delay') || 0);
      var from = { opacity: 0 };
      if (mode === 'up') from.y = 28;
      if (mode === 'left') from.x = -28;
      if (mode === 'right') from.x = 28;
      if (mode === 'scale') from.scale = 0.96;

      gsap.set(el, from);
      gsap.to(el, {
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
        duration: 1,
        delay: delay,
        scrollTrigger: { trigger: el, start: 'top 88%', once: true },
      });
    });
  };

  /** Group children of [data-stagger] so a grid lands as one gesture. */
  SS.stagger = function (root) {
    var groups = (root || document).querySelectorAll('[data-stagger]');
    groups.forEach(function (group) {
      var items = group.children;
      if (!items.length) return;
      if (!gsap || reduced) return;
      gsap.from(items, {
        opacity: 0,
        y: 22,
        duration: 0.85,
        stagger: parseFloat(group.getAttribute('data-stagger')) || 0.07,
        scrollTrigger: { trigger: group, start: 'top 86%', once: true },
      });
    });
  };

  /* -------------------------------------------------------------- counters */

  /** Numbers count to their real value once, when they scroll into view. */
  SS.counters = function (root) {
    var nodes = (root || document).querySelectorAll('[data-count]');
    nodes.forEach(function (node) {
      var target = parseFloat(node.getAttribute('data-count'));
      if (isNaN(target)) return;
      var decimals = parseInt(node.getAttribute('data-decimals') || '0', 10);
      var prefix = node.getAttribute('data-prefix') || '';
      var suffix = node.getAttribute('data-suffix') || '';
      var write = function (value) {
        node.textContent =
          prefix +
          value.toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
          }) +
          suffix;
      };

      if (!gsap || reduced) return write(target);

      // Zeroing here would leave every below-the-fold counter reading 0 until it
      // was scrolled to, so the real value stays put until the tween starts.
      var state = { value: 0 };
      gsap.to(state, {
        value: target,
        duration: 1.4,
        ease: 'power2.out',
        scrollTrigger: { trigger: node, start: 'top 96%', once: true },
        onStart: function () {
          write(0);
        },
        onUpdate: function () {
          write(state.value);
        },
      });
    });
  };

  /* ----------------------------------------------------- pointer reactions */

  /** Primary actions lean toward the cursor — a spring, so it settles honestly. */
  SS.magnetic = function (root) {
    if (!Motion || reduced || window.matchMedia('(hover: none)').matches) return;
    (root || document).querySelectorAll('[data-magnetic]').forEach(function (el) {
      var strength = parseFloat(el.getAttribute('data-magnetic')) || 0.35;
      var spring = { type: 'spring', stiffness: 260, damping: 18, mass: 0.4 };

      el.addEventListener('pointermove', function (event) {
        var box = el.getBoundingClientRect();
        Motion.animate(
          el,
          {
            x: (event.clientX - (box.left + box.width / 2)) * strength,
            y: (event.clientY - (box.top + box.height / 2)) * strength,
          },
          spring
        );
      });
      el.addEventListener('pointerleave', function () {
        Motion.animate(el, { x: 0, y: 0 }, spring);
      });
    });
  };

  /** Cards tip a couple of degrees under the pointer, like glass catching light. */
  SS.tilt = function (root) {
    if (!Motion || reduced || window.matchMedia('(hover: none)').matches) return;
    (root || document).querySelectorAll('[data-tilt]').forEach(function (el) {
      var max = parseFloat(el.getAttribute('data-tilt')) || 6;
      var spring = { type: 'spring', stiffness: 200, damping: 20 };
      el.style.transformStyle = 'preserve-3d';

      el.addEventListener('pointermove', function (event) {
        var box = el.getBoundingClientRect();
        var px = (event.clientX - box.left) / box.width - 0.5;
        var py = (event.clientY - box.top) / box.height - 0.5;
        el.style.setProperty('--spot-x', ((px + 0.5) * 100).toFixed(1) + '%');
        el.style.setProperty('--spot-y', ((py + 0.5) * 100).toFixed(1) + '%');
        Motion.animate(el, { rotateY: px * max, rotateX: -py * max }, spring);
      });
      el.addEventListener('pointerleave', function () {
        Motion.animate(el, { rotateY: 0, rotateX: 0 }, spring);
      });
    });
  };

  /* -------------------------------------------------------- scroll progress */

  SS.scrollProgress = function () {
    var bar = document.querySelector('[data-scroll-progress]');
    if (!bar || !gsap || reduced) return;
    gsap.to(bar, {
      scaleX: 1,
      ease: 'none',
      scrollTrigger: { start: 0, end: 'max', scrub: 0.3 },
    });
  };

  /* ------------------------------------------------------------------ boot */

  function boot() {
    document.documentElement.classList.add('js');
    SS.reveal();
    SS.stagger();
    SS.counters();
    SS.magnetic();
    SS.tilt();
    SS.scrollProgress();

    (SS.data('flash-messages', []) || []).forEach(function (item) {
      SS.toast(item.message, { type: item.category === 'error' ? 'error' : 'success' });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
