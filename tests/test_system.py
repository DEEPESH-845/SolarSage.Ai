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
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Must be set before anything imports Backend.config.settings.
TMP_DIR = tempfile.mkdtemp(prefix="solarsage-test-")
os.environ["DATA_DIR"] = TMP_DIR
os.environ.pop("SQLITE_DATABASE_PATH", None)
os.environ.pop("BACKEND_URL", None)

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
                 "/system/logs", "/settings", "/hardware/telemetry",
                 "/panels/panel_01/history", "/openapi.json"):
        assert client.get(path).status_code == 200, path

    assert client.post("/analyze", json={"panel_id": "panel_01"}).status_code == 200
    assert client.post("/spray", json={"panel_id": "panel_01"}).status_code == 200
    assert client.put("/settings", json={"values": {"dust_threshold": 42}}).json()["dust_threshold"] == 42
    assert client.post("/settings/reset").json()["dust_threshold"] == 60


def test_flask_pages_and_json_endpoints():
    from Frontend.app import app

    client = app.test_client()
    for path in ("/", "/dashboard", "/panels", "/settings", "/system-reports"):
        assert client.get(path).status_code == 200, path

    for path in ("/api/status", "/api/telemetry", "/api/settings",
                 "/api/system-reports", "/api/panel/panel_01"):
        assert client.get(path).status_code == 200, path

    assert client.get("/api/panel/not_a_panel").status_code == 404
    assert client.post("/api/system-mode", json={"mode": "nope"}).status_code == 400

    reports = client.get("/api/system-reports").get_json()
    assert isinstance(reports["logs"], list), "logs must stay a list — templates slice it"
    assert sum(reports["panel_health"][k] for k in
               ("clean", "moderate_dust", "needs_cleaning", "unknown")) == len(settings.panel_ids)

    # Actions write rows and open a valve, so they are POST-only and redirect back.
    assert client.post("/analyze/panel_01").status_code == 302
    assert client.post("/spray/panel_01").status_code == 302
    assert client.get("/analyze/panel_01").status_code == 405, "GET must not be able to spray"
    assert client.get("/spray/panel_01").status_code == 405

    # An unknown panel is rejected before it reaches the filesystem or the database.
    rejected = client.post("/analyze/../../etc/passwd", headers={"X-Requested-With": "fetch"})
    assert rejected.status_code in (400, 404), rejected.status_code

    # A write asked for by another origin is refused outright.
    foreign = client.post("/spray/panel_01", headers={"Origin": "https://evil.example"})
    assert foreign.status_code == 403, foreign.status_code

    # A referrer pointing off-site must not be used as the redirect target.
    bounced = client.post("/spray/panel_01", headers={"Referer": "https://evil.example/steal"})
    assert bounced.headers["Location"] in ("/dashboard", "/"), bounced.headers["Location"]


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
