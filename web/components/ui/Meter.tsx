import type { CSSProperties } from "react";
import { clsx } from "@/lib/clsx";

/**
 * A horizontal bar. `value` is a percentage, `colour` a CSS colour — both are
 * passed as custom properties because the fill and its glow are drawn in CSS.
 */
export function Meter({
  value,
  colour,
  className,
  style: extra,
}: {
  value: number;
  colour?: string;
  className?: string;
  /** Layout only — a table cell stretches its meter, a card does not. */
  style?: CSSProperties;
}) {
  const style = {
    ...extra,
    "--value": `${value.toFixed(1)}%`,
    ...(colour ? { "--meter-color": colour } : {}),
  } as CSSProperties;

  return (
    <span className={clsx("meter", className)} style={style}>
      <span className="meter__fill" />
    </span>
  );
}
