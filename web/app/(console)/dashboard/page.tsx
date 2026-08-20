import type { Metadata } from "next";
import { ActionButton } from "@/components/console/ActionButton";
import { BulkActions } from "@/components/console/BulkActions";
import { ConsolePage } from "@/components/console/ConsolePage";
import { DecisionCard } from "@/components/console/DecisionCard";
import { HealthCard } from "@/components/console/HealthCard";
import { PanelCard } from "@/components/console/PanelCard";
import { analyzeAllAction, sprayManyAction } from "@/app/actions";
import { Empty } from "@/components/ui/Empty";
import { Icon } from "@/components/ui/Icon";
import { Stagger } from "@/components/ui/Motion";
import { getOverview } from "@/lib/api";
import Link from "next/link";

/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Dashboard" };

export default async function DashboardPage() {
  const { health, panels, counts, stats, latest_decision, settings } = await getOverview();

  return (
    <ConsolePage
      eyebrow="Array 01 · Bengaluru"
      title="Dashboard"
      demo={Boolean(settings.demo_seeded_at)}
      refreshInterval={settings.refresh_interval}
      actions={
        <>
          <ActionButton perform={analyzeAllAction} label="Analyse all" busyLabel="Analysing…" icon="scan" />
          <ActionButton
            perform={sprayManyAction.bind(null, "dirty")}
            label="Wash what needs it"
            busyLabel="Washing…"
            icon="droplet"
            variant="water"
            confirm={{
              title: "Wash every dusty panel?",
              message:
                "Only panels above the schedule threshold are sprayed. Clean panels are left alone.",
              confirmLabel: "Wash them",
            }}
          />
        </>
      }
    >
      <section className="grid dash__top">
        <HealthCard health={health} stats={stats} className="dash__health" />
        <DecisionCard decision={latest_decision} />
      </section>

      <section className="panel dash__panels">
        <div className="panel__head">
          <h2 className="panel__title">Panels</h2>
          <div className="row">
            <span className="mono text-faint">
              {counts.clean} clean · {counts.attention} need attention · {counts.unknown} untested
            </span>
            <Link className="link-arrow" href="/panels">
              All detail <Icon name="arrow" size={13} />
            </Link>
          </div>
        </div>

        {panels.length ? (
          <Stagger className="grid grid--4 panelgrid" step={0.06}>
            {panels.map((panel) => (
              <PanelCard key={panel.id} panel={panel} sprayDuration={settings.spray_duration} />
            ))}
          </Stagger>
        ) : (
          <Empty icon="grid">No panels are configured.</Empty>
        )}
      </section>

      <BulkActions
        settings={settings}
        totalPanels={counts.total}
        tankCapacityMl={health?.water.capacity_ml ?? 0}
      />
    </ConsolePage>
  );
}
