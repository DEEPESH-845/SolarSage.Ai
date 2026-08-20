#!/usr/bin/env python3
"""End-to-end check of the SolarSage stack.

Runs against a throwaway database in a temp directory, so it never touches the
real one. Run it with `python tests/test_system.py` (or `pytest tests/`).
"""

import json
import os
import sqlite3
import sys
import tempfile
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Must be set before anything imports Backend.config.settings.
TMP_DIR = tempfile.mkdtemp(prefix="solarsage-test-")
os.environ["DATA_DIR"] = TMP_DIR
os.environ.pop("SQLITE_DATABASE_PATH", None)
os.environ.pop("API_TOKEN", None)

from Backend import services  # noqa: E402
from Backend.config.settings import settings  # noqa: E402
from Backend.database.connection import SessionLocal, init_database  # noqa: E402

# Both app entrypoints do this on import; tests run in alphabetical order, so do
# it here rather than inside whichever test happens to sort first.
init_database()


def test_sqlite_available():
    assert sqlite3.sqlite_version_info >= (3, 8), sqlite3.sqlite_version
    assert settings.db_path.is_file(), f"database not created at {settings.db_path}"
    assert str(settings.db_path).startswith(TMP_DIR), "test must not use the real database"


def test_classifier_reads_the_image_fixtures():
    from Backend.agents.image_classifier import ImageClassifierAgent

    agent = ImageClassifierAgent()
    result = agent.classify_dust_level(settings.image_dir / "panel_01_test.jpg")

    assert "error" not in result, result
    assert 0.0 <= result["dust_level"] <= 1.0, result["dust_level"]
    assert 0.0 <= result["confidence"] <= 1.0, result["confidence"]
    assert result["status"] in {"LOW", "MODERATE", "HIGH", "CRITICAL"}, result["status"]
    assert result["daily_power_loss_kwh"] is not None, "forecast stage did not run"
    assert json.dumps(result), "result must be JSON-serialisable for the API"

    missing = agent.classify_dust_level(settings.image_dir / "does_not_exist.jpg")
    assert "error" in missing, missing


def test_fixtures_are_distinct_and_cover_every_decision_band():
    """They used to be four copies of one file, so every panel reported the same
    dust level and only one branch of the decision logic was ever exercised."""
    import hashlib

    from Backend.agents.image_classifier import ImageClassifierAgent

    images = [settings.image_dir / f"{p}_test.jpg" for p in settings.panel_ids]
    digests = {hashlib.md5(i.read_bytes()).hexdigest() for i in images}
    assert len(digests) == len(images), "the panel fixtures are not distinct images"

    agent = ImageClassifierAgent()
    coverage = [agent.classify_dust_level(i)["dust_level"] * 100 for i in images]
    assert coverage == sorted(coverage), f"fixtures should soil progressively: {coverage}"

    defaults = services.DEFAULT_SETTINGS
    assert coverage[0] < defaults["schedule_threshold"], f"panel_01 should read clean: {coverage[0]}"
    assert defaults["schedule_threshold"] < coverage[1] < defaults["dust_threshold"], (
        f"panel_02 should land between the thresholds: {coverage[1]}")
    assert coverage[2] > defaults["dust_threshold"], f"panel_03 should need cleaning: {coverage[2]}"
    assert coverage[3] > defaults["dust_threshold"], f"panel_04 should need cleaning: {coverage[3]}"


def test_the_same_frame_always_reads_the_same():
    """The classifier used to add Gaussian noise to its own measurement, so one
    image produced a different dust level on every run and the cleaning
    thresholds were being applied to that noise."""
    from Backend.agents.image_classifier import ImageClassifierAgent

    agent = ImageClassifierAgent()
    image = settings.image_dir / "panel_01_test.jpg"
    readings = [agent.classify_dust_level(image) for _ in range(4)]

    assert len({r["dust_level"] for r in readings}) == 1, [r["dust_level"] for r in readings]
    assert len({r["confidence"] for r in readings}) == 1
    assert len({r["daily_power_loss_kwh"] for r in readings}) == 1, "forecast must be reproducible too"
    assert len({tuple(r["insights"]) for r in readings}) == 1


