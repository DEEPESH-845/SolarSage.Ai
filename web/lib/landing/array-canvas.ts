/**
 * The array on the landing page: photovoltaic modules whose soiling is the real
 * dust coverage from the database, cleared by a spray pass that runs the way the
 * hardware does — left to right, once, then the glass soils again.
 *
 * This is imperative canvas drawing and stays that way: React owns when it runs
 * (see components/landing/Hero.tsx), and this module owns what a module looks
 * like. `state` is the handle an animation timeline tweens.
 */

const WAFER = "#1c2a63";
const WAFER_DEEP = "#0e1740";
const BUSBAR = "rgba(198, 208, 228, 0.3)";

export interface ArrayState {
  /** Nozzle position, 0–1 across the canvas; outside that range it is parked. */
  sweep: number;
  /** How far the glass behind the nozzle has soiled again, 0–1. */
  recover: number;
  /** Drift of the sun's sheen across the glass. */
  glint: number;
}

export interface ArrayCanvas {
  resize(): void;
  render(): void;
  state: ArrayState;
}

/** Soiling is grain, not a wash of colour, so it gets a real noise tile. */
function dustPattern(): HTMLCanvasElement {
  const tile = document.createElement("canvas");
  tile.width = tile.height = 72;
  const context = tile.getContext("2d")!;
  const image = context.createImageData(72, 72);

  for (let i = 0; i < image.data.length; i += 4) {
    const grain = Math.random();
    image.data[i] = 198 + grain * 34;
    image.data[i + 1] = 140 + grain * 40;
    image.data[i + 2] = 78 + grain * 34;
    // Sparse: soiling reads as a veil with texture, not a coat of paint.
    image.data[i + 3] = grain > 0.86 ? 130 : grain > 0.62 ? 46 : 12;
  }
  context.putImageData(image, 0, 0);
  return tile;
}

function roundRect(
  context: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  r: number,
) {
  context.beginPath();
  context.moveTo(x + r, y);
  context.arcTo(x + w, y, x + w, y + h, r);
  context.arcTo(x + w, y + h, x, y + h, r);
  context.arcTo(x, y + h, x, y, r);
  context.arcTo(x, y, x + w, y, r);
  context.closePath();
}

