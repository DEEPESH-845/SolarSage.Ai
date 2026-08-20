import Link from "next/link";
import { CurveFigure } from "./CurveFigure";
import { Counter } from "@/components/ui/Counter";
import { Reveal, Stagger, Tilt } from "@/components/ui/Motion";
import { hasDecision } from "@/lib/status";
import type { LatestDecision } from "@/lib/types";

/**
 * What soiling costs, in the array's own numbers. When nothing has been
 * analysed the section says so and sends the visitor to the console — inventing
 * a plausible figure here would undercut the one claim the product makes.
 */
export function CostSection({ decision }: { decision: LatestDecision | null }) {
  const analysis = hasDecision(decision) ? decision.analysis : null;
  const priced = analysis?.daily_power_loss_kwh != null;

  return (
    <section className="section" id="cost">
      <div className="shell">
        <div className="section__head">
          <Reveal as="p" className="eyebrow">
            What soiling costs
          </Reveal>
          <Reveal as="h2" className="display" delay={0.08}>
            A clean panel and a dirty one
            <br />
            are the same hardware.
          </Reveal>
          <Reveal as="p" className="lede" delay={0.14}>
            The difference only shows up as a gap between what the array should make and what it
            actually makes. That gap is the entire reason to spend water — so the system measures it
            before it sprays.
          </Reveal>
        </div>

        <CurveFigure />

        {priced && analysis && hasDecision(decision) ? (
          <Stagger className="grid grid--3 cost__stats" step={0.09}>
            <Tilt className="stat panel" max={4}>
              <p className="label">Lost each day</p>
              <Counter
                className="numeral stat__value"
                value={analysis.daily_power_loss_kwh ?? 0}
                decimals={2}
                suffix=" kWh"
              />
              <p className="stat__note">
                Measured on {decision.panel_id} at {(decision.dust_level * 100).toFixed(1)}% dust
                coverage.
              </p>
            </Tilt>

            <Tilt className="stat panel" max={4}>
              <p className="label">Output held back</p>
              <Counter
                className="numeral stat__value text-dust"
                value={analysis.power_loss_percentage ?? 0}
                decimals={1}
                suffix="%"
              />
              <p className="stat__note">Soiling loss the forecaster derived from that coverage.</p>
            </Tilt>

            <Tilt className="stat panel" max={4}>
              <p className="label">Recovered per week</p>
              <Counter
                className="numeral stat__value text-water"
                value={analysis.estimated_savings_weekly ?? 0}
                decimals={2}
                prefix="$"
              />
              <p className="stat__note">
                {analysis.cleaning_cost_usd != null
                  ? `Net of the $${analysis.cleaning_cost_usd} a wash costs, paying back in ${analysis.payback_period_days} days.`
                  : "Net of what the wash costs to run."}
              </p>
            </Tilt>
          </Stagger>
        ) : (
          <Reveal className="panel cost__pending">
            <p className="label">No priced analysis on record</p>
            <p className="lede" style={{ margin: "0.75rem 0 1.5rem" }}>
              The numbers here come from a real classifier run — nothing is filled in until one has
              happened. Open the console and analyse the array to see what the current soiling is
              worth.
            </p>
            <Link className="btn btn--sun" href="/dashboard">
              Analyse the array
            </Link>
          </Reveal>
        )}
      </div>
    </section>
  );
}
