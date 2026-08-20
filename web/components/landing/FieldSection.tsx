import { RingArc } from "./RingArc";
import { Icon } from "@/components/ui/Icon";
import { Reveal, Stagger, Tilt } from "@/components/ui/Motion";
import { reading as readingText, stamp } from "@/lib/format";
import type { Telemetry } from "@/lib/types";

/**
 * The last sweep off the hardware, unedited. The capture covers the whole ESP32
 * network, so only the nodes wired to panels this system controls are shown —
 * and the note underneath says how many were left out.
 */
export function FieldSection({
  telemetry,
  panelCount,
}: {
  telemetry: Telemetry;
  panelCount: number;
}) {
  const readings = telemetry.readings ?? [];
  const mapped = readings.slice(0, panelCount);

  return (
    <section className="section" id="field">
      <div className="shell">
        <div className="section__head section__head--split">
          <div>
            <Reveal as="p" className="eyebrow">
              Last sweep from the array
            </Reveal>
            <Reveal as="h2" className="display" delay={0.08}>
              Real hardware, real readings.
            </Reveal>
          </div>
          <Reveal as="p" className="mono text-faint field__source" mode="right">
            {telemetry.available ? (
              <>
                {telemetry.source}
                <br />
                captured {stamp(telemetry.captured_at, "")} UTC
              </>
            ) : (
              "No capture file found in Hardware/"
            )}
          </Reveal>
        </div>

        {mapped.length ? (
          <>
            <Stagger className="grid grid--4 field__grid" step={0.08}>
              {mapped.map((reading) => (
                <Tilt key={reading.panel_id} className="reading panel" max={7}>
                  <header className="row row--between">
                    <p className="label">{reading.panel_id.replace("PANNEL_", "Panel ")}</p>
                    <span className="mono text-faint">{readingText(reading.efficiency, "%")}</span>
                  </header>

                  <div
                    className="reading__ring"
                    style={{ "--value": reading.efficiency } as React.CSSProperties}
                  >
                    <svg viewBox="0 0 100 100" aria-hidden="true">
                      <circle className="reading__track" cx="50" cy="50" r="42" />
                      <RingArc efficiency={reading.efficiency} />
                    </svg>
                    <p className="numeral reading__value">
                      {Math.round(reading.efficiency)}
                      <span className="reading__unit">%</span>
                    </p>
                    <p className="label reading__caption">Efficiency</p>
                  </div>

                  <dl className="reading__rows">
                    <div>
                      <dt>
                        <Icon name="thermometer" size={13} /> Cell temp
                      </dt>
                      <dd className="tabular">{readingText(reading.temperature, "°C")}</dd>
                    </div>
                    <div>
                      <dt>
                        <Icon name="humidity" size={13} /> Humidity
                      </dt>
                      <dd className="tabular">{readingText(reading.humidity, "%")}</dd>
                    </div>
                    <div>
                      <dt>
                        <Icon name="clock" size={13} /> Spray gap
                      </dt>
                      <dd className="tabular">{reading.spray_interval}s</dd>
                    </div>
                  </dl>
                </Tilt>
              ))}
            </Stagger>

            <Reveal as="p" className="field__note mono text-faint">
              {readings.length} nodes reported in this capture; the {mapped.length} wired to panels
              under management are shown. Across the whole sweep: {telemetry.avg_temperature}°C ·{" "}
              {telemetry.avg_humidity}% RH · {telemetry.avg_efficiency}% efficiency. Raw power and
              light counts come off the ADC uncalibrated and are left unclipped in the console.
            </Reveal>
          </>
        ) : (
          <Reveal as="p" className="panel">
            No telemetry captures are present, so this section has nothing to show yet.
          </Reveal>
        )}
      </div>
    </section>
  );
}
