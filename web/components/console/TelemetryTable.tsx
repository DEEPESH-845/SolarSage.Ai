import { Pill } from "@/components/ui/Pill";
import { reading as readingText, words } from "@/lib/format";
import type { TelemetryReading } from "@/lib/types";

/**
 * The last sweep off the ESP32 nodes. Power and light come off the ADC
 * uncalibrated and can read negative — they are shown raw rather than clipped,
 * so a miscalibrated node stays visible instead of looking plausible.
 */
export function TelemetryTable({
  readings,
  panelIds,
}: {
  readings: TelemetryReading[];
  /** Hardware nodes map to panels positionally, in configured order. */
  panelIds: string[];
}) {
  return (
    <>
      <div className="table-wrap">
        <table className="data">
          <thead>
            <tr>
              <th>Sensor node</th>
              <th>Efficiency</th>
              <th>Cell temp</th>
              <th>Humidity</th>
              <th>Spray interval</th>
              <th>Power (raw)</th>
              <th>Light (raw)</th>
            </tr>
          </thead>
          <tbody>
            {readings.map((reading, index) => (
              <tr key={reading.panel_id}>
                <td className="mono">
                  {reading.panel_id}
                  {index < panelIds.length && (
                    <span style={{ marginLeft: "0.5rem" }}>
                      <Pill tone="clean" dot={false}>{words(panelIds[index])}</Pill>
                    </span>
                  )}
                </td>
                <td className="mono tabular">{readingText(reading.efficiency, "%")}</td>
                <td className="mono tabular">{readingText(reading.temperature, "°C")}</td>
                <td className="mono tabular">{readingText(reading.humidity, "%")}</td>
                <td className="mono tabular">{reading.spray_interval}s</td>
                <td className={`mono tabular ${reading.power < 0 ? "text-faint" : ""}`}>
                  {reading.power}
                </td>
                <td className={`mono tabular ${reading.light < 0 ? "text-faint" : ""}`}>
                  {reading.light}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mono text-faint" style={{ marginTop: "1rem", fontSize: "0.72rem" }}>
        Power and light come off the ADC uncalibrated and can read negative — they are shown raw
        rather than clipped, so a miscalibrated node stays visible.
      </p>
    </>
  );
}
