import { titleCase } from "@/lib/format";
import { PANEL_STATE } from "@/lib/status";
import type { Counts, PanelState } from "@/lib/types";

/** Circumference of the r=54 ring the SVG draws, which is what the segment
 *  lengths are a fraction of. */
const CIRCUMFERENCE = 339.3;

const ORDER: PanelState[] = ["clean", "moderate_dust", "needs_cleaning", "unknown"];

/**
 * The array's states as one ring. Segments are laid end to end by walking an
 * offset, so the ring reads clockwise in the same order as the legend under it.
 */
export function Donut({ counts }: { counts: Counts }) {
  const total = counts.total || 1;
  let offset = 0;

  const segments = ORDER.map((state) => {
    const value = counts[state];
    const length = Number(((value / total) * CIRCUMFERENCE).toFixed(2));
    const segment = { state, value, length, offset: -offset, colour: PANEL_STATE[state].colour };
    offset += length;
    return segment;
  });

  return (
    <div className="donut">
      <div className="donut__chart">
        <svg
          viewBox="0 0 120 120"
          role="img"
          aria-label={`Panel states: ${counts.clean} clean, ${counts.moderate_dust} moderate, ${counts.needs_cleaning} needing a wash, ${counts.unknown} untested.`}
        >
          <circle className="donut__ring" cx="60" cy="60" r="54" stroke="rgba(198,208,228,0.08)" />
          {segments
            .filter((segment) => segment.value > 0)
            .map((segment) => (
              <circle
                key={segment.state}
                className="donut__ring"
                cx="60"
                cy="60"
                r="54"
                stroke={segment.colour}
                strokeDasharray={`${segment.length} ${(CIRCUMFERENCE - segment.length).toFixed(2)}`}
                strokeDashoffset={segment.offset.toFixed(2)}
              />
            ))}
        </svg>
        <div className="donut__center">
          <p className="numeral numeral--md donut__value">{counts.health_percentage}%</p>
          <p className="label">Clean</p>
        </div>
      </div>

      <dl className="donut__legend">
        {segments.map((segment) => (
          <div key={segment.state}>
            <span className="donut__swatch" style={{ background: segment.colour }} />
            <dt>{titleCase(segment.state)}</dt>
            <dd className="tabular">{segment.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
