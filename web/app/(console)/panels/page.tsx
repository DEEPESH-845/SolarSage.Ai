import type { Metadata } from "next";
import { ActionButton } from "@/components/console/ActionButton";
import { ConsolePage } from "@/components/console/ConsolePage";
import { PanelTable } from "@/components/console/PanelTable";
import { StatCard } from "@/components/console/StatCard";
import { TelemetryTable } from "@/components/console/TelemetryTable";
import { analyzeAllAction, sprayManyAction } from "@/app/actions";
import { Empty } from "@/components/ui/Empty";
import { Stagger } from "@/components/ui/Motion";
import { Panel } from "@/components/ui/Surface";
import { overviewFeed, telemetryFeed } from "@/lib/feed";
import { stamp } from "@/lib/format";

/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Panels" };

export default async function PanelsPage() {
  const { data: overview, source, reason } = await overviewFeed();
  const telemetry = await telemetryFeed(source);
  const { panels, counts, settings } = overview;
  const readings = telemetry.readings ?? [];

  return (
    <ConsolePage
      eyebrow={`${counts.total} panels · ${counts.attention} needing attention`}
      title="Panels"
      source={source}
      reason={reason}
      seeded={Boolean(settings.demo_seeded_at)}
      refreshInterval={settings.refresh_interval}
      actions={
        <>
          <ActionButton perform={analyzeAllAction} label="Analyse all" busyLabel="Analysing…" icon="scan" />
          <ActionButton
            perform={sprayManyAction.bind(null, "dirty")}
            label="Wash dusty"
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
      <Stagger className="grid grid--4 statgrid" step={0.06}>
        <StatCard label="Under watch" value={counts.total} note="Panels configured in the system" />
        <StatCard
          label="Clean"
          value={counts.clean}
          tone="water"
          note={`Below the schedule threshold (${settings.schedule_threshold}%)`}
        />
        <StatCard
          label="Moderate dust"
          value={counts.moderate_dust}
          tone="dust"
          note="Scheduled, not sprayed yet"
        />
        <StatCard
          label="Needs washing"
          value={counts.needs_cleaning}
          tone="alarm"
          note={`Past the immediate threshold (${settings.dust_threshold}%)`}
        />
      </Stagger>

      <Panel
        title="Panel detail"
        aside={<span className="mono text-faint">Dust coverage as measured on the last frame</span>}
      >
        {panels.length ? (
          <PanelTable panels={panels} sprayDuration={settings.spray_duration} />
        ) : (
          <Empty icon="grid">No panels are configured, so there is nothing to show.</Empty>
        )}
      </Panel>

      <Panel
        title="Last hardware sweep"
        aside={
          <span className="mono text-faint">
            {telemetry.available
              ? `${readings.length} nodes · ${telemetry.source} · ${stamp(telemetry.captured_at, "")} UTC`
              : "No capture files in Hardware/"}
          </span>
        }
      >
        {readings.length ? (
          <TelemetryTable readings={readings} panelIds={panels.map((panel) => panel.id)} />
        ) : (
          <Empty icon="wifi">
            No telemetry captures were found. Drop an ESP32 capture into Hardware/ and reload.
          </Empty>
        )}
      </Panel>
    </ConsolePage>
  );
}
