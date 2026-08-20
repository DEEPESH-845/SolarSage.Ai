import { ActionButton } from "./ActionButton";
import { refillTankAction } from "@/app/actions";
import { Counter } from "@/components/ui/Counter";
import { Empty } from "@/components/ui/Empty";
import { Icon } from "@/components/ui/Icon";
import { Pill } from "@/components/ui/Pill";
import { Tank } from "@/components/ui/Tank";
import { healthLabel } from "@/lib/status";
import { reading, stamp } from "@/lib/format";
import type { Health, Stats } from "@/lib/types";

/**
 * What the system itself is doing: how much water is left, whether the cameras
 * answered, and how warm the array is. The dashboard and the settings page show
 * the same card, because it answers the same question on both.
 */
export function HealthCard({
  health,
  stats,
  className,
  showReading = false,
}: {
  health: Health | null;
  stats: Stats | null;
  className?: string;
  /** The settings page also shows when the reading was taken. */
  showReading?: boolean;
}) {
  return (
    <article className={`panel ${className ?? ""}`}>
      <div className="panel__head">
        <h2 className="panel__title">{showReading ? "System state" : "System"}</h2>
        {health ? (
          <Pill tone={health.status} live>
            {healthLabel(health.status)}
          </Pill>
        ) : (
          <Pill tone="unknown">Offline</Pill>
        )}
      </div>

      {health ? (
        <>
          <div className="tankrow">
            <Tank level={health.water_level} />

            <div className="tankrow__facts">
              <p className="label">Water tank</p>
              <Counter
                className="numeral numeral--lg tankrow__value"
                value={health.water_level}
                decimals={1}
                suffix="%"
              />
              <p className="mono text-faint">
                {reading(health.water.remaining_ml)} of {health.water.capacity_ml} ml
              </p>
              <ActionButton perform={refillTankAction} label="Refill tank" busyLabel="Refilling…" icon="droplet" />
            </div>
          </div>

          <dl className="factlist">
            <div>
              <dt>
                <Icon name="camera" size={14} /> Cameras
              </dt>
              <dd className={health.camera_status === "online" ? "text-water" : "text-dust"}>
                {healthLabel(health.camera_status as never)}
              </dd>
            </div>
            <div>
              <dt>
                <Icon name="thermometer" size={14} /> Array temperature
              </dt>
              <dd>{health.system_temperature}</dd>
            </div>
            <div>
              <dt>
                <Icon name="clock" size={14} /> {showReading ? "Process uptime" : "Uptime"}
              </dt>
              <dd>{stats?.system_uptime ?? "—"}</dd>
            </div>
            {showReading ? (
              <>
                <div>
                  <dt>
                    <Icon name="chip" size={14} /> Water used total
                  </dt>
                  <dd>{reading(stats?.water_used_total ?? 0, " ml")}</dd>
                </div>
                <div>
                  <dt>
                    <Icon name="refresh" size={14} /> Reading taken
                  </dt>
                  <dd>{stamp(health.timestamp)} UTC</dd>
                </div>
              </>
            ) : (
              <div>
                <dt>
                  <Icon name="wifi" size={14} /> Telemetry
                </dt>
                <dd>{health.telemetry_available ? "Receiving" : "No capture"}</dd>
              </div>
            )}
          </dl>
        </>
      ) : (
        <Empty icon="alert">
          The service layer did not answer. Reload the page; if it keeps failing, check the backend
          log.
        </Empty>
      )}
    </article>
  );
}
