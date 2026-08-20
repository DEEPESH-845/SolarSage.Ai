import { clsx } from "@/lib/clsx";

/**
 * The small status badge used everywhere a state has to be visible at a glance.
 * `tone` is the CSS modifier — see `panelState()` for the panel-state mapping,
 * which exists so a pill and the meter beside it can never disagree.
 */
export function Pill({
  tone,
  children,
  live = false,
  dot = true,
}: {
  tone: string;
  children: React.ReactNode;
  live?: boolean;
  /** A pill that labels rather than reports state carries no status dot. */
  dot?: boolean;
}) {
  return (
    <span className={clsx("pill", `pill--${tone}`, live && "pill--live")}>
      {dot && <span className="pill__dot" />}
      {children}
    </span>
  );
}
