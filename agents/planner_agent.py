from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from tools.crop_calendar_loader import select_calendar_entry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EXPLANATION_KEYS = ["task", "when", "why", "how", "risk"]


def _decorate_task(task: Dict[str, Any], risk_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Enhance task with risk information from weather data."""
    # Ensure month is preserved from task
    month = task.get("month", "").strip() if task.get("month") else ""
    
    # Get risk info - use month if available, fallback to task's risk field
    risk_info = {}
    if month and month in risk_map:
        risk_info = risk_map.get(month, {})
    
    return {
        "month": month,  # Keep original month from calendar
        "task": task.get("task", ""),
        "when": task.get("when", month if month else ""),
        "why": task.get("why", ""),
        "how": task.get("how", ""),
        "risk": risk_info.get("level", task.get("risk", "Medium")),
        "risk_alert": risk_info.get("alert", ""),
    }


def generate_plan(
    calendar_data: Dict[str, Any],
    crop: str,
    state: str,
    season: str,
    risk_map: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    """Generate a seasonal farm plan with risk-aware tasks."""
    try:
        entries = select_calendar_entry(calendar_data, crop, state, season)
        if not entries:
            logger.warning(f"No calendar entry for {crop}/{state}/{season}")
            return {
                "crop": crop,
                "state": state,
                "season": season,
                "tasks": [],
                "note": f"No matching calendar entry found for {crop} in {state} during {season} season.",
            }

        tasks = [_decorate_task(task, risk_map) for task in entries]
        logger.info(f"Generated {len(tasks)} tasks for {crop}/{state}/{season}")
        return {
            "crop": crop,
            "state": state,
            "season": season,
            "tasks": tasks,
        }
    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        return {
            "crop": crop,
            "state": state,
            "season": season,
            "tasks": [],
            "note": f"Error generating plan: {str(e)}",
        }


def format_tasks(tasks: List[Dict[str, Any]]) -> List[str]:
    """Format tasks using TASK → WHEN → WHY → HOW → RISK structure."""
    formatted = []
    for idx, task in enumerate(tasks, 1):
        segment = f"**{idx}.** " + " | ".join(
            [
                f"**TASK:** {task.get('task','')}",
                f"**WHEN:** {task.get('when','')}",
                f"WHY:** {task.get('why','')}",
                f"**HOW:** {task.get('how','')}",
                f"**RISK:** {task.get('risk','')}",
            ]
        )
        if task.get("risk_alert"):
            segment = segment + f" | 🚨 **ALERT:** {task['risk_alert']}"
        formatted.append(segment)
    return formatted


def build_readiness(checklist: Dict[str, Any]) -> Dict[str, Any]:
    """Build input readiness checklist (non-monetary)."""
    return {
        "Seed availability": checklist.get("seed_available", "Unknown"),
        "Fertilizer type": checklist.get("fertilizer", "Unknown"),
        "Irrigation dependency": checklist.get("irrigation", "Unknown"),
        "Labor intensity": checklist.get("labor", "Unknown"),
        "Weather flags": checklist.get("weather_flags", []),
    }
