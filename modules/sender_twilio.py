from __future__ import annotations

from twilio.rest import Client


def send_whatsapp_twilio_message(
    *,
    sid: str,
    token: str,
    from_number: str,
    to_number: str,
    body: str,
) -> None:
    client = Client(sid, token)
    client.messages.create(
        from_=from_number,
        to=f"whatsapp:+{to_number}" if not to_number.startswith("whatsapp:") else to_number,
        body=body,
    )