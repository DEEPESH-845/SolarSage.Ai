# Panel fixtures

Four **synthetic** frames standing in for the panel cameras. They are renders,
not photographs — `make_fixtures.py` draws a photovoltaic module and then soils
it, so the demo and the tests have four panels in genuinely different states.

Until now these four files were byte-identical copies of one image, so every
panel always reported the same dust level.

| File | Soiling applied | Measured coverage | State under the default thresholds |
|---|---|---|---|
| `panel_01_test.jpg` | none | ~23% | clean (below the 30% schedule threshold) |
| `panel_02_test.jpg` | 61% | ~43% | moderate dust — cleaning is scheduled |
| `panel_03_test.jpg` | 85% | ~66% | needs cleaning — past the 60% immediate threshold |
| `panel_04_test.jpg` | 100% | ~74% | needs cleaning, CRITICAL risk band |

The measured column is what `Agents/crew.py` reports, not what was painted on:
the renderer applies dust, and the classifier measures it independently.

Regenerate with:

```bash
python Backend/data/images/make_fixtures.py
```

The renderer is seeded, so every run produces identical bytes — a change to
these files is always deliberate. Replace them with real photographs whenever
camera frames are available; nothing else needs to change.
