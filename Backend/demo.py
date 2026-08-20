"""Synthetic panel history for a deployment with no hardware behind it.

The console is deployable on its own (Vercel), where there is no ESP32, no
camera and no persistent disk: the database is recreated empty on every cold
start, so every panel reads "unknown", the ledger reads zero and the decision
card is a hole. That is an accurate picture of an empty database and a useless
picture of the system.

So an empty database gets one plausible week of operation, generated the same
way the real thing generates it: the classifier runs over the synthetic image
fixtures (see Backend/data/images/README.md), and the analyses it returns are
back-filled as if dust had been accumulating since each panel's last wash.
Nothing here fabricates a measurement — the dust levels, forecasts and
economics are what the pipeline actually reports for those frames.

Seeded rows are marked with the `demo_seeded_at` setting, which is what the
console reads to label itself as demo data. Set DEMO_DATA=false to keep an
empty database empty.
"""

import json
import logging
from datetime import timedelta
from itertools import cycle

from sqlalchemy.orm import Session

from Backend import services
from Backend.config.settings import settings
from Backend.database.models import CleaningAction, PanelStatus, SystemSetting, utcnow

log = logging.getLogger(__name__)

# Days since each panel was last washed, oldest wash on the dustiest fixture —
# which is why the fixtures read progressively dirtier in that same order.
DAYS_SINCE_WASH = (2, 6, 10, 14)
HISTORY_POINTS = 6  # readings between that wash and now


def _history(dust_now: float, washed_days_ago: float):
    """Dust climbing back linearly from a wash to today's measured coverage."""
    for point in range(HISTORY_POINTS):
        share = (point + 1) / (HISTORY_POINTS + 1)  # strictly between wash and now
        yield washed_days_ago * (1 - share), round(dust_now * share, 4)


def _backfill(db: Session, panel_id: str, current: dict, washed_days_ago: float):
    """Write the wash, and the readings taken since it, behind today's analysis."""
    now = utcnow()
    config = services.get_settings(db)

    db.add(
        CleaningAction(
            panel_id=panel_id,
            timestamp=now - timedelta(days=washed_days_ago),
            action_type="spray",
            water_volume=config["spray_duration"] * services.ML_PER_SECOND_OF_SPRAY,
            duration=config["spray_duration"],
            success=True,
        )
    )

    for days_ago, dust in _history(current["dust_level"], washed_days_ago):
        db.add(
            PanelStatus(
                panel_id=panel_id,
                timestamp=now - timedelta(days=days_ago),
                dust_level=dust,
                classification_confidence=current["confidence"],
                is_dirty=dust * 100 > config["schedule_threshold"],
                needs_cleaning=dust * 100 > config["dust_threshold"],
                image_path=str(settings.image_dir / f"{panel_id}_test.jpg"),
            )
        )


def seed_if_empty(db: Session) -> bool:
    """Populate a database that has never seen an analysis. Returns whether it did.

    Never raises: a deployment that cannot seed itself must still serve pages.
    """
    if not settings.demo_data:
        return False
    try:
        if db.query(PanelStatus).count():
            return False

        seeded = 0
        for panel_id, washed_days_ago in zip(settings.panel_ids, cycle(DAYS_SINCE_WASH)):
            # The real pipeline, on the fixture frame: this writes today's status,
            # the decision it drove and — if the panel is past the threshold and
            # auto-cleaning is on — the wash that followed.
            current = services.analyze_panel(db, panel_id)
            if "error" in current:
                log.warning("Demo seed skipped %s: %s", panel_id, current["error"])
                continue
            _backfill(db, panel_id, current, washed_days_ago)
            seeded += 1

        if not seeded:
            return False

        db.add(SystemSetting(key="demo_seeded_at", value=json.dumps(utcnow().isoformat())))
        services.log_event(
            db, "WARNING", "demo",
            f"No hardware connected — seeded {seeded} panel(s) with synthetic history",
            {"panels": seeded, "source": "image fixtures"},
        )
        db.commit()
        log.info("Seeded demo data for %d panel(s)", seeded)
        return True
    except Exception:
        log.exception("Demo seed failed — continuing with an empty database")
        db.rollback()
        return False
