import { ActionButton } from "./ActionButton";
import { analyzePanelAction, sprayPanelAction } from "@/app/actions";
import { Meter } from "@/components/ui/Meter";
import { Tilt } from "@/components/ui/Motion";
import { Pill } from "@/components/ui/Pill";
import { pct, pctWhole, titleCase } from "@/lib/format";
import { panelState } from "@/lib/status";
import type { Panel } from "@/lib/types";

/** One panel on the dashboard: what it reads now, and the two things an
 *  operator can do about it. */
export function PanelCard({ panel, sprayDuration }: { panel: Panel; sprayDuration: number }) {
  const state = panelState(panel.status);
  const analysed = panel.dust_level != null;

  return (
    <Tilt className="card card--tight panelcard" max={6}>
      <header className="row row--between">
        <h3 className="panelcard__id mono">{titleCase(panel.id)}</h3>
        <Pill tone={state.pill}>{state.label}</Pill>
      </header>

      <p className="numeral numeral--md panelcard__dust">
        <span>{analysed ? pct(panel.dust_level) : "—"}</span>
        <span className="panelcard__unit">{analysed ? "dust" : "not analysed"}</span>
      </p>

      <Meter
        className="panelcard__meter"
        value={(panel.dust_level ?? 0) * 100}
        colour={state.colour}
      />

      <dl className="panelcard__meta">
        <div>
          <dt>Confidence</dt>
          <dd>{pctWhole(panel.confidence)}</dd>
        </div>
        <div>
          <dt>Last washed</dt>
          <dd>{panel.last_cleaned}</dd>
        </div>
      </dl>

      <div className="panelcard__actions">
        <ActionButton
          perform={analyzePanelAction.bind(null, panel.id)}
          label="Analyse"
          busyLabel="Analysing…"
          icon="scan"
        />
        <ActionButton
          perform={sprayPanelAction.bind(null, panel.id)}
          label="Wash"
          busyLabel="Washing…"
          icon="droplet"
          variant="water"
          confirm={{
            title: `Wash ${panel.id}?`,
            message: `This opens the valve for ${sprayDuration} seconds — about ${sprayDuration * 20}ml of water.`,
            confirmLabel: "Wash panel",
          }}
        />
      </div>
    </Tilt>
  );
}
