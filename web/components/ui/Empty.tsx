import { clsx } from "@/lib/clsx";
import { Icon } from "./Icon";

/**
 * What a region says when it has nothing to show. Every empty state names the
 * thing that would fill it, so the page never reads as broken when it is simply
 * early.
 */
export function Empty({
  icon,
  tall = false,
  children,
}: {
  icon: string;
  tall?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className={clsx("empty", tall && "empty--tall")}>
      <Icon name={icon} size={tall ? 22 : 20} />
      {tall ? <div>{children}</div> : children}
    </div>
  );
}

export function Note({
  tone,
  icon,
  children,
}: {
  tone: "ok" | "error" | "demo";
  icon: string;
  children: React.ReactNode;
}) {
  return (
    <p className={clsx("note", `note--${tone}`)} role={tone === "demo" ? "status" : undefined}>
      <Icon name={icon} size={tone === "demo" ? 15 : 14} />
      <span>{children}</span>
    </p>
  );
}
