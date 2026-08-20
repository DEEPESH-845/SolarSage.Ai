import { ActionButton } from "./ActionButton";
import { analyzeAllAction, sprayManyAction } from "@/app/actions";
import { Icon } from "@/components/ui/Icon";
import type { SystemSettings } from "@/lib/types";

/**
 * The three operations that touch the whole array. Each card says what it will
 * do and how much water that costs before the button is pressed — the confirm
 * dialog is the second chance, not the first warning.
 */
export function BulkActions({
  settings,
  totalPanels,
  tankCapacityMl,
}: {
  settings: SystemSettings;
  totalPanels: number;
  tankCapacityMl: number;
}) {
  const perPanelMl = settings.spray_duration * 20;

  return (
    <section className="grid grid--3 dash__bulk">
      <article className="panel action">
        <h3 className="panel__title">
          <Icon name="scan" size={15} /> Analyse every panel
        </h3>
        <p className="action__body">
          Runs the camera and classifier across the array. Washing follows only if a panel crosses
          the immediate threshold and auto-cleaning is on.
        </p>
        <ActionButton perform={analyzeAllAction} label="Run analysis" busyLabel="Analysing…" block />
      </article>

      <article className="panel action">
        <h3 className="panel__title">
          <Icon name="droplet" size={15} /> Wash what needs it
        </h3>
        <p className="action__body">
          Sprays only the panels currently marked dusty or worse. Uses {perPanelMl}ml per panel at{" "}
          {settings.water_pressure} pressure.
        </p>
        <ActionButton
          perform={sprayManyAction.bind(null, "dirty")}
          label="Wash dusty panels"
          busyLabel="Washing…"
          variant="water"
          block
          confirm={{
            title: "Wash every dusty panel?",
            message:
              "Only panels above the schedule threshold are sprayed. Clean panels are left alone.",
            confirmLabel: "Wash them",
          }}
        />
      </article>

      <article className="panel action action--danger">
        <h3 className="panel__title">
          <Icon name="alert" size={15} /> Wash everything
        </h3>
        <p className="action__body">
          Sprays all {totalPanels} panels regardless of state — about {totalPanels * perPanelMl}ml
          from a {tankCapacityMl}ml tank.
        </p>
        <ActionButton
          perform={sprayManyAction.bind(null, "all")}
          label="Wash all panels"
          busyLabel="Washing…"
          variant="danger"
          block
          confirm={{
            title: "Wash all panels?",
            message:
              "Every panel is sprayed regardless of how dirty it is. This can empty the tank.",
            confirmLabel: "Wash everything",
            danger: true,
          }}
        />
      </article>
    </section>
  );
}
