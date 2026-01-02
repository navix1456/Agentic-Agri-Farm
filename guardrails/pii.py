import re

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4})")


def _mask_email(match: re.Match) -> str:
    email = match.group(0)
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked_local = "***"
    else:
        masked_local = f"{local[0]}***{local[-1]}"
    return f"{masked_local}@{domain}"


def _mask_phone(match: re.Match) -> str:
    raw = match.group(0)
    digits = re.sub(r"\D", "", raw)
    if len(digits) <= 2:
        return "**"
    masked = "*" * (len(digits) - 2) + digits[-2:]
    return masked


def mask_pii(text: str) -> str:
    if not text:
        return text
    masked = EMAIL_PATTERN.sub(_mask_email, text)
    masked = PHONE_PATTERN.sub(_mask_phone, masked)
    return masked


def contains_pii(text: str) -> bool:
    if not text:
        return False
    return bool(EMAIL_PATTERN.search(text) or PHONE_PATTERN.search(text))


def redact_and_flag(text: str) -> tuple[str, bool]:
    """Return masked text and flag if any PII was detected."""
    masked = mask_pii(text)
    return masked, masked != text
