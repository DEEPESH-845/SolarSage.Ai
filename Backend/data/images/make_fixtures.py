#!/usr/bin/env python3
"""Regenerate the four synthetic panel fixtures.

These are NOT photographs. They are rendered stand-ins for camera frames, used
so the demo and the tests have four panels in visibly different states instead
of four copies of one file. Every run produces identical bytes — the renderer is
seeded — so a fixture change is always a deliberate, reviewable one.

Each fixture renders the same module and then soils it: a tan blotch layer,
local contrast loss and desaturation, which is what the classifier in
Agents/crew.py actually measures. The four levels are chosen to land either side
of the default thresholds (schedule 30%, immediate 60%), so an analysis run
exercises the clean, scheduled and immediate paths rather than only one.

    python Backend/data/images/make_fixtures.py
"""

import sys
from pathlib import Path

import cv2
import numpy as np

WIDTH, HEIGHT = 640, 480
COLS, ROWS = 6, 4

# Soiling strength per panel, tuned so the measured coverage spans the bands.
# The measured value is printed on regeneration and asserted in the tests.
FIXTURES = {
    "panel_01": 0.00,  # just washed
    "panel_02": 0.61,  # dusty enough to schedule
    "panel_03": 0.85,  # past the immediate threshold
    "panel_04": 1.00,  # heavily soiled
}


def render_module(rng: np.random.Generator) -> np.ndarray:
    """A clean photovoltaic module: silicon cells, busbars, frame, gloss."""
    image = np.full((HEIGHT, WIDTH, 3), (26, 20, 14), dtype=np.uint8)  # BGR frame

    margin, gap = 26, 6
    cell_w = (WIDTH - 2 * margin - (COLS - 1) * gap) // COLS
    cell_h = (HEIGHT - 2 * margin - (ROWS - 1) * gap) // ROWS

    for row in range(ROWS):
        for col in range(COLS):
            x = margin + col * (cell_w + gap)
            y = margin + row * (cell_h + gap)

            # Monocrystalline blue as it photographs in sunlight: bright and
            # saturated. A clean panel has to read bright, because the classifier
            # treats darkness as soiling.
            base = np.array([210, 132, 72], dtype=np.float64)  # BGR
            base += rng.normal(0, 5, 3)
            cell = np.full((cell_h, cell_w, 3), base.clip(0, 255), dtype=np.uint8)

            # Diagonal crystal sheen keeps local contrast high on a clean panel.
            sheen = np.linspace(-18, 18, cell_w, dtype=np.float64)
            cell = np.clip(cell.astype(np.float64) + sheen[None, :, None], 0, 255).astype(np.uint8)

            # Silver busbars: fine fingers plus a collector. These are the edges
            # the classifier looks for, and the first thing dust hides.
            for fx in range(cell_w // 8, cell_w - 2, max(6, cell_w // 8)):
                cv2.line(cell, (fx, 2), (fx, cell_h - 3), (232, 232, 232), 1)
            cv2.line(cell, (2, cell_h // 2), (cell_w - 3, cell_h // 2), (244, 244, 244), 2)

            image[y:y + cell_h, x:x + cell_w] = cell

    # Daylight on the glass: an overall lift plus the sky caught along the top.
    glare = np.full((HEIGHT, WIDTH), 34.0)
    glare[:HEIGHT // 2] += np.linspace(52, 0, HEIGHT // 2)[:, None]
    return np.clip(image.astype(np.float64) + glare[:, :, None], 0, 255).astype(np.uint8)


def soil(image: np.ndarray, level: float, rng: np.random.Generator) -> np.ndarray:
    """Lay dust over a module: tan blotches, softened detail, lost colour."""
    if level <= 0:
        return image

    out = image.astype(np.float64)

    # Blotchy deposit rather than an even wash — dust settles unevenly.
    noise = rng.random((HEIGHT // 8, WIDTH // 8))
    blotches = cv2.resize(noise, (WIDTH, HEIGHT), interpolation=cv2.INTER_CUBIC)
    blotches = cv2.GaussianBlur(blotches, (0, 0), 9)
    blotches = (blotches - blotches.min()) / (np.ptp(blotches) + 1e-9)
    alpha = (0.25 + 0.75 * blotches) * level

    dust_colour = np.array([120, 158, 186], dtype=np.float64)  # BGR, warm grey-tan
    out = out * (1 - alpha[:, :, None]) + dust_colour * alpha[:, :, None]

    # Dust scatters light, so edges and local contrast go first.
    blurred = cv2.GaussianBlur(out, (0, 0), 0.6 + 3.4 * level)
    out = out * (1 - level * 0.85) + blurred * (level * 0.85)

    # ...and the blue desaturates towards grey.
    grey = cv2.cvtColor(out.astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float64)
    out = out * (1 - level * 0.55) + grey[:, :, None] * (level * 0.55)

    # Fine grain on top, so the surface still reads as a surface.
    out += rng.normal(0, 2.5 * level, out.shape)
    return np.clip(out, 0, 255).astype(np.uint8)


def main() -> int:
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here.parents[2]))
    from Agents.crew import standalone_analyze_image  # noqa: E402

    for index, (panel_id, level) in enumerate(FIXTURES.items()):
        rng = np.random.default_rng(20250612 + index)  # seeded: identical bytes every run
        frame = soil(render_module(rng), level, rng)
        path = here / f"{panel_id}_test.jpg"
        cv2.imwrite(str(path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 92])

        measured = standalone_analyze_image(str(path))
        print(
            f"{panel_id}  soiling {level:>4.0%}  ->  measured {measured['dust_level']:5.2f}% "
            f"({measured['risk_category'].value})  confidence {measured['confidence']:.0f}%"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
