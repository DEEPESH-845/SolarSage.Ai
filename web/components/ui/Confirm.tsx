"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { animate, prefersReducedMotion } from "@/lib/motion";

/**
 * `window.confirm`, replaced by something that matches the rest of the console.
 *
 * Anything that opens a valve asks first. `useConfirm()` returns a function that
 * resolves to the operator's answer, so a caller reads as a plain await rather
 * than a callback dance.
 */

export interface ConfirmRequest {
  title: string;
  message: string;
  confirmLabel?: string;
  danger?: boolean;
}

const ConfirmContext = createContext<(request: ConfirmRequest) => Promise<boolean>>(
  async () => false,
);

export function useConfirm() {
  return useContext(ConfirmContext);
}

interface Pending extends ConfirmRequest {
  resolve: (value: boolean) => void;
}

export function ConfirmProvider({ children }: { children: React.ReactNode }) {
  const [pending, setPending] = useState<Pending | null>(null);

  const ask = useCallback(
    (request: ConfirmRequest) =>
      new Promise<boolean>((resolve) => setPending({ ...request, resolve })),
    [],
  );

  const answer = useCallback(
    (value: boolean) => {
      pending?.resolve(value);
      setPending(null);
    },
    [pending],
  );

  return (
    <ConfirmContext.Provider value={ask}>
      {children}
      {pending && <ConfirmDialog request={pending} onAnswer={answer} />}
    </ConfirmContext.Provider>
  );
}

function ConfirmDialog({
  request,
  onAnswer,
}: {
  request: ConfirmRequest;
  onAnswer: (value: boolean) => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    dialog.showModal();
    if (!prefersReducedMotion()) {
      animate(
        dialog,
        { opacity: [0, 1], y: [12, 0], scale: [0.98, 1] },
        { type: "spring", stiffness: 400, damping: 34 },
      );
    }
  }, []);

  return (
    <dialog
      ref={ref}
      className="dialog dialog--ask"
      // Escape closes the dialog; it must answer "no" rather than leave the
      // caller's promise hanging forever.
      onCancel={(event) => {
        event.preventDefault();
        onAnswer(false);
      }}
    >
      <div className="dialog__head">
        <h2 className="panel__title">{request.title}</h2>
      </div>
      <div className="dialog__body">
        <p className="lede" style={{ fontSize: "1rem" }}>
          {request.message}
        </p>
        <div className="row row--end" style={{ marginTop: "1.75rem", justifyContent: "flex-end" }}>
          <button className="btn btn--sm" type="button" onClick={() => onAnswer(false)}>
            Cancel
          </button>
          <button
            className={`btn btn--sm ${request.danger ? "btn--danger" : "btn--sun"}`}
            type="button"
            autoFocus
            onClick={() => onAnswer(true)}
          >
            {request.confirmLabel ?? "Continue"}
          </button>
        </div>
      </div>
    </dialog>
  );
}