def test_a_failed_analysis_reports_an_error_instead_of_inventing_one():
    """A fabricated dust level reaches the decision engine and opens a valve."""
    import numpy as np

    from Agents.crew import ProductionImageProcessor, standalone_analyze_image

    unreadable = Path(TMP_DIR) / "not_an_image.jpg"
    unreadable.write_text("plainly not a jpeg")
    assert "error" in standalone_analyze_image(str(unreadable))

    # An array the CV stage cannot handle must raise, not fall back to a guess.
    try:
        ProductionImageProcessor.process_image(np.zeros((8, 8), dtype=np.uint8))
        raise AssertionError("a broken frame produced a result")
    except Exception as e:
        assert "failed" in str(e).lower(), e


def test_decision_engine_survives_a_forecast_that_produced_nothing():
    """payback_days was only bound when there was a loss to pay back."""
    from Agents.crew import standalone_decision_engine

    result = standalone_decision_engine({"dust_level": 40, "confidence": 80}, {})
    assert "error" not in result, result
    assert result["cost_benefit_analysis"]["payback_period_days"] == 999


def test_a_refill_recorded_with_an_offset_still_counts_water():
    """An offset-carrying timestamp used to compare as a later moment than it was,
    hiding real usage from the tank guard."""
    from datetime import timedelta, timezone as tz

    db = SessionLocal()
    try:
        services.reset_settings(db)
        ist = tz(timedelta(hours=5, minutes=30))
        refilled = datetime.now(tz.utc) - timedelta(hours=1)
        services.update_settings(db, {"tank_refilled_at": refilled.astimezone(ist).isoformat()})

        stored = services.get_settings(db)["tank_refilled_at"]
        assert "+" not in stored, f"stored with an offset: {stored}"

        before = services.water_status(db)["used_ml"]
        services.spray_panel(db, "panel_01")
        after = services.water_status(db)["used_ml"]
        assert after > before, "a spray after the refill was not counted"
    finally:
        services.reset_settings(db)
        services.refill_tank(db)
        db.close()


def test_demo_seed_fills_an_empty_database_once():
    """A console deployed without hardware starts empty on every cold start, so the
    pages had nothing to show. Seeding must fill it — and never a second time."""
    import tempfile as _tempfile

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from Backend import demo
    from Backend.database.models import Base

    engine = create_engine(f"sqlite:///{_tempfile.mkdtemp(prefix='solarsage-demo-')}/fresh.db")
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    try:
        assert demo.seed_if_empty(db) is True, "an empty database was not seeded"

        panels = services.list_panels(db)["panels"]
        assert all(p["status"] != "unknown" for p in panels), panels
        assert all(p["last_cleaned"] != "Never" for p in panels), panels
        assert len({p["status"] for p in panels}) > 1, "every panel got the same state"

        for panel in panels:
            history = services.panel_history(db, panel["id"])["status_history"]
            assert len(history) > demo.HISTORY_POINTS, (panel["id"], len(history))

        stats = services.system_stats(db)
        assert stats["total_analyses"] and stats["total_cleanings"] and stats["water_used_total"]
        assert services.latest_decision(db).get("decision_id"), "no decision to show"
        assert services.get_settings(db)["demo_seeded_at"], "seeded data is not labelled"

        assert demo.seed_if_empty(db) is False, "seeded a database that already had rows"
        assert services.system_stats(db)["total_analyses"] == stats["total_analyses"]

        # The label survives a settings reset — the rows it describes do.
        services.reset_settings(db)
        assert services.get_settings(db)["demo_seeded_at"], "reset dropped the synthetic-data label"
    finally:
        db.close()


def test_log_limit_is_bounded():
    db = SessionLocal()
    try:
        assert len(services.system_logs(db, limit=10**9)) <= 500
        assert len(services.system_logs(db, limit=0)) <= 1
    finally:
        db.close()


def test_analyze_records_status_decision_and_log():
    db = SessionLocal()
    try:
        services.reset_settings(db)
        services.update_settings(db, {"auto_clean": False})

        result = services.analyze_panel(db, "panel_01")
        assert "error" not in result, result
        assert result["decision"] in {"spray_now", "schedule_cleaning", "no_action"}
        assert result["water_volume"] == result["spray_duration"] * services.ML_PER_SECOND_OF_SPRAY

        assert services.latest_decision(db)["decision_id"] == result["decision_id"]

        panels = {p["id"]: p for p in services.list_panels(db)["panels"]}
        assert panels["panel_01"]["dust_level"] == result["dust_level"]

        messages = [entry["message"] for entry in services.system_logs(db)]
        assert any("panel_01" in m for m in messages), messages
    finally:
        db.close()


