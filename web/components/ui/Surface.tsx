import { clsx } from "@/lib/clsx";

/**
 * The two raised surfaces the design system defines.
 *
 * `Panel` is a titled region of a page; `Card` is a tile inside one. They share
 * a background, border and radius in core.css — the difference is padding and
 * whether there is a head.
 */

export function Panel({
  title,
  aside,
  className,
  children,
}: {
  title?: string;
  /** Sits opposite the title: a pill, a count, a link. */
  aside?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <section className={clsx("panel", className)}>
      {(title || aside) && (
        <div className="panel__head">
          {title && <h2 className="panel__title">{title}</h2>}
          {aside}
        </div>
      )}
      {children}
    </section>
  );
}

export function Card({
  className,
  tight = false,
  children,
  ...rest
}: React.HTMLAttributes<HTMLElement> & { tight?: boolean }) {
  return (
    <article className={clsx("card", tight && "card--tight", className)} {...rest}>
      {children}
    </article>
  );
}
