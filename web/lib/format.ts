/**
 * Formatting the console does over and over. Every one of these takes the value
 * the backend actually sends — including null — so a missing reading prints as
 * an em dash instead of "NaN%" or "null".
 */

const DASH = "—";

/** A 0–1 fraction as a percentage. */
export function pct(fraction: number | null | undefined, digits = 1): string {
  return fraction == null ? DASH : `${(fraction * 100).toFixed(digits)}%`;
}

/** A 0–1 fraction as a whole-number percentage — used where space is tight. */
export function pctWhole(fraction: number | null | undefined): string {
  return fraction == null ? DASH : `${Math.round(fraction * 100)}%`;
}

export function ml(value: number | null | undefined): string {
  return value == null ? DASH : `${Math.round(value).toLocaleString()} ml`;
}

/** ISO timestamp to "YYYY-MM-DD HH:MM:SS", the form every table uses. */
export function stamp(iso: string | null | undefined, fallback = "never"): string {
  return iso ? String(iso).slice(0, 19).replace("T", " ") : fallback;
}

/** snake_case to words: "needs_cleaning" reads as "needs cleaning". */
export function words(value: string | null | undefined): string {
  return String(value ?? "").replace(/_/g, " ");
}

/**
 * Title Case for a snake_case, lower-case or SHOUTED label: "WITHIN_24H"
 * becomes "Within 24h", the way the templates this replaced rendered it.
 */
export function titleCase(value: string | null | undefined): string {
  return words(value)
    .toLowerCase()
    .replace(/\b[a-z]/g, (character) => character.toUpperCase());
}

/**
 * A reading, printed the way the service layer prints it.
 *
 * The backend rounds its floats and Python shows them with a decimal point:
 * 81.0, not 81. JSON does not carry that distinction, so a whole-numbered
 * reading would otherwise change shape between the API and the screen.
 */
export function reading(value: number | null | undefined, unit = ""): string {
  if (value == null) return DASH;
  return `${Number.isInteger(value) ? value.toFixed(1) : value}${unit}`;
}

/** A number with fixed decimals, grouped — matches the counter animation. */
export function decimal(value: number, digits = 0): string {
  return value.toLocaleString(undefined, {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
}
