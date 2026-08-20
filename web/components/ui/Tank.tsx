import type { CSSProperties } from "react";

/** The water tank, filled to `level` per cent. Purely decorative markup: the
 *  reading beside it is the accessible copy, so this carries the label. */
export function Tank({ level }: { level: number }) {
  return (
    <div
      className="tank"
      style={{ "--level": `${level}%` } as CSSProperties}
      role="img"
      aria-label={`Water tank ${level} per cent full`}
    >
      <div className="tank__fill">
        <span className="tank__wave" />
      </div>
      <div className="tank__ticks" aria-hidden="true">
        <i />
        <i />
        <i />
      </div>
    </div>
  );
}
