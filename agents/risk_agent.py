from __future__ import annotations

from typing import Any, Dict, List

from tools.weather_api import build_risk_map, get_month_risk


def assess_risk(state: str, month: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assess weather risk for a specific state and month."""
    risk = get_month_risk(weather_data, state, month) or {}
    return {
        "state": state,
        "month": month,
        "level": risk.get("level", "Medium"),
        "alert": risk.get("alert", ""),
    }


def full_risk_map(state: str, weather_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Get complete risk map for all months in a state."""
    return build_risk_map(weather_data, state)


def summarize_risks(risk_map: Dict[str, Dict[str, Any]]) -> List[str]:
    """Create formatted summary of monthly risks."""
    summary = []
    for month, info in risk_map.items():
        risk_level = info.get('level', 'Medium')
        emoji = "🟢" if risk_level == "Low" else "🟡" if risk_level == "Medium" else "🔴"
        summary.append(f"{emoji} **{month}:** {risk_level} | {info.get('alert', '')}")
    return summary
