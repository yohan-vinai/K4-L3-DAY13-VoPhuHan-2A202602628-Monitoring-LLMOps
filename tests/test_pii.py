from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_event_redacts_nested_log_values() -> None:
    raw_email = "student@example.edu.vn"
    raw_phone = "090 123 4567"
    event = {
        "event": "request_received",
        "session_id": "safe-session",
        "payload": {"message_preview": f"{raw_email}, {raw_phone}"},
    }

    scrubbed = scrub_event(None, "info", event)

    rendered = str(scrubbed)
    assert raw_email not in rendered
    assert raw_phone not in rendered
    assert "REDACTED_EMAIL" in rendered
    assert "REDACTED_PHONE_VN" in rendered


def test_scrub_text_redacts_identity_and_payment_card_numbers() -> None:
    text = "CCCD 001234567890; card 4111 1111 1111 1111"

    scrubbed = scrub_text(text)

    assert "001234567890" not in scrubbed
    assert "4111 1111 1111 1111" not in scrubbed
    assert "REDACTED_CCCD" in scrubbed
    assert "REDACTED_CREDIT_CARD" in scrubbed
