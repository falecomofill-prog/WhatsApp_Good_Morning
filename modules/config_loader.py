from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AppConfig:
    sender_mode: str
    destination_phone: str
    chrome_profile_path: str
    whatsapp_web_url: str
    greetings_file: str
    messages_file: str
    headless: bool
    login_timeout_seconds: int
    element_timeout_seconds: int
    min_open_delay_seconds: int
    max_open_delay_seconds: int
    min_pre_send_delay_seconds: int
    max_pre_send_delay_seconds: int
    min_post_send_delay_seconds: int
    max_post_send_delay_seconds: int
    max_retries: int
    retry_delay_seconds: int
    twilio_sid: str
    twilio_token: str
    twilio_whatsapp_number: str


def _get_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()
    if raw in {"true", "1", "yes", "y"}:
        return True
    if raw in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Environment variable {name} must be a boolean (true/false).")


def _validate_range(min_name: str, max_name: str, min_value: int, max_value: int) -> None:
    if min_value > max_value:
        raise ValueError(f"{min_name} cannot be greater than {max_name}.")


def _validate_sender_mode(mode: str) -> None:
    allowed = {"selenium", "twilio"}
    if mode not in allowed:
        raise ValueError(f"SENDER_MODE must be one of: {', '.join(sorted(allowed))}")


def load_config() -> AppConfig:
    load_dotenv()

    sender_mode = _get_required("SENDER_MODE").lower().strip()
    _validate_sender_mode(sender_mode)

    config = AppConfig(
        sender_mode=sender_mode,
        destination_phone=_get_required("DESTINATION_PHONE"),
        chrome_profile_path=_get_required("CHROME_PROFILE_PATH"),
        whatsapp_web_url=_get_required("WHATSAPP_WEB_URL"),
        greetings_file=_get_required("GREETINGS_FILE"),
        messages_file=_get_required("MESSAGES_FILE"),
        headless=_get_bool("HEADLESS", False),
        login_timeout_seconds=_get_int("LOGIN_TIMEOUT_SECONDS", 120),
        element_timeout_seconds=_get_int("ELEMENT_TIMEOUT_SECONDS", 60),
        min_open_delay_seconds=_get_int("MIN_OPEN_DELAY_SECONDS", 2),
        max_open_delay_seconds=_get_int("MAX_OPEN_DELAY_SECONDS", 5),
        min_pre_send_delay_seconds=_get_int("MIN_PRE_SEND_DELAY_SECONDS", 3),
        max_pre_send_delay_seconds=_get_int("MAX_PRE_SEND_DELAY_SECONDS", 7),
        min_post_send_delay_seconds=_get_int("MIN_POST_SEND_DELAY_SECONDS", 2),
        max_post_send_delay_seconds=_get_int("MAX_POST_SEND_DELAY_SECONDS", 4),
        max_retries=_get_int("MAX_RETRIES", 2),
        retry_delay_seconds=_get_int("RETRY_DELAY_SECONDS", 5),
        twilio_sid=os.getenv("TWILIO_SID", "").strip(),
        twilio_token=os.getenv("TWILIO_TOKEN", "").strip(),
        twilio_whatsapp_number=os.getenv("TWILIO_WHATSAPP_NUMBER", "").strip(),
    )

    _validate_range(
        "MIN_OPEN_DELAY_SECONDS",
        "MAX_OPEN_DELAY_SECONDS",
        config.min_open_delay_seconds,
        config.max_open_delay_seconds,
    )
    _validate_range(
        "MIN_PRE_SEND_DELAY_SECONDS",
        "MAX_PRE_SEND_DELAY_SECONDS",
        config.min_pre_send_delay_seconds,
        config.max_pre_send_delay_seconds,
    )
    _validate_range(
        "MIN_POST_SEND_DELAY_SECONDS",
        "MAX_POST_SEND_DELAY_SECONDS",
        config.min_post_send_delay_seconds,
        config.max_post_send_delay_seconds,
    )

    if config.sender_mode == "twilio":
        if not config.twilio_sid:
            raise ValueError("TWILIO_SID is required when SENDER_MODE=twilio")
        if not config.twilio_token:
            raise ValueError("TWILIO_TOKEN is required when SENDER_MODE=twilio")
        if not config.twilio_whatsapp_number:
            raise ValueError("TWILIO_WHATSAPP_NUMBER is required when SENDER_MODE=twilio")

    return config