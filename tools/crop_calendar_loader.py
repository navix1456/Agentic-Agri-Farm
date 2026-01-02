import json
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_calendar(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def select_calendar_entry(
    data: Dict[str, Any], crop: str, state: str, season: str
) -> Optional[List[Dict[str, Any]]]:
    crop_data = data.get(crop)
    if not crop_data:
        return None
    state_data = crop_data.get(state)
    if not state_data:
        return None
    return state_data.get(season)
