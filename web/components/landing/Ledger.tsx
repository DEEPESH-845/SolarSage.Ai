import { Counter } from "@/components/ui/Counter";
import { Reveal, Stagger } from "@/components/ui/Motion";
import type { Stats } from "@/lib/types";

/** What the system has actually done, counted from its own database. */
export function Ledger({ stats }: { stats: Stats }) {
  const entries = [
    { label: "Panels analysed", value: stats.total_analyses, decimals: 0, suffix: "" },
    { label: "Wash cycles run", value: stats.total_cleanings, decimals: 0, suffix: "" },
    { label: "Water spent", value: stats.water_used_total, decimals: 0, suffix: " ml" },
    {
      label: "Mean dust coverage",
      value: Number((stats.avg_dust_level * 100).toFixed(1)),
      decimals: 1,
      suffix: "%",
    },
  ];

  return (
    <section className="section section--ledger">
      <div className="shell">
        <Reveal as="p" className="eyebrow">
          The ledger so far
        </Reveal>

        <Stagger className="ledger" step={0.08}>
          {entries.map((entry) => (
            <div className="ledger__item" key={entry.label}>
              <Counter
                className="numeral ledger__value"
                value={entry.value}
                decimals={entry.decimals}
                suffix={entry.suffix}
              />
              <p className="label">{entry.label}</p>
            </div>
          ))}
        </Stagger>

        <Reveal as="p" className="mono text-faint ledger__note">
          Counted from the system database, not from a brochure. Uptime this process:{" "}
          {stats.system_uptime}.
        </Reveal>
      </div>
    </section>
  );
}
