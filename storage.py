import json
from pathlib import Path


DATA_DIR = Path("data")
SCHEDULE_FILE = DATA_DIR / "schedule.txt"
LAST_SENT_FILE = DATA_DIR / "last_sent.txt"
HISTORY_FILE = DATA_DIR / "history.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(exist_ok=True)


def read_schedule() -> tuple[str | None, str | None]:
    ensure_data_dir()

    if not SCHEDULE_FILE.exists():
        return None, None

    content = SCHEDULE_FILE.read_text(encoding="utf-8").strip()

    if "|" not in content:
        return None, None

    saved_date, scheduled_time = content.split("|", 1)
    return saved_date, scheduled_time


def write_schedule(today_date: str, scheduled_time: str) -> None:
    ensure_data_dir()
    SCHEDULE_FILE.write_text(f"{today_date}|{scheduled_time}", encoding="utf-8")


def read_last_sent_date() -> str | None:
    ensure_data_dir()

    if not LAST_SENT_FILE.exists():
        return None

    content = LAST_SENT_FILE.read_text(encoding="utf-8").strip()
    return content or None


def write_last_sent_date(today_date: str) -> None:
    ensure_data_dir()
    LAST_SENT_FILE.write_text(today_date, encoding="utf-8")


def load_history() -> list[dict]:
    ensure_data_dir()

    if not HISTORY_FILE.exists():
        return []

    try:
        content = HISTORY_FILE.read_text(encoding="utf-8").strip()

        if not content:
            return []

        data = json.loads(content)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def save_history(history: list[dict]) -> None:
    ensure_data_dir()
    HISTORY_FILE.write_text(
        json.dumps(history, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )