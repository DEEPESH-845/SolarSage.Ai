"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { animate, prefersReducedMotion } from "@/lib/motion";

/**
 * Every action in the console reports through a toast — this replaces the DOM
 * building the old kit.js did. One provider owns the queue; anything below it
 * calls `useToast()` and forgets about the element.
 */

export type ToastKind = "success" | "error" | "info";

interface ToastRequest {
  message: string;
  kind?: ToastKind;
  title?: string;
  duration?: number;
}

interface ToastItem extends ToastRequest {
  id: number;
}

const DEFAULT_TITLES: Record<ToastKind, string> = {
  success: "Done",
  error: "Not done",
  info: "Note",
};

const ToastContext = createContext<(request: ToastRequest | string) => void>(() => {});

export function useToast() {
  return useContext(ToastContext);
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const nextId = useRef(0);

  const dismiss = useCallback((id: number) => {
    setItems((current) => current.filter((item) => item.id !== id));
  }, []);

  const push = useCallback((request: ToastRequest | string) => {
    const item = typeof request === "string" ? { message: request } : request;
    setItems((current) => [...current, { ...item, id: nextId.current++ }]);
  }, []);

  return (
    <ToastContext.Provider value={push}>
      {children}
      <div className="toasts" role="status" aria-live="polite">
        {items.map((item) => (
          <Toast key={item.id} item={item} onDismiss={() => dismiss(item.id)} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}

function Toast({ item, onDismiss }: { item: ToastItem; onDismiss: () => void }) {
  const ref = useRef<HTMLDivElement>(null);
  const kind = item.kind ?? "success";

  useEffect(() => {
    const element = ref.current;
    if (element && !prefersReducedMotion()) {
      animate(
        element,
        { opacity: [0, 1], x: [40, 0], scale: [0.96, 1] },
        { type: "spring", stiffness: 420, damping: 32 },
      );
    }
    // An error stays long enough to be read twice; anything else clears itself.
    const timer = setTimeout(onDismiss, item.duration ?? (kind === "error" ? 8000 : 5000));
    return () => clearTimeout(timer);
  }, [item.duration, kind, onDismiss]);

  return (
    <div ref={ref} className={`toast toast--${kind}`}>
      <div className="toast__body">
        <div className="toast__title">{item.title ?? DEFAULT_TITLES[kind]}</div>
        <div>{item.message}</div>
      </div>
      <button className="toast__close" type="button" aria-label="Dismiss" onClick={onDismiss}>
        ×
      </button>
    </div>
  );
}
