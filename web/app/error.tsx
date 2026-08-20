"use client";

import { useEffect } from "react";
import { ErrorScreen } from "./not-found";
import { Icon } from "@/components/ui/Icon";

/**
 * The last resort. A page usually fails here because the backend did not answer,
 * so the first thing offered is trying again rather than navigating away.
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <ErrorScreen
      code={500}
      title="The console hit an error"
      detail={
        error.message ||
        "The request was logged. Try again, or check that the backend is running."
      }
    >
      <button className="btn" type="button" onClick={reset}>
        <Icon name="refresh" size={14} /> Try again
      </button>
    </ErrorScreen>
  );
}
