from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class AppConfig:
    mode: str

    destination_phone: str
    chrome_profile_path: str
    chrome_profile_directory: str
    whatsapp_web_url: str

    greetings_file: str
    messages_file: str

    headless: bool
    enable_headless_fallback: bool
    use_random_delay: bool

    login_timeout_seconds: int
    element_timeout_seconds: int
    page_load_timeout_seconds: int
    script_timeout_seconds: int

    min_open_delay_seconds: int
    max_open_delay_seconds: int
    min_pre_send_delay_seconds: int
    max_pre_send_delay_seconds: int
    min_post_send_delay_seconds: int
    max_post_send_delay_seconds: int

    max_retries: int
    retry_delay_seconds: int

    chromedriver_path: str

    send_window_enabled: bool
    send_window_start: str
    send_window_end: str

    @property
    def my_whatsapp_number(self) -> str:
        return self.destination_phone

    @property
    def element_timeout(self) -> int:
        return self.element_timeout_seconds

    @property
    def page_load_timeout(self) -> int:
        return self.page_load_timeout_seconds

    @property
    def script_timeout(self) -> int:
        return self.script_timeout_seconds


def _get_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _get_optional(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name, str(default)).strip()
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"Environment variable {name} must be an integer.") from exc


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name, str(default)).strip().lower()

    if raw in {"true", "1", "yes", "y", "on"}:
        return True

    if raw in {"false", "0", "no", "n", "off"}:
        return False

    raise ValueError(f"Environment variable {name} must be a boolean (true/false).")


def _validate_non_negative(name: str, value: int) -> None:
    if value < 0:
        raise ValueError(f"{name} cannot be negative.")


def _validate_range(min_name: str, max_name: str, min_value: int, max_value: int) -> None:
    if min_value > max_value:
        raise ValueError(f"{min_name} cannot be greater than {max_name}.")


def _validate_phone(phone: str) -> None:
    normalized = "".join(ch for ch in phone if ch.isdigit())

    if len(normalized) < 10:
        raise ValueError(
            "DESTINATION_PHONE appears invalid. "
            "Use country code + area code + number, digits only."
        )


def _validate_mode(mode: str) -> str:
    normalized = mode.strip().upper()

    if normalized not in {"TEST", "PROD"}:
        raise ValueError("MODE must be either TEST or PROD.")

    return normalized


def _validate_time_hhmm(name: str, value: str) -> None:
    parts = value.split(":")

    if len(parts) != 2:
        raise ValueError(f"{name} must be in HH:MM format.")

    hour_str, minute_str = parts

    if not hour_str.isdigit() or not minute_str.isdigit():
        raise ValueError(f"{name} must be in HH:MM format.")

    hour = int(hour_str)
    minute = int(minute_str)

    if not (0 <= hour <= 23):
        raise ValueError(f"{name} hour must be between 00 and 23.")

    if not (0 <= minute <= 59):
        raise ValueError(f"{name} minute must be between 00 and 59.")


def load_config() -> AppConfig:
    load_dotenv()

    config = AppConfig(
        mode=_validate_mode(_get_optional("MODE", "PROD")),

        destination_phone=_get_required("DESTINATION_PHONE"),
        chrome_profile_path=_get_required("CHROME_PROFILE_PATH"),
        chrome_profile_directory=_get_optional("CHROME_PROFILE_DIRECTORY", "Default"),
        whatsapp_web_url=_get_optional("WHATSAPP_WEB_URL", "https://web.whatsapp.com"),

        greetings_file=_get_required("GREETINGS_FILE"),
        messages_file=_get_required("MESSAGES_FILE"),

        headless=_get_bool("HEADLESS", False),
        enable_headless_fallback=_get_bool("ENABLE_HEADLESS_FALLBACK", True),
        use_random_delay=_get_bool("USE_RANDOM_DELAY", True),

        login_timeout_seconds=_get_int("LOGIN_TIMEOUT_SECONDS", 120),
        element_timeout_seconds=_get_int("ELEMENT_TIMEOUT_SECONDS", 60),
        page_load_timeout_seconds=_get_int("PAGE_LOAD_TIMEOUT_SECONDS", 60),
        script_timeout_seconds=_get_int("SCRIPT_TIMEOUT_SECONDS", 60),

        min_open_delay_seconds=_get_int("MIN_OPEN_DELAY_SECONDS", 2),
        max_open_delay_seconds=_get_int("MAX_OPEN_DELAY_SECONDS", 5),

        min_pre_send_delay_seconds=_get_int("MIN_PRE_SEND_DELAY_SECONDS", 3),
        max_pre_send_delay_seconds=_get_int("MAX_PRE_SEND_DELAY_SECONDS", 7),

        min_post_send_delay_seconds=_get_int("MIN_POST_SEND_DELAY_SECONDS", 2),
        max_post_send_delay_seconds=_get_int("MAX_POST_SEND_DELAY_SECONDS", 4),

        max_retries=_get_int("MAX_RETRIES", 2),
        retry_delay_seconds=_get_int("RETRY_DELAY_SECONDS", 5),

        chromedriver_path=_get_optional("CHROMEDRIVER_PATH", ""),

        send_window_enabled=_get_bool("SEND_WINDOW_ENABLED", False),
        send_window_start=_get_optional("SEND_WINDOW_START", "08:30"),
        send_window_end=_get_optional("SEND_WINDOW_END", "09:30"),
    )

    _validate_phone(config.destination_phone)

    _validate_non_negative("LOGIN_TIMEOUT_SECONDS", config.login_timeout_seconds)
    _validate_non_negative("ELEMENT_TIMEOUT_SECONDS", config.element_timeout_seconds)
    _validate_non_negative("PAGE_LOAD_TIMEOUT_SECONDS", config.page_load_timeout_seconds)
    _validate_non_negative("SCRIPT_TIMEOUT_SECONDS", config.script_timeout_seconds)
    _validate_non_negative("MAX_RETRIES", config.max_retries)
    _validate_non_negative("RETRY_DELAY_SECONDS", config.retry_delay_seconds)

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

    _validate_time_hhmm("SEND_WINDOW_START", config.send_window_start)
    _validate_time_hhmm("SEND_WINDOW_END", config.send_window_end)

    return config