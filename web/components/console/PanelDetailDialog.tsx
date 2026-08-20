"use client";

import { useEffect, useRef, useState } from "react";
import { loadPanelDetailAction } from "@/app/actions";
import { Icon } from "@/components/ui/Icon";
import { animate, prefersReducedMotion } from "@/lib/motion";
import { ml, pct, reading as readingText, stamp, titleCase, words } from "@/lib/format";
import type { PanelDetail } from "@/lib/types";

/**
 * Everything recorded about one panel: its current state, the last reading from
 * its sensor node, and the two histories that explain how it got there. Loaded
 * when the drawer opens rather than with the page — a table of ten panels
 * should not fetch ten histories nobody asked for.
 */
export function PanelDetailDialog({
  panelId,
  onClose,
}: {
  panelId: string;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [detail, setDetail] = useState<PanelDetail | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    dialog.showModal();
    if (!prefersReducedMotion()) {
      animate(dialog, { opacity: [0, 1], y: [14, 0] }, { type: "spring", stiffness: 380, damping: 34 });
    }
  }, []);

  useEffect(() => {
    let live = true;
    setDetail(null);
    setError(null);
    loadPanelDetailAction(panelId).then((result) => {
      if (!live) return;
      if (result.ok) setDetail(result.detail);
      else setError(result.message);
    });
    return () => {
      live = false;
    };
  }, [panelId]);

  const panel = detail?.panel;
  const reading = detail?.telemetry;

  return (
    <dialog
      ref={ref}
      className="dialog"
      aria-labelledby="panel-detail-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <div className="dialog__head">
        <h2 className="panel__title" id="panel-detail-title">
          {words(panelId)}
        </h2>
        <button className="btn btn--sm btn--icon" type="button" aria-label="Close" onClick={onClose}>
          <Icon name="close" size={15} />
        </button>
      </div>

      <div className="dialog__body">
        {error ? (
          <p className="note note--error">{error}</p>
        ) : !detail ? (
          <p className="empty">
            <span className="spinner" /> Loading panel history…
          </p>
        ) : (
          <>
            <div className="detail__cols">
              <section>
                <h3 className="label">Current state</h3>
                <Facts
                  rows={[
                    ["Status", titleCase(panel?.status ?? "unknown")],
                    ["Dust coverage", pct(panel?.dust_level)],
                    ["Confidence", pct(panel?.confidence)],
                    ["Last analysed", stamp(panel?.last_analysed)],
                    ["Last washed", panel?.last_cleaned ?? "never"],
                    ["Image fixture", panel?.image_available ? "present" : "missing"],
                  ]}
                />
              </section>

              <section>
                <h3 className="label">Last hardware reading</h3>
                {reading ? (
                  <Facts
                    rows={[
                      ["Efficiency", readingText(reading.efficiency, "%")],
                      ["Cell temperature", readingText(reading.temperature, "°C")],
                      ["Humidity", readingText(reading.humidity, "%")],
                      ["Spray interval", `${reading.spray_interval}s`],
                      ["Power (raw)", String(reading.power)],
                      ["Light (raw)", String(reading.light)],
                    ]}
                  />
                ) : (
                  <p className="text-faint">No telemetry recorded for this panel.</p>
                )}
              </section>
            </div>

            <div className="detail__cols">
              <section>
                <h3 className="label">Recent analyses</h3>
                <ul className="detail__list">
                  {detail.status_history.length ? (
                    detail.status_history.map((entry) => (
                      <li className="detail__row" key={entry.id}>
                        <span className="mono">{stamp(entry.timestamp)}</span>
                        <span className="mono text-dust">{pct(entry.dust_level)} dust</span>
                      </li>
                    ))
                  ) : (
                    <li className="detail__row text-faint">Nothing analysed yet.</li>
                  )}
                </ul>
              </section>

              <section>
                <h3 className="label">Recent washes</h3>
                <ul className="detail__list">
                  {detail.cleaning_history.length ? (
                    detail.cleaning_history.map((entry) => (
                      <li className="detail__row" key={entry.id}>
                        <span className="mono">{stamp(entry.timestamp)}</span>
                        <span className={`mono ${entry.success ? "text-water" : "text-alarm"}`}>
                          {entry.success ? ml(entry.water_volume) : (entry.error_message ?? "failed")}
                        </span>
                      </li>
                    ))
                  ) : (
                    <li className="detail__row text-faint">Never washed.</li>
                  )}
                </ul>
              </section>
            </div>
          </>
        )}
      </div>
    </dialog>
  );
}

function Facts({ rows }: { rows: [string, string][] }) {
  return (
    <dl className="detail__facts">
      {rows.map(([term, value]) => (
        <div className="detail__fact" key={term}>
          <dt>{term}</dt>
          <dd className="mono">{value}</dd>
        </div>
      ))}
    </dl>
  );
}
