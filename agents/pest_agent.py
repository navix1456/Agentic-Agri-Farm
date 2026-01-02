from __future__ import annotations

from typing import Dict

SAFETY_TEXT = (
    "Avoid blanket chemical sprays. Prioritize scouting, pheromone traps, and RNAi-based "
    "precision strategies when available. Consult local experts for regulated inputs. "
    "This agent provides non-prescriptive, research-backed advisory guidance and explicitly "
    "avoids chemical dosage or medical recommendations."
)


PERSISTENT_PEST_NOTES = {
    "cotton": "Monitor for bollworm and whitefly; use trap-based monitoring first.",
    "rice": "Watch for stem borer and leaf folder; maintain field sanitation.",
    "wheat": "Scout for rust early; remove volunteer plants to reduce inoculum.",
}


def explain_pest(pest_or_crop: str) -> Dict[str, str]:
    """Provide pest management guidance with emphasis on RNAi and safety."""
    key = (pest_or_crop or "").lower()
    note = PERSISTENT_PEST_NOTES.get(key, "Emphasize scouting and threshold-based action.")
    return {
        "topic": pest_or_crop,
        "explanation": note,
        "safety": SAFETY_TEXT,
        "why_rnai": "RNAi targets pest genes precisely, reducing non-target impacts and resistance pressure.",
    }
