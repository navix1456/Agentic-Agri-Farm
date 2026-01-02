from __future__ import annotations

BLOCKED_KEYWORDS = [
    # Medical/Health
    "medical advice",
    "prescription",
    "doctor",
    "cure",
    "treat",
    "disease",
    
    # Chemical/Pesticide dosing
    "dosage",
    "dose",
    "ml per",
    "kg per",
    "chemical spray",
    "pesticide",
    "insecticide",
    "herbicide",
    "fungicide",
    "poison",
    
    # Illegal activity
    "illicit",
    "illegal",
    "contraband",
    "narcotic",
    "smuggle",
    "steal",
    "black market",
]

SAFETY_NOTICE = (
    "This system provides advisory guidance only and does not give medical or chemical "
    "dosage instructions. Consult local agronomists or authorities for restricted topics."
)


def is_safe(text: str) -> bool:
    if not text:
        return True
    lowered = text.lower()
    return not any(keyword in lowered for keyword in BLOCKED_KEYWORDS)


def enforce_safety(text: str) -> tuple[bool, str]:
    """Return (allowed, message)."""
    if is_safe(text):
        return True, ""
    return False, SAFETY_NOTICE
