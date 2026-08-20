import type { Metadata } from "next";
import { ConsolePage } from "@/components/console/ConsolePage";
import { Donut } from "@/components/console/Donut";
import { ExportButtons } from "@/components/console/ExportButtons";
import { LogTable } from "@/components/console/LogTable";
import { StatCard } from "@/components/console/StatCard";
import { Empty } from "@/components/ui/Empty";
import { Icon } from "@/components/ui/Icon";
import { Meter } from "@/components/ui/Meter";
import { Stagger } from "@/components/ui/Motion";
import { Pill } from "@/components/ui/Pill";
import { Panel } from "@/components/ui/Surface";
import { getLogs, getOverview } from "@/lib/api";
import { reading, stamp } from "@/lib/format";
import { healthLabel } from "@/lib/status";

/**
 * Live hardware state: rendered per request, never prerendered. This also keeps
 * the build independent of the backend — the API is a separate deployment, and
 * `next build` must not need it to be up.
 */
export const dynamic = "force-dynamic";

export const metadata: Metadata = { title: "Reports" };

export default async function ReportsPage() {
  const [overview, logs] = await Promise.all([getOverview(), getLogs()]);
  const { health, panels, counts, stats, settings } = overview;

  const errors = logs.filter((log) => log.level === "ERROR").length;
  const warnings = logs.filter((log) => log.level === "WARNING").length;
  const avgDustPercent = Number((stats.avg_dust_level * 100).toFixed(1));
  const mlPerCycle = stats.total_cleanings
    ? Number((stats.water_used_total / stats.total_cleanings).toFixed(1))
    : 0;

  return (
    <ConsolePage
      eyebrow="Everything the system has recorded"
      title="Reports"
      demo={Boolean(settings.demo_seeded_at)}
      refreshInterval={settings.refresh_interval}
      actions={<ExportButtons stats={stats} counts={counts} panels={panels} logs={logs} />}
    >
      <Stagger className="grid grid--4 statgrid" step={0.06}>
        <StatCard
          label="Analyses run"
          value={stats.total_analyses}
          note="Frames scored since the database was created"
        />
        <StatCard
          label="Wash cycles"
          value={stats.total_cleanings}
          tone="water"
          note="Successful sprays only — refusals are logged, not counted"
        />
        <StatCard
          label="Water spent"
          value={stats.water_used_total}
          suffix=" ml"
          note={`${reading(mlPerCycle)} ml per cycle`}
        />
        <StatCard
          label="Mean dust coverage"
          value={avgDustPercent}
          decimals={1}
          suffix="%"
          tone="dust"
          note="Across every analysis on record"
        />
      </Stagger>

      <div className="reports__split">
        <Panel
          title="Array health"
          aside={<span className="mono text-faint">{counts.health_percentage}% clean</span>}
        >
          {panels.length ? <Donut counts={counts} /> : <Empty icon="chart">No panel data to chart yet.</Empty>}
        </Panel>

        <Panel
          title="Running state"
          aside={<Pill tone={health?.status ?? "unknown"}>{healthLabel(health?.status)}</Pill>}
        >
          <div className="bars">
            <div className="bars__row">
              <div className="bars__head">
                <span className="text-dim">Mean dust coverage</span>
                <span className="mono">{avgDustPercent}%</span>
              </div>
              <Meter value={avgDustPercent} colour="var(--dust)" />
            </div>
            <div className="bars__row">
              <div className="bars__head">
                <span className="text-dim">Water remaining</span>
                <span className="mono">{health?.water_level ?? 0}%</span>
              </div>
              <Meter value={health?.water_level ?? 0} colour="var(--water)" />
            </div>
            <div className="bars__row">
              <div className="bars__head">
                <span className="text-dim">Panels clean</span>
                <span className="mono">{counts.health_percentage}%</span>
              </div>
              <Meter value={counts.health_percentage} />
            </div>
          </div>

          <dl className="factlist">
            <div>
              <dt>
                <Icon name="clock" size={14} /> Process uptime
              </dt>
              <dd>{stats.system_uptime}</dd>
            </div>
            <div>
              <dt>
                <Icon name="scan" size={14} /> Last analysis
              </dt>
              <dd>{stamp(stats.last_analysis)}</dd>
            </div>
            <div>
              <dt>
                <Icon name="alert" size={14} /> Errors in log
              </dt>
              <dd className={errors ? "text-alarm" : "text-water"}>
                {errors} of {logs.length}
              </dd>
            </div>
            <div>
              <dt>
                <Icon name="info" size={14} /> Warnings in log
              </dt>
              <dd className={warnings ? "text-dust" : undefined}>{warnings}</dd>
            </div>
          </dl>
        </Panel>
      </div>

      <LogTable logs={logs} />
    </ConsolePage>
  );
}
