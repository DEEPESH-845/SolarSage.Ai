/* ==========================================================================
   SolarSage — console behaviour.

   One delegated click handler runs every action, every action reports through a
   toast, and anything that changed the array refreshes the live values in place
   instead of reloading the page under the operator.
   ========================================================================== */

(function () {
  'use strict';

  var SS = window.SS;
  if (!SS) return;

  var settings = SS.data('console-config', {}) || {};

  /* --------------------------------------------------------- live values */

  var STATUS_LABEL = {
    clean: 'Clean',
    moderate_dust: 'Moderate Dust',
    needs_cleaning: 'Needs Cleaning',
    unknown: 'Unknown',
  };

  var STATUS_COLOR = {
    clean: 'var(--water)',
    moderate_dust: 'var(--dust)',
    needs_cleaning: 'var(--alarm)',
    unknown: 'var(--ink-faint)',
  };

  function setPill(node, status, label) {
    if (!node) return;
    node.className = node.className.replace(/pill--[\w]+/g, '').trim() + ' pill--' + status;
    node.innerHTML = '<span class="pill__dot"></span>' + SS.esc(label);
  }

  /** The decision card follows the newest decision without a page reload. When
      the card is not on the page (or was rendered empty), a reload is the only
      way to show one, so do that once rather than rebuilding the template here. */
  function updateDecision(decision) {
    if (!decision || !decision.decision_id) return;
    var stamp = document.querySelector('[data-live="decision-stamp"]');
    if (!stamp) {
      if (document.querySelector('.dash__decision .empty')) window.location.reload();
      return;
    }
    if (stamp.getAttribute('data-decision-id') === decision.decision_id) return;

    stamp.setAttribute('data-decision-id', decision.decision_id);
    stamp.textContent = SS.fmt.stamp(decision.timestamp) + ' UTC';

    var set = function (name, text) {
      var node = document.querySelector('[data-live="' + name + '"]');
      if (node) node.textContent = text;
    };
    set('decision-action', decision.action);
    set('decision-panel', decision.panel_id);
    set('decision-dust', SS.fmt.pct(decision.dust_level));

    var card = document.querySelector('.dash__decision');
    if (card && SS.Motion && !SS.reduced) {
      SS.Motion.animate(card, { opacity: [0.55, 1] }, { duration: 0.5 });
    }
  }

  function refreshLive() {
    return SS.request('/api/live').then(function (result) {
      if (!result.ok) return result;
      var live = result.data;

      var statusPill = document.querySelector('[data-live="system-status"]');
      if (statusPill && live.health) {
        setPill(statusPill, live.health.status, live.health.status);
        statusPill.classList.add('pill--live');
      }

      var tank = document.querySelector('[data-live="water-tank"]');
      if (tank && live.health) tank.style.setProperty('--level', live.health.water_level + '%');

      var tankText = document.querySelector('[data-live="water-text"]');
      if (tankText && live.health) {
        tankText.textContent =
          live.health.water.remaining_ml + ' of ' + live.health.water.capacity_ml + ' ml';
      }

      document.querySelectorAll('[data-live="count"]').forEach(function (node) {
        var key = node.getAttribute('data-count-key');
        if (live.counts && live.counts[key] != null) node.textContent = live.counts[key];
      });

      updateDecision(live.latest_decision);

      (live.panels || []).forEach(function (panel) {
        var card = document.querySelector('[data-panel-card="' + panel.id + '"]');
        if (!card) return;
        setPill(
          card.querySelector('[data-live="panel-status"]'),
          panel.status === 'moderate_dust' ? 'moderate' : panel.status,
          STATUS_LABEL[panel.status] || panel.status
        );

        var dust = card.querySelector('[data-live="panel-dust"]');
        if (dust) {
          dust.innerHTML =
            panel.dust_level == null
              ? '—<span class="panelcard__unit">not analysed</span>'
              : (panel.dust_level * 100).toFixed(1) + '<span class="panelcard__unit">% dust</span>';
        }

        var meter = card.querySelector('[data-live="panel-meter"]');
        if (meter) {
          meter.style.setProperty('--value', ((panel.dust_level || 0) * 100).toFixed(1) + '%');
          meter.style.setProperty('--meter-color', STATUS_COLOR[panel.status]);
        }

        var cleaned = card.querySelector('[data-live="panel-cleaned"]');
        if (cleaned) cleaned.textContent = panel.last_cleaned;

        if (SS.Motion && !SS.reduced) {
          SS.Motion.animate(card, { scale: [0.995, 1] }, { type: 'spring', stiffness: 400, damping: 30 });
        }
      });

      return result;
    });
  }

  /* -------------------------------------------------------------- actions */

  /** Each action: how to ask, what to call, what to say. */
  var ACTIONS = {
    analyze: {
      label: 'Analysing',
      url: function (button) {
        return '/analyze/' + encodeURIComponent(button.getAttribute('data-panel'));
      },
    },
    spray: {
      label: 'Washing',
      confirm: function (button) {
        return {
          title: 'Wash ' + button.getAttribute('data-panel') + '?',
          message:
            'This opens the valve for ' +
            (settings.spray_duration || 5) +
            ' seconds — about ' +
            (settings.spray_duration || 5) * 20 +
            'ml of water.',
          confirmLabel: 'Wash panel',
        };
      },
      url: function (button) {
        return '/spray/' + encodeURIComponent(button.getAttribute('data-panel'));
      },
    },
    'analyze-all': { label: 'Analysing', url: '/api/quick-analyze' },
    'clean-dirty': {
      label: 'Washing',
      confirm: {
        title: 'Wash every dusty panel?',
        message: 'Only panels above the schedule threshold are sprayed. Clean panels are left alone.',
        confirmLabel: 'Wash them',
      },
      url: '/api/clean-dirty-panels',
    },
    'clean-all': {
      label: 'Washing',
      confirm: {
        title: 'Wash all panels?',
        message: 'Every panel is sprayed regardless of how dirty it is. This can empty the tank.',
        confirmLabel: 'Wash everything',
        danger: true,
      },
      url: '/api/emergency-clean-all',
    },
    refill: { label: 'Refilling', url: '/api/refill-tank' },
    'reset-settings': {
      label: 'Resetting',
      confirm: {
        title: 'Reset every setting?',
        message: 'Thresholds, schedule and notification settings all go back to their defaults.',
        confirmLabel: 'Reset',
        danger: true,
      },
      url: '/api/settings/reset',
      after: function () {
        window.location.reload();
      },
    },
  };

  function runAction(name, button) {
    var action = ACTIONS[name];
    if (!action) return;

    var ask = typeof action.confirm === 'function' ? action.confirm(button) : action.confirm;
    var url = typeof action.url === 'function' ? action.url(button) : action.url;

    var go = function () {
      return SS.busy(button, action.label + '…', function () {
        return SS.request(url, { method: 'POST' }).then(function (result) {
          var message =
            result.data.message || result.data.error || (result.ok ? 'Done.' : 'That did not work.');
          SS.toast(message, { type: result.ok ? 'success' : 'error' });

          if (result.data.failures && result.data.failures.length) {
            result.data.failures.forEach(function (failure) {
              SS.toast(failure.panel_id + ': ' + failure.error, { type: 'error' });
            });
          }
          if (result.ok && action.after) return action.after(result);
          if (result.ok) return refreshLive();
          return result;
        });
      });
    };

    if (ask) {
      SS.confirm(ask).then(function (confirmed) {
        if (confirmed) go();
      });
      return;
    }
    go();
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-action]');
    if (!button) return;
    var name = button.getAttribute('data-action');
    if (ACTIONS[name]) {
      event.preventDefault();
      runAction(name, button);
    }
  });

  /* --------------------------------------------------- panel detail drawer */

  function rowsOrEmpty(items, render, empty) {
    return items && items.length
      ? items.map(render).join('')
      : '<li class="detail__row text-faint">' + empty + '</li>';
  }

  function openPanelDetail(panelId) {
    var dialog = document.getElementById('panel-detail');
    if (!dialog) return;
    var body = dialog.querySelector('[data-detail-body]');
    var heading = dialog.querySelector('[data-detail-title]');

    heading.textContent = panelId.replace(/_/g, ' ');
    body.innerHTML = '<p class="empty"><span class="spinner"></span> Loading panel history…</p>';
    dialog.showModal();

    if (SS.Motion && !SS.reduced) {
      SS.Motion.animate(
        dialog,
        { opacity: [0, 1], y: [14, 0] },
        { type: 'spring', stiffness: 380, damping: 34 }
      );
    }

    SS.request('/api/panel/' + encodeURIComponent(panelId)).then(function (result) {
      if (!result.ok) {
        body.innerHTML =
          '<p class="note note--error">' + SS.esc(result.data.error || 'Could not load this panel.') + '</p>';
        return;
      }

      var data = result.data;
      var panel = data.panel || {};
      var reading = data.telemetry;

      var facts = [
        ['Status', SS.fmt.words(panel.status || 'unknown')],
        ['Dust coverage', SS.fmt.pct(panel.dust_level)],
        ['Confidence', SS.fmt.pct(panel.confidence)],
        ['Last analysed', SS.fmt.stamp(panel.last_analysed)],
        ['Last washed', panel.last_cleaned || 'never'],
        ['Image fixture', panel.image_available ? 'present' : 'missing'],
      ];

      var hardware = reading
        ? [
            ['Efficiency', reading.efficiency + '%'],
            ['Cell temperature', reading.temperature + '°C'],
            ['Humidity', reading.humidity + '%'],
            ['Spray interval', reading.spray_interval + 's'],
            ['Power (raw)', reading.power],
            ['Light (raw)', reading.light],
          ]
        : [];

      var asRows = function (pairs) {
        return pairs
          .map(function (pair) {
            return (
              '<div class="detail__fact"><dt>' +
              SS.esc(pair[0]) +
              '</dt><dd class="mono">' +
              SS.esc(pair[1]) +
              '</dd></div>'
            );
          })
          .join('');
      };

      body.innerHTML =
        '<div class="detail__cols">' +
        '<section><h3 class="label">Current state</h3><dl class="detail__facts">' +
        asRows(facts) +
        '</dl></section>' +
        '<section><h3 class="label">Last hardware reading</h3>' +
        (hardware.length
          ? '<dl class="detail__facts">' + asRows(hardware) + '</dl>'
          : '<p class="text-faint">No telemetry recorded for this panel.</p>') +
        '</section></div>' +
        '<div class="detail__cols">' +
        '<section><h3 class="label">Recent analyses</h3><ul class="detail__list">' +
        rowsOrEmpty(
          data.status_history,
          function (item) {
            return (
              '<li class="detail__row"><span class="mono">' +
              SS.esc(SS.fmt.stamp(item.timestamp)) +
              '</span><span class="mono text-dust">' +
              SS.esc(SS.fmt.pct(item.dust_level)) +
              ' dust</span></li>'
            );
          },
          'Nothing analysed yet.'
        ) +
        '</ul></section>' +
        '<section><h3 class="label">Recent washes</h3><ul class="detail__list">' +
        rowsOrEmpty(
          data.cleaning_history,
          function (item) {
            return (
              '<li class="detail__row"><span class="mono">' +
              SS.esc(SS.fmt.stamp(item.timestamp)) +
              '</span><span class="mono ' +
              (item.success ? 'text-water' : 'text-alarm') +
              '">' +
              SS.esc(item.success ? SS.fmt.ml(item.water_volume) : item.error_message || 'failed') +
              '</span></li>'
            );
          },
          'Never washed.'
        ) +
        '</ul></section></div>';
    });
  }

  document.addEventListener('click', function (event) {
    var trigger = event.target.closest('[data-detail]');
    if (!trigger) return;
    event.preventDefault();
    openPanelDetail(trigger.getAttribute('data-detail'));
  });

  var detailDialog = document.getElementById('panel-detail');
  if (detailDialog) {
    detailDialog.querySelector('[data-close]').addEventListener('click', function () {
      detailDialog.close();
    });
  }

  /* ------------------------------------------------------------- settings */

  var FIELDS = {
    dust_threshold: 'number',
    schedule_threshold: 'number',
    spray_duration: 'number',
    refresh_interval: 'number',
    water_pressure: 'text',
    alert_email: 'text',
    cleaning_frequency: 'text',
    preferred_time: 'text',
    auto_clean: 'bool',
    notifications: 'bool',
  };

  function collectSettings() {
    var values = {};
    Object.keys(FIELDS).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      values[id] =
        FIELDS[id] === 'bool' ? el.checked : FIELDS[id] === 'number' ? Number(el.value) : el.value;
    });
    return values;
  }

  /** Sliders paint their own track, and the threshold band underneath them. */
  function wireSliders() {
    var map = document.querySelector('.threshold-map');

    document.querySelectorAll('input[type="range"]').forEach(function (slider) {
      var output = document.querySelector('[data-output="' + slider.id + '"]');
      var band = slider.getAttribute('data-threshold');
      var paint = function () {
        var pct = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        slider.style.setProperty('--fill', pct + '%');
        if (output) output.textContent = slider.value + '%';
        if (map && band) map.style.setProperty('--' + band, slider.value + '%');
      };
      slider.addEventListener('input', paint);
      paint();
    });
  }

  function wireSettingsPage() {
    var saveButtons = document.querySelectorAll('[data-action="save-settings"]');
    if (!saveButtons.length) return;

    wireSliders();

    saveButtons.forEach(function (save) {
      save.addEventListener('click', function () {
        var values = collectSettings();
        if (values.schedule_threshold >= values.dust_threshold) {
          SS.toast('The schedule threshold has to stay below the immediate threshold.', { type: 'error' });
          return;
        }
        SS.busy(save, 'Saving…', function () {
          return SS.request('/api/settings', { method: 'POST', body: values }).then(function (result) {
            SS.toast(result.data.message || result.data.error || 'Could not save.', {
              type: result.ok ? 'success' : 'error',
            });
            if (result.ok) setTimeout(function () { window.location.reload(); }, 700);
          });
        });
      });
    });

    document.querySelectorAll('[data-action="toggle-mode"]').forEach(function (button) {
      button.addEventListener('click', function () {
        var mode = button.getAttribute('data-mode');
        SS.confirm({
          title: mode === 'paused' ? 'Pause cleaning?' : 'Resume cleaning?',
          message:
            mode === 'paused'
              ? 'Analysis keeps running, but no valve opens until the system is resumed.'
              : 'Washing becomes possible again, by hand and automatically.',
          confirmLabel: mode === 'paused' ? 'Pause' : 'Resume',
          danger: mode === 'paused',
        }).then(function (confirmed) {
          if (!confirmed) return;
          SS.busy(button, 'Working…', function () {
            return SS.request('/api/system-mode', { method: 'POST', body: { mode: mode } }).then(
              function (result) {
                SS.toast(result.data.message || result.data.error || 'Could not change the mode.', {
                  type: result.ok ? 'success' : 'error',
                });
                if (result.ok) setTimeout(function () { window.location.reload(); }, 700);
              }
            );
          });
        });
      });
    });
  }

  /* -------------------------------------------------------------- exports */

  function download(filename, content, mime) {
    var blob = new Blob([content], { type: mime });
    var url = URL.createObjectURL(blob);
    var link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(function () {
      URL.revokeObjectURL(url);
    }, 1000);
    SS.toast('Saved ' + filename, { type: 'info', title: 'Export' });
  }

  function today() {
    return new Date().toISOString().slice(0, 10);
  }

  function csvCell(value) {
    var text = value == null ? '' : String(value);
    return /[",\n]/.test(text) ? '"' + text.replace(/"/g, '""') + '"' : text;
  }

  var EXPORTS = {
    report: function (data) {
      download(
        'solarsage-report-' + today() + '.json',
        JSON.stringify(
          { generated_at: new Date().toISOString(), statistics: data.stats, panel_health: data.panel_health, recent_logs: data.logs },
          null,
          2
        ),
        'application/json'
      );
    },
    panels: function (data) {
      var lines = ['panel_id,status,dust_percent,confidence_percent,last_analysed,last_cleaned'];
      (data.panels || []).forEach(function (panel) {
        lines.push(
          [
            panel.id,
            panel.status,
            panel.dust_level == null ? '' : (panel.dust_level * 100).toFixed(1),
            panel.confidence == null ? '' : (panel.confidence * 100).toFixed(1),
            panel.last_analysed || '',
            panel.last_cleaned,
          ]
            .map(csvCell)
            .join(',')
        );
      });
      download('solarsage-panels-' + today() + '.csv', lines.join('\n'), 'text/csv');
    },
    logs: function (data) {
      var text = (data.logs || [])
        .map(function (log) {
          return '[' + log.timestamp + '] ' + log.level + ' ' + log.component + ': ' + log.message;
        })
        .join('\n');
      download('solarsage-logs-' + today() + '.txt', text || 'No log entries.', 'text/plain');
    },
  };

  document.addEventListener('click', function (event) {
    var button = event.target.closest('[data-export]');
    if (!button) return;
    var kind = button.getAttribute('data-export');

    if (kind === 'settings') {
      SS.busy(button, 'Exporting…', function () {
        return SS.request('/api/settings').then(function (result) {
          download('solarsage-settings-' + today() + '.json', JSON.stringify(result.data, null, 2), 'application/json');
        });
      });
      return;
    }

    SS.busy(button, 'Exporting…', function () {
      return SS.request('/api/system-reports').then(function (result) {
        if (!result.ok) return SS.toast('Could not build the export.', { type: 'error' });
        (EXPORTS[kind] || EXPORTS.report)(result.data);
      });
    });
  });

  /* ---------------------------------------------------------- log filter */

  function wireLogFilter() {
    var input = document.getElementById('log-filter');
    if (!input) return;
    var rows = Array.prototype.slice.call(document.querySelectorAll('[data-log-row]'));
    input.addEventListener('input', function () {
      var needle = input.value.toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {
        var match = row.getAttribute('data-log-row').indexOf(needle) !== -1;
        row.hidden = !match;
        if (match) shown++;
      });
      var count = document.getElementById('log-count');
      if (count) count.textContent = shown + ' of ' + rows.length;
    });
  }

  /* ------------------------------------------------------------ polling */

  function startPolling() {
    var seconds = Number(settings.refresh_interval || 0);
    if (!seconds || !document.querySelector('[data-live]')) return;
    setInterval(function () {
      if (!document.hidden) refreshLive();
    }, Math.max(5, seconds) * 1000);
  }

  /* --------------------------------------------------------------- boot */

  function boot() {
    wireSettingsPage();
    wireLogFilter();
    startPolling();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
