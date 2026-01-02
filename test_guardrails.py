"""Unit tests for guardrails module."""

from guardrails.pii import contains_pii, mask_pii, redact_and_flag
from guardrails.safety import enforce_safety, is_safe


def test_email_masking():
    text = "Contact me at farmer@example.com"
    masked = mask_pii(text)
    assert "farmer@example.com" not in masked
    assert "@example.com" in masked
    print(f"✓ Email masking: {masked}")


def test_phone_masking():
    text = "Call me at 9876543210"
    masked = mask_pii(text)
    assert "9876543210" not in masked
    assert masked.endswith("10")
    print(f"✓ Phone masking: {masked}")


def test_pii_detection():
    assert contains_pii("My email is test@test.com")
    assert contains_pii("Phone: 1234567890")
    assert not contains_pii("Hello world")
    print("✓ PII detection working")


def test_redact_and_flag():
    text, flagged = redact_and_flag("Email: farmer@farm.com, phone: 9999999999")
    assert flagged
    assert "farmer@farm.com" not in text
    assert "9999999999" not in text
    print(f"✓ Redact and flag: {text}")


def test_safety_filter():
    assert not is_safe("Give me pesticide dosage")
    assert not is_safe("I need medical advice")
    assert is_safe("Plan my rice crop")
    print("✓ Safety filter working")


def test_enforce_safety():
    allowed, msg = enforce_safety("Plan my wheat season")
    assert allowed
    assert msg == ""
    
    blocked, msg = enforce_safety("What chemical spray dose?")
    assert not blocked
    assert "advisory guidance" in msg
    print(f"✓ Enforce safety: {msg[:50]}...")


if __name__ == "__main__":
    print("Running guardrails tests...\n")
    test_email_masking()
    test_phone_masking()
    test_pii_detection()
    test_redact_and_flag()
    test_safety_filter()
    test_enforce_safety()
    print("\n✅ All tests passed!")