def test_thresholds_drive_the_decision():
    db = SessionLocal()
    try:
        services.update_settings(db, {"dust_threshold": 0, "schedule_threshold": 0, "auto_clean": False})
        assert services.analyze_panel(db, "panel_02")["decision"] == "spray_now"

        services.update_settings(db, {"dust_threshold": 100, "schedule_threshold": 100})
        assert services.analyze_panel(db, "panel_02")["decision"] == "no_action"
    finally:
        services.reset_settings(db)
        db.close()


def test_auto_clean_executes_only_when_enabled_and_active():
    db = SessionLocal()
    try:
        services.reset_settings(db)
        services.update_settings(db, {"dust_threshold": 0, "auto_clean": True})
        assert "auto_clean" in services.analyze_panel(db, "panel_03")

        services.update_settings(db, {"auto_clean": False})
        assert "auto_clean" not in services.analyze_panel(db, "panel_03")

        services.update_settings(db, {"auto_clean": True, "system_mode": "paused"})
        assert "auto_clean" not in services.analyze_panel(db, "panel_03")
    finally:
        services.reset_settings(db)
        db.close()


def test_spray_respects_pause_and_the_water_tank():
    db = SessionLocal()
    try:
        services.reset_settings(db)
        services.refill_tank(db)

        ok = services.spray_panel(db, "panel_01")
        assert "error" not in ok, ok
        assert ok["water_used_ml"] > 0

        services.update_settings(db, {"system_mode": "paused"})
        assert "error" in services.spray_panel(db, "panel_01")

        # Drain the tank: one spray larger than the whole tank must be refused.
        services.update_settings(db, {"system_mode": "active", "spray_duration": 10_000})
        empty = services.spray_panel(db, "panel_01")
        assert "error" in empty and "Insufficient water" in empty["error"], empty

        failed = services.panel_history(db, "panel_01")["cleaning_history"][0]
        assert failed["success"] is False and failed["error_message"], failed
    finally:
        services.reset_settings(db)
        services.refill_tank(db)
        db.close()


def test_settings_reject_values_that_would_act_badly():
    db = SessionLocal()
    try:
        services.reset_settings(db)
        saved = services.update_settings(db, {
            "refresh_interval": 0,          # would become a browser timer of 0ms
            "dust_threshold": 4000,         # out of range
            "water_pressure": "firehose",   # not a real setting
            "auto_clean": "false",          # a string is not automatically True
            "preferred_time": "not a time",
        })
        assert saved["refresh_interval"] >= 5, saved["refresh_interval"]
        assert saved["dust_threshold"] == 100, saved["dust_threshold"]
        assert saved["water_pressure"] == "medium", saved["water_pressure"]
        assert saved["auto_clean"] is False, saved["auto_clean"]
        assert saved["preferred_time"] == "06:00", saved["preferred_time"]
    finally:
        services.reset_settings(db)
        db.close()


def test_unknown_panels_are_refused_everywhere():
    db = SessionLocal()
    try:
        for call in (services.analyze_panel, services.spray_panel, services.panel_history):
            result = call(db, "../../../etc/passwd")
            assert "error" in result and "Unknown panel" in result["error"], (call.__name__, result)
    finally:
        db.close()


def test_aggregates_and_bulk_operations():
    """These rules used to live in the Flask frontend. They are business rules —
    the tallies decide what the console shows and the scope decides what gets wet."""
    db = SessionLocal()
    try:
        services.reset_settings(db)
        services.refill_tank(db)

        counts = services.panel_counts(services.list_panels(db))
        assert counts["total"] == len(settings.panel_ids)
        assert counts["clean"] + counts["moderate_dust"] + counts["needs_cleaning"] \
            + counts["unknown"] == counts["total"]
        assert counts["attention"] == counts["moderate_dust"] + counts["needs_cleaning"]

        view = services.overview(db)
        assert set(view) == {"health", "panels", "counts", "stats",
                             "latest_decision", "settings", "timestamp"}
        assert len(view["panels"]) == counts["total"]

        detail = services.panel_detail(db, "panel_01")
        assert detail["panel"]["id"] == "panel_01"
        assert "status_history" in detail and "cleaning_history" in detail
        assert "error" in services.panel_detail(db, "../etc/passwd")

        services.update_settings(db, {"auto_clean": False})
        analysed = services.analyze_all(db)
        assert analysed["analysed"] == counts["total"], analysed
        assert not analysed["failures"], analysed["failures"]

        dirty = services.resolve_spray_scope(db, "dirty")
        every = services.resolve_spray_scope(db, "all")
        assert set(dirty) <= set(every) and len(every) == counts["total"]

        washed = services.spray_many(db, "all")
        assert washed["cleaned"] == len(every), washed
        assert washed["water_used_ml"] > 0

        # A paused system refuses every panel, and says so per panel.
        services.update_settings(db, {"system_mode": "paused"})
        refused = services.spray_many(db, "all")
        assert refused["cleaned"] == 0 and len(refused["failures"]) == len(every), refused

        try:
            services.resolve_spray_scope(db, "everything")
            raise AssertionError("an unknown scope was accepted")
        except ValueError:
            pass
    finally:
        services.reset_settings(db)
        services.refill_tank(db)
        db.close()


