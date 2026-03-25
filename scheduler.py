import random
from datetime import datetime
from zoneinfo import ZoneInfo

from storage import read_schedule, write_schedule


TZ = ZoneInfo("America/Sao_Paulo")

ALLOWED_TIMES = [
    "07:30",
    "07:40",
    "07:50",
    "08:00",
    "08:10",
    "08:20",
    "08:30",
]

START_WINDOW = "07:30"
END_WINDOW = "08:30"
TOLERANCE_SECONDS = 600


def get_now() -> datetime:
    return datetime.now(TZ)


def get_today_date() -> str:
    return get_now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    return get_now().strftime("%H:%M")


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