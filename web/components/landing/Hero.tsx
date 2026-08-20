"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { Counter } from "@/components/ui/Counter";
import { Icon } from "@/components/ui/Icon";
import { Pill } from "@/components/ui/Pill";
import { createArray, type ArrayCanvas } from "@/lib/landing/array-canvas";
import { prefersReducedMotion } from "@/lib/motion";
import { healthLabel } from "@/lib/status";
import type { Counts, Health, Panel } from "@/lib/types";

/**
 * The first screen: the real array, drawn with the real coverage, washing
 * itself once so a visitor sees the whole product in one gesture. Everything
 * animated here is a nicety — the readouts and the copy are plain markup, so a
 * visitor with reduced motion or no JavaScript loses nothing but the show.
 */
export function Hero({
  panels,
  health,
  counts,
}: {
  panels: Panel[];
  health: Health | null;
  counts: Counts;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const replayRef = useRef<() => void>(() => {});

  // Coverage per module, in panel order — a panel that has never been analysed
  // is drawn lightly soiled rather than as spotless glass it has not earned.
  const dust = panels.map((panel) => (panel.dust_level == null ? 0.32 : Math.min(1, panel.dust_level)));
  while (dust.length < 4) dust.push(0.28);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const array: ArrayCanvas = createArray(canvas, dust);
    array.resize();
    array.render();

    if (prefersReducedMotion()) return;
    gsap.registerPlugin(ScrollTrigger, SplitText);

    let visible = true;
    const observer = new IntersectionObserver((entries) => {
      visible = entries[0].isIntersecting;
    });
    observer.observe(canvas);

    const tick = () => {
      if (!visible || document.hidden) return;
      array.state.glint += 0.0016;
      array.render();
    };
    gsap.ticker.add(tick);

    let resizeTimer: ReturnType<typeof setTimeout>;
    const onResize = () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        array.resize();
        array.render();
      }, 120);
    };
    window.addEventListener("resize", onResize);

    /** One honest cycle: the nozzle crosses, the glass is clean behind it, and
        then it starts soiling again — because that is what actually happens. */
    let cycle: gsap.core.Timeline | null = null;
    const replay = () => {
      cycle?.kill();
      cycle = gsap
        .timeline()
        .set(array.state, { recover: 0, sweep: -0.35 })
        .to(array.state, { sweep: 1.35, duration: 2.6, ease: "power1.inOut" })
        .to(array.state, { recover: 1, duration: 3.4, ease: "power1.in" }, "+=1.1")
        .set(array.state, { sweep: -0.4 });
    };
    replayRef.current = replay;
    const opening = gsap.delayedCall(1.1, replay);

    return () => {
      observer.disconnect();
      gsap.ticker.remove(tick);
      window.removeEventListener("resize", onResize);
      clearTimeout(resizeTimer);
      opening.kill();
      cycle?.kill();
    };
    // The coverage only changes on a full page load, and re-running this would
    // restart the wash cycle under the visitor.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useHeroIntro();

  return (
    <section className="hero">
      <div className="hero__field" aria-hidden="true">
        <canvas ref={canvasRef} id="wafer" className="hero__canvas" />
        <div className="hero__horizon" />
      </div>

      <div className="shell hero__inner">
        <p className="eyebrow hero__eyebrow">
          Array 01 · Bengaluru · {panels.length} panels under watch
        </p>

        <h1 className="display hero__title">
          <span className="line">Dust takes the yield</span>
          <span className="line">
            before anyone <em>sees</em> it.
          </span>
        </h1>

        <p className="lede hero__lede">
          SolarSage reads each panel from its own camera, turns the soiling into kilowatt-hours and
          rupees, and opens the valve only when the wash pays for itself.
        </p>

        <div className="hero__actions">
          <Link className="btn btn--sun" href="/dashboard">
            Open the console <Icon name="arrow" size={14} />
          </Link>
          <button className="btn" type="button" onClick={() => replayRef.current()}>
            <Icon name="play" size={14} /> Run a wash cycle
          </button>
        </div>

        <dl className="hero__readout">
          <div className="readout">
            <dt className="label">System</dt>
            <dd>
              <Pill tone={health?.status ?? "unknown"} live>
                {healthLabel(health?.status)}
              </Pill>
            </dd>
          </div>
          <div className="readout">
            <dt className="label">Water tank</dt>
            <Counter
              as="dd"
              className="numeral readout__value"
              value={health?.water_level ?? 0}
              decimals={1}
              suffix="%"
            />
          </div>
          <div className="readout">
            <dt className="label">Cameras</dt>
            <dd className="readout__value mono">{healthLabel(health?.camera_status as never)}</dd>
          </div>
          <div className="readout">
            <dt className="label">Needs attention</dt>
            <Counter
              as="dd"
              className={`numeral readout__value ${counts.attention ? "text-dust" : "text-water"}`}
              value={counts.attention}
            />
          </div>
        </dl>
      </div>

      <div className="hero__scroll mono" aria-hidden="true">
        scroll
      </div>
    </section>
  );
}

/**
 * The opening: lines of the headline rise out of their own mask, then each
 * block below it arrives. Built after the fonts resolve — a timeline created
 * before that would have played itself out before the text had its real shape.
 */
function useHeroIntro() {
  useEffect(() => {
    if (prefersReducedMotion()) return;
    gsap.registerPlugin(ScrollTrigger, SplitText);

    let context: gsap.Context | null = null;
    const run = () => {
      context = gsap.context(() => {
        const timeline = gsap.timeline({ defaults: { ease: "power3.out" } });
        const title = document.querySelector<HTMLElement>(".hero__title");

        if (title) {
          const split = new SplitText(title, { type: "lines", mask: "lines" });
          timeline.from(split.lines, { yPercent: 115, duration: 1.1, stagger: 0.09 }, 0);
        }
        timeline
          .from(".hero__eyebrow", { opacity: 0, y: 12, duration: 0.8 }, 0.1)
          .from(".hero__lede", { opacity: 0, y: 18, duration: 0.9 }, 0.45)
          .from(".hero__actions > *", { opacity: 0, y: 16, duration: 0.7, stagger: 0.08, clearProps: "transform" }, 0.6)
          .from(".readout", { opacity: 0, y: 20, duration: 0.8, stagger: 0.06, clearProps: "transform" }, 0.75)
          .from(".hero__scroll", { opacity: 0, duration: 0.6 }, 1.1);

        // The hero drifts as the reader leaves it, so the array stays in view a
        // beat longer than the copy does.
        gsap.to(".hero__field", {
          yPercent: 14,
          ease: "none",
          scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true },
        });
        gsap.to(".hero__inner", {
          yPercent: -6,
          opacity: 0.15,
          ease: "none",
          scrollTrigger: { trigger: ".hero", start: "top top", end: "bottom top", scrub: true },
        });
      });
    };

    if (document.fonts?.ready) document.fonts.ready.then(run);
    else run();

    return () => context?.revert();
  }, []);
}