def test_health_and_stats_report_real_values():
    db = SessionLocal()
    try:
        health = services.health(db)
        assert health["camera_status"] == "online", health
        assert 0 <= health["water_level"] <= 100, health
        assert health["water"]["capacity_ml"] == settings.water_tank_capacity_ml

        stats = services.system_stats(db)
        assert stats["total_panels"] == len(settings.panel_ids)
        assert stats["total_analyses"] > 0 and stats["total_cleanings"] > 0
        assert 0 <= stats["avg_dust_level"] <= 1
    finally:
        db.close()


def test_hardware_telemetry_is_parsed():
    telemetry = services.latest_telemetry()
    assert telemetry["available"], telemetry
    assert telemetry["readings"], "no readings parsed from Hardware/panel_data_*.json"
    assert telemetry["avg_temperature"] is not None


def test_fastapi_routes():
    from fastapi.testclient import TestClient

    from Backend.api.main import app

    client = TestClient(app)
    for path in ("/", "/health", "/panels", "/latest-decision", "/system/stats",
                 "/system/logs", "/settings", "/hardware/telemetry", "/overview",
                 "/panels/panel_01/history", "/panels/panel_01/detail", "/openapi.json"):
        assert client.get(path).status_code == 200, path

    # The frontend renders these; an unknown panel must not reach the filesystem.
    assert client.get("/panels/not_a_panel/detail").status_code == 404
    assert client.post("/analyze", json={"panel_id": "../../etc/passwd"}).status_code == 404
    assert client.post("/panels/analyze-all").json()["analysed"] > 0
    assert client.post("/panels/spray", json={"scope": "dirty"}).status_code == 200
    assert client.post("/panels/spray", json={"scope": "sideways"}).status_code == 400

    assert client.post("/analyze", json={"panel_id": "panel_01"}).status_code == 200
    assert client.post("/spray", json={"panel_id": "panel_01"}).status_code == 200
    assert client.put("/settings", json={"values": {"dust_threshold": 42}}).json()["dust_threshold"] == 42
    assert client.post("/settings/reset").json()["dust_threshold"] == 60


def test_a_deployed_api_refuses_unauthenticated_writes():
    """The API is reachable from anywhere once deployed, and its POST routes open
    a valve. With API_TOKEN set, a write without the header must not act."""
    import importlib

    from fastapi.testclient import TestClient

    os.environ["API_TOKEN"] = "test-token"
    try:
        import Backend.api.main as api

        importlib.reload(api)
        client = TestClient(api.app)

        assert client.get("/panels").status_code == 200, "reads must stay open"
        assert client.post("/spray", json={"panel_id": "panel_01"}).status_code == 401
        assert client.post("/panels/spray", json={"scope": "all"}).status_code == 401
        assert client.put("/settings", json={"values": {"dust_threshold": 42}}).status_code == 401

        headers = {"X-API-Key": "test-token"}
        assert client.post("/spray", json={"panel_id": "panel_01"}, headers=headers).status_code == 200
    finally:
        os.environ.pop("API_TOKEN", None)
        importlib.reload(api)


def main():
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"  ✅ {test.__name__}")
        except Exception as e:
            failures += 1
            print(f"  ❌ {test.__name__}: {type(e).__name__}: {e}")

    print("=" * 60)
    print(f"{len(tests) - failures}/{len(tests)} passed" + (f" — {failures} FAILED" if failures else " 🎉"))
    return 1 if failures else 0


if __name__ == "__main__":
    print("🧪 SolarSage system tests")
    print("=" * 60)
    sys.exit(main())
