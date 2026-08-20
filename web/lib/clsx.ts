/**
 * Join class names, dropping anything falsy — the one-line version of the
 * `clsx` package, which is not worth a dependency for this.
 */
export function clsx(...parts: (string | false | null | undefined)[]): string {
  return parts.filter(Boolean).join(" ");
}
