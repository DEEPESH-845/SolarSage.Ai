import Link from "next/link";
import { Counter } from "@/components/ui/Counter";
import { Icon } from "@/components/ui/Icon";
import { Meter } from "@/components/ui/Meter";
import { MagneticLink, Reveal, Tilt } from "@/components/ui/Motion";
import { pct, titleCase } from "@/lib/format";
import { panelState } from "@/lib/status";
import type { Counts, Health, Panel } from "@/lib/types";

/** A miniature of the dashboard, drawn from the same numbers the dashboard
 *  would show — not a screenshot, so it can never go stale. */
export function ConsolePreview({
  panels,
  counts,
  health,
}: {
  panels: Panel[];
  counts: Counts;
  health: Health | null;
}) {
  return (
    <section className="section" id="console">
      <div className="shell console-cta">
        <div className="console-cta__copy">
          <Reveal as="p" className="eyebrow">
            The console
          </Reveal>
          <Reveal as="h2" className="display" delay={0.08}>
            Every panel, one page.
          </Reveal>
          <Reveal as="p" className="lede" delay={0.14}>
            Status per panel, the decision behind it, the water left in the tank, and the controls to
            analyse or wash anything by hand. Same numbers, no dashboard theatre.
          </Reveal>
          <Reveal className="row row--wrap console-cta__actions" delay={0.2}>
            <MagneticLink className="btn btn--sun" href="/dashboard">
              Open the console <Icon name="arrow" size={14} />
            </MagneticLink>
            <Link className="link-arrow" href="/reports">
              Read the reports <Icon name="arrow" size={13} />
            </Link>
          </Reveal>
        </div>

        <Tilt as="div" className="preview" max={5} reveal="scale">
          <div className="preview__chrome">
            <span className="preview__dot" />
            <span className="preview__dot" />
            <span className="preview__dot" />
            <span className="mono preview__path">solarsage / dashboard</span>
          </div>

          <div className="preview__body">
            <div className="preview__stats">
              <div>
                <p className="label">Clean</p>
                <Counter className="numeral text-water" value={counts.clean} />
              </div>
              <div>
                <p className="label">Dusty</p>
                <Counter className="numeral text-dust" value={counts.moderate_dust} />
              </div>
              <div>
                <p className="label">Wash now</p>
                <Counter className="numeral text-alarm" value={counts.needs_cleaning} />
              </div>
              <div>
                <p className="label">Untested</p>
                <Counter className="numeral text-faint" value={counts.unknown} />
              </div>
            </div>

            <ul className="preview__rows">
              {panels.map((panel) => (
                <li key={panel.id}>
                  <span className="mono">{titleCase(panel.id)}</span>
                  <Meter
                    className="preview__meter"
                    value={(panel.dust_level ?? 0) * 100}
                    colour={panelState(panel.status).colour}
                  />
                  <span className="mono text-faint">
                    {panel.dust_level == null ? "not analysed" : `${pct(panel.dust_level)} dust`}
                  </span>
                </li>
              ))}
            </ul>

            <div className="preview__tank">
              <p className="label">Water tank</p>
              <Meter value={health?.water_level ?? 0} colour="var(--water)" />
              <p className="mono text-faint">
                {health?.water.remaining_ml ?? 0} of {health?.water.capacity_ml ?? 0} ml
              </p>
            </div>
          </div>
        </Tilt>
      </div>
    </section>
  );
}
