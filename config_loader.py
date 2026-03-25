import json
from pathlib import Path


SETTINGS_FILE = Path("config") / "app_settings.json"


def load_settings() -> dict:
    if not SETTINGS_FILE.exists():
        raise FileNotFoundError(f"Settings file not found: {SETTINGS_FILE}")

    with SETTINGS_FILE.open("r", encoding="utf-8") as file:
        settings = json.load(file)

    required_fields = [
        "timezone",
        "start_window",
        "end_window",
        "tolerance_seconds",
        "allowed_times",
        "allowed_weekdays",
    ]

    missing_fields = [field for field in required_fields if field not in settings]

    if missing_fields:
        raise ValueError(
            f"Missing settings in {SETTINGS_FILE}: {', '.join(missing_fields)}"
        )

    if not isinstance(settings["allowed_times"], list) or not settings["allowed_times"]:
        raise ValueError("'allowed_times' must be a non-empty list.")

    if not isinstance(settings["allowed_weekdays"], list) or not settings["allowed_weekdays"]:
        raise ValueError("'allowed_weekdays' must be a non-empty list.")

    return settings