/** `dust` is one 0–1 coverage per module, in panel order. */
export function createArray(canvas: HTMLCanvasElement, dust: number[]): ArrayCanvas {
  const ctx = canvas.getContext("2d")!;
  const pattern = ctx.createPattern(dustPattern(), "repeat");
  const state: ArrayState = { sweep: -0.4, recover: 1, glint: 0 };
  const box = { w: 0, h: 0 };

  function resize() {
    const rect = canvas.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    box.w = rect.width;
    box.h = rect.height;
    canvas.width = Math.max(1, Math.round(rect.width * dpr));
    canvas.height = Math.max(1, Math.round(rect.height * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function drawModule(x: number, y: number, w: number, h: number, soiling: number, index: number) {
    const cols = 6;
    const rows = 3;
    const pad = Math.max(4, w * 0.022);
    const cellW = (w - pad * (cols + 1)) / cols;
    const cellH = (h - pad * (rows + 1)) / rows;

    ctx.save();

    // frame
    ctx.fillStyle = "rgba(6, 11, 28, 0.92)";
    roundRect(ctx, x, y, w, h, 6);
    ctx.fill();
    ctx.strokeStyle = "rgba(198, 208, 228, 0.16)";
    ctx.lineWidth = 1;
    ctx.stroke();

    // cells + busbars
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const cx = x + pad + c * (cellW + pad);
        const cy = y + pad + r * (cellH + pad);
        const gradient = ctx.createLinearGradient(cx, cy, cx + cellW, cy + cellH);
        gradient.addColorStop(0, WAFER);
        gradient.addColorStop(1, WAFER_DEEP);
        ctx.fillStyle = gradient;
        roundRect(ctx, cx, cy, cellW, cellH, 2);
        ctx.fill();

        ctx.strokeStyle = BUSBAR;
        ctx.lineWidth = 0.6;
        ctx.beginPath();
        ctx.moveTo(cx + cellW * 0.33, cy + 2);
        ctx.lineTo(cx + cellW * 0.33, cy + cellH - 2);
        ctx.moveTo(cx + cellW * 0.66, cy + 2);
        ctx.lineTo(cx + cellW * 0.66, cy + cellH - 2);
        ctx.moveTo(cx + 2, cy + cellH / 2);
        ctx.lineTo(cx + cellW - 2, cy + cellH / 2);
        ctx.stroke();
      }
    }

    // Dust, only ahead of the spray pass: a flat ochre veil for the loss of
    // contrast, grain on top for the texture. Both scale with real coverage.
    const sweepX = state.sweep * box.w;
    if (soiling > 0.01) {
      // Two bands: still-dirty glass ahead of the nozzle, and glass behind it
      // that is clean now and soiling again at state.recover.
      const bands: [number, number, number][] = [
        [x, Math.min(sweepX, x + w), state.recover],
        [Math.max(x, sweepX), x + w, 1],
      ];

      for (const [from, to, strength] of bands) {
        if (to - from <= 0.5 || strength <= 0.01) continue;
        ctx.save();
        roundRect(ctx, x, y, w, h, 6);
        ctx.clip();
        ctx.beginPath();
        ctx.rect(from, y, to - from, h);
        ctx.clip();

        ctx.globalAlpha = Math.min(0.34, soiling * 0.36) * strength;
        ctx.fillStyle = "#c4813c";
        ctx.fillRect(x, y, w, h);

        ctx.globalAlpha = Math.min(0.5, soiling * 0.55) * strength;
        if (pattern) ctx.fillStyle = pattern;
        ctx.fillRect(x, y, w, h);
        ctx.restore();
      }
    }

    // a low sheen that drifts, so the glass reads as glass
    ctx.save();
    roundRect(ctx, x, y, w, h, 6);
    ctx.clip();
    const edge = ctx.createLinearGradient(x, y, x, y + h * 0.35);
    edge.addColorStop(0, "rgba(226, 236, 255, 0.14)");
    edge.addColorStop(1, "rgba(226, 236, 255, 0)");
    ctx.fillStyle = edge;
    ctx.fillRect(x, y, w, h * 0.35);
    ctx.restore();

    ctx.save();
    roundRect(ctx, x, y, w, h, 6);
    ctx.clip();
    const sheenX = x + (((state.glint + index * 0.17) % 1.4) - 0.2) * w;
    const sheen = ctx.createLinearGradient(sheenX, y, sheenX + w * 0.42, y + h);
    sheen.addColorStop(0, "rgba(255, 211, 122, 0)");
    sheen.addColorStop(0.5, "rgba(255, 211, 122, 0.07)");
    sheen.addColorStop(1, "rgba(255, 211, 122, 0)");
    ctx.fillStyle = sheen;
    ctx.fillRect(x, y, w, h);
    ctx.restore();

    ctx.restore();
  }

  function drawSpray() {
    const x = state.sweep * box.w;
    if (x < 0 || x > box.w) return;
    const band = ctx.createLinearGradient(x - 60, 0, x + 20, 0);
    band.addColorStop(0, "rgba(53, 214, 195, 0)");
    band.addColorStop(0.7, "rgba(53, 214, 195, 0.16)");
    band.addColorStop(1, "rgba(233, 255, 252, 0.5)");
    ctx.fillStyle = band;
    ctx.fillRect(x - 60, 0, 62, box.h);
  }

  function render() {
    ctx.clearRect(0, 0, box.w, box.h);
    if (box.w < 10) return;

    // Two rows of two modules, weighted to the right of the viewport so the
    // headline keeps the left third to itself.
    const wide = box.w > 900;
    const left = box.w * (wide ? 0.54 : 0.08);
    const right = box.w * (wide ? 0.96 : 0.92);
    const width = right - left;
    const gap = width * 0.045;
    const modW = (width - gap) / 2;
    const modH = modW * 0.54;
    const top = box.h * (wide ? 0.16 : 0.3);

    ctx.save();
    ctx.translate(left + width / 2, top + modH);
    ctx.rotate(-0.035);
    ctx.translate(-(left + width / 2), -(top + modH));

    // The far row is drawn smaller and inset, so the array has depth without
    // needing a real perspective transform.
    for (let i = 0; i < 4; i++) {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const shrink = row === 0 ? 0.88 : 1;
      const w = modW * shrink;
      const h = modH * shrink;
      ctx.globalAlpha = row === 0 ? 0.62 : 1;
      drawModule(
        left + col * (modW + gap) + (modW - w) / 2,
        top + row * (modH + gap),
        w,
        h,
        dust[i] ?? 0.3,
        i,
      );
      ctx.globalAlpha = 1;
    }
    drawSpray();
    ctx.restore();
  }

  return { resize, render, state };
}
