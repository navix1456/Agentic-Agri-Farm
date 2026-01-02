import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_weather(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_month_risk(data: Dict[str, Any], state: str, month: str) -> Optional[Dict[str, Any]]:
    state_data = data.get(state, {})
    return state_data.get(month)


def build_risk_map(data: Dict[str, Any], state: str) -> Dict[str, Dict[str, Any]]:
    return data.get(state, {})
