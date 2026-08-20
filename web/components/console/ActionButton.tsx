"use client";

import { useTransition } from "react";
import { Icon } from "@/components/ui/Icon";
import { useConfirm, type ConfirmRequest } from "@/components/ui/Confirm";
import { useToast } from "@/components/ui/Toast";
import { clsx } from "@/lib/clsx";
import type { ActionResult } from "@/lib/types";

/**
 * A button that runs one server action and reports what happened.
 *
 * Every write in the console goes through this: it asks first when the action
 * says to, locks itself while the server works, toasts the result, and toasts
 * each per-panel failure separately so a partial bulk wash is not summarised
 * away. The server action revalidates the page, so nothing here touches state.
 */
export function ActionButton({
  perform,
  label,
  busyLabel,
  icon,
  confirm: confirmRequest,
  variant,
  small = true,
  block = false,
  iconOnly = false,
  title,
}: {
  /** A server action, usually bound to its panel: `sprayPanelAction.bind(null, id)`. */
  perform: () => Promise<ActionResult>;
  label: string;
  busyLabel?: string;
  icon?: string;
  confirm?: ConfirmRequest;
  variant?: "sun" | "water" | "danger";
  small?: boolean;
  block?: boolean;
  iconOnly?: boolean;
  title?: string;
}) {
  const [pending, startTransition] = useTransition();
  const confirm = useConfirm();
  const toast = useToast();

  async function onClick() {
    if (confirmRequest && !(await confirm(confirmRequest))) return;

    startTransition(async () => {
      const result = await perform();
      toast({ message: result.message, kind: result.ok ? "success" : "error" });
      result.failures?.forEach((failure) =>
        toast({ message: `${failure.panel_id}: ${failure.error}`, kind: "error" }),
      );
    });
  }

  return (
    <button
      className={clsx(
        "btn",
        small && "btn--sm",
        variant && `btn--${variant}`,
        block && "btn--block",
        iconOnly && "btn--icon",
      )}
      type="button"
      onClick={onClick}
      disabled={pending}
      aria-busy={pending || undefined}
      title={title ?? (iconOnly ? label : undefined)}
      aria-label={iconOnly ? label : undefined}
    >
      {pending ? (
        <>
          <span className="spinner" aria-hidden="true" />
          {!iconOnly && (busyLabel ?? "Working…")}
        </>
      ) : (
        <>
          {icon && <Icon name={icon} size={iconOnly ? 15 : 14} />}
          {!iconOnly && label}
        </>
      )}
    </button>
  );
}
