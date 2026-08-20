import Link from "next/link";
import { Icon } from "@/components/ui/Icon";

export default function NotFound() {
  return (
    <ErrorScreen
      code={404}
      title="No such page"
      detail="The address you followed is not part of the console."
    />
  );
}

/** Shared by the 404 and the error boundary — same shape, different words. */
export function ErrorScreen({
  code,
  title,
  detail,
  children,
}: {
  code: number;
  title: string;
  detail: string;
  children?: React.ReactNode;
}) {
  return (
    <section
      className="shell"
      style={{
        minHeight: "80vh",
        display: "grid",
        placeContent: "center",
        textAlign: "center",
        gap: "1.25rem",
        padding: "4rem 0",
      }}
    >
      <p className="numeral" style={{ fontSize: "clamp(4rem, 16vw, 9rem)", color: "var(--wafer-500)" }}>
        {code}
      </p>
      <h1 className="display" style={{ fontSize: "clamp(1.6rem, 4vw, 2.4rem)" }}>
        {title}
      </h1>
      <p className="lede" style={{ marginInline: "auto" }}>
        {detail}
      </p>
      <div className="row" style={{ justifyContent: "center", marginTop: "1rem" }}>
        {children}
        <Link className="btn btn--sun" href="/dashboard">
          <Icon name="gauge" size={14} /> Back to the console
        </Link>
        <Link className="btn" href="/">
          Home
        </Link>
      </div>
    </section>
  );
}
