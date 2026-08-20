"use client";

import { useState } from "react";
import { ActionButton } from "./ActionButton";
import { PanelDetailDialog } from "./PanelDetailDialog";
import { analyzePanelAction, sprayPanelAction } from "@/app/actions";
import { Icon } from "@/components/ui/Icon";
import { Meter } from "@/components/ui/Meter";
import { Pill } from "@/components/ui/Pill";
import { pct, pctWhole, titleCase } from "@/lib/format";
import { panelState } from "@/lib/status";
import type { Panel } from "@/lib/types";

/**
 * Every panel as one row: state, coverage, confidence, when it was last washed
 * and what to do next. The only client state here is which panel's history is
 * open — everything a row *does* is a server action.
 */
export function PanelTable({
  panels,
  sprayDuration,
}: {
  panels: Panel[];
  sprayDuration: number;
}) {
  const [openPanel, setOpenPanel] = useState<string | null>(null);

  return (
    <>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Panel</th>
              <th>State</th>
              <th>Dust coverage</th>
              <th>Confidence</th>
              <th>Last washed</th>
              <th>Next step</th>
              <th>
                <span className="visually-hidden">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {panels.map((panel) => {
              const state = panelState(panel.status);
              return (
                <tr key={panel.id}>
                  <td>
                    <strong className="mono">{titleCase(panel.id)}</strong>
                  </td>
                  <td>
                    <Pill tone={state.pill}>{state.label}</Pill>
                  </td>
                  <td style={{ minWidth: "11rem" }}>
                    <div className="row" style={{ "--row-gap": "0.6rem" } as React.CSSProperties}>
                      <span className="mono tabular" style={{ width: "4.2rem" }}>
                        {panel.dust_level == null ? "—" : pct(panel.dust_level)}
                      </span>
                      <Meter
                        style={{ flex: 1 }}
                        value={(panel.dust_level ?? 0) * 100}
                        colour={state.colour}
                      />
                    </div>
                  </td>
                  <td className="mono tabular">{pctWhole(panel.confidence)}</td>
                  <td className="mono">{panel.last_cleaned}</td>
                  <td>
                    <span className={`${state.nextStepClass} mono`}>{state.nextStep}</span>
                  </td>
                  <td>
                    <div
                      className="row"
                      style={{ "--row-gap": "0.4rem", justifyContent: "flex-end" } as React.CSSProperties}
                    >
                      <ActionButton
                        perform={analyzePanelAction.bind(null, panel.id)}
                        label={`Analyse ${panel.id}`}
                        icon="scan"
                        iconOnly
                      />
                      <ActionButton
                        perform={sprayPanelAction.bind(null, panel.id)}
                        label={`Wash ${panel.id}`}
                        icon="droplet"
                        variant="water"
                        iconOnly
                        confirm={{
                          title: `Wash ${panel.id}?`,
                          message: `This opens the valve for ${sprayDuration} seconds — about ${sprayDuration * 20}ml of water.`,
                          confirmLabel: "Wash panel",
                        }}
                      />
                      <button
                        className="btn btn--sm btn--icon"
                        type="button"
                        title={`History for ${panel.id}`}
                        aria-label={`History for ${panel.id}`}
                        onClick={() => setOpenPanel(panel.id)}
                      >
                        <Icon name="info" size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {openPanel && <PanelDetailDialog panelId={openPanel} onClose={() => setOpenPanel(null)} />}
    </>
  );
}
