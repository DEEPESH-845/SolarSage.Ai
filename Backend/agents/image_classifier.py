"""Dust classification for the API layer.

Thin adapter over the computer-vision + forecasting pipeline that already lives
in ``Agents/crew.py``. That pipeline speaks percentages (0-100); the API and the
dashboard templates speak fractions (0-1), so the conversion happens here and
nowhere else.
"""

from pathlib import Path
from typing import Union

from Agents.crew import (
    standalone_analyze_image,
    standalone_decision_engine,
    standalone_solar_forecast,
)

DEFAULT_LOCATION = "Bengaluru, India"


def _val(x):
    """Enum members survive model_dump(); str() on them yields 'Cls.NAME'."""
    return getattr(x, "value", x)


class ImageClassifierAgent:
    """Analyses a panel image and returns dust level plus economic context."""

    def __init__(self, location: str = DEFAULT_LOCATION):
        self.location = location

    def classify_dust_level(self, image_path: Union[str, Path]) -> dict:
        path = Path(image_path)
        if not path.exists():
            return {"error": f"Image not found: {path}"}

        analysis = standalone_analyze_image(str(path))
        if "error" in analysis:
            return analysis

        forecast = standalone_solar_forecast(self.location, analysis)
        if "error" in forecast:
            return forecast

        decision = standalone_decision_engine(analysis, forecast)
        if "error" in decision:
            return decision

        cost_benefit = decision.get("cost_benefit_analysis", {})
        return {
            # Fractions — the API thresholds and dashboard templates expect 0-1.
            "dust_level": round(analysis["dust_level"] / 100, 4),
            "confidence": round(analysis["confidence"] / 100, 4),
            "status": _val(analysis["risk_category"]),
            # Context carried through from the forecasting/economic stages.
            "visual_score": analysis["visual_score"],
            "image_quality": analysis["image_quality"],
            "insights": analysis["ai_insights"],
            "processing_time_ms": round(analysis["processing_time_ms"], 1),
            "daily_power_loss_kwh": forecast["daily_power_loss_kwh"],
            "power_loss_percentage": forecast["power_loss_percentage"],
            "optimal_cleaning_window": _val(forecast["optimal_cleaning_window"]),
            "cleaning_cost_usd": forecast["economic_factors"].get("cleaning_cost_usd"),
            "estimated_savings_weekly": decision["estimated_savings_weekly"],
            "roi_percentage": cost_benefit.get("roi_percentage"),
            "payback_period_days": cost_benefit.get("payback_period_days"),
            "recommendation": _val(decision["cleaning_priority"]),
            "reasoning": decision["llama_reasoning"],
        }
