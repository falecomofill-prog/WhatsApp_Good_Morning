import random
from datetime import datetime
from zoneinfo import ZoneInfo

from config_loader import load_settings
from storage import read_schedule, write_schedule


settings = load_settings()

TZ = ZoneInfo(settings["timezone"])
START_WINDOW = settings["start_window"]
END_WINDOW = settings["end_window"]
TOLERANCE_SECONDS = settings["tolerance_seconds"]
ALLOWED_TIMES = settings["allowed_times"]
ALLOWED_WEEKDAYS = settings["allowed_weekdays"]


def get_now() -> datetime:
    return datetime.now(TZ)


def get_today_date() -> str:
    return get_now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    return get_now().strftime("%H:%M")


def get_current_weekday() -> int:
    return get_now().weekday()


def is_allowed_weekday(now: datetime | None = None) -> bool:
    if now is None:
        now = get_now()

    return now.weekday() in ALLOWED_WEEKDAYS


def time_string_to_datetime(time_str: str, reference: datetime | None = None) -> datetime:
    if reference is None:
        reference = get_now()

    hour, minute = map(int, time_str.split(":"))

    return reference.replace(hour=hour, minute=minute, second=0, microsecond=0)


def is_within_execution_window(now: datetime | None = None) -> bool:
    if now is None:
        now = get_now()

    start_dt = time_string_to_datetime(START_WINDOW, now)
    end_dt = time_string_to_datetime(END_WINDOW, now)

    return start_dt <= now <= end_dt


def get_or_create_daily_schedule() -> tuple[str, bool]:
    today_date = get_today_date()
    saved_date, scheduled_time = read_schedule()

    if saved_date == today_date and scheduled_time:
        return scheduled_time, False

    scheduled_time = random.choice(ALLOWED_TIMES)
    write_schedule(today_date, scheduled_time)
    return scheduled_time, True


def is_within_tolerance(scheduled_time: str, now: datetime | None = None) -> bool:
    if now is None:
        now = get_now()

    scheduled_dt = time_string_to_datetime(scheduled_time, now)
    difference = abs((now - scheduled_dt).total_seconds())

    return difference <= TOLERANCE_SECONDS