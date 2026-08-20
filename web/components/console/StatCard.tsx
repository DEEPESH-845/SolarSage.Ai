import { Counter } from "@/components/ui/Counter";
import { clsx } from "@/lib/clsx";

/** A single figure with the sentence that says what it counts. */
export function StatCard({
  label,
  value,
  note,
  tone,
  decimals = 0,
  suffix = "",
}: {
  label: string;
  value: number;
  note: string;
  tone?: "water" | "dust" | "alarm";
  decimals?: number;
  suffix?: string;
}) {
  return (
    <article className="card card--tight statcard">
      <p className="label">{label}</p>
      <Counter
        className={clsx("numeral numeral--lg statcard__value", tone && `text-${tone}`)}
        value={value}
        decimals={decimals}
        suffix={suffix}
      />
      <p className="statcard__note">{note}</p>
    </article>
  );
}
