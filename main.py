import sys

from config import MODE
from logger import log_event
from messaging import build_message, send_whatsapp_message
from scheduler import (
    get_current_time,
    get_now,
    get_or_create_daily_schedule,
    get_today_date,
    is_allowed_weekday,
    is_within_execution_window,
    is_within_tolerance,
)
from storage import read_last_sent_date, write_last_sent_date


def main() -> None:
    print(f"[INFO] Running in {MODE} mode")

    today_date = get_today_date()
    current_time = get_current_time()
    now = get_now()

    if MODE == "PROD" and not is_allowed_weekday(now):
        print("[INFO] Today is not an allowed weekday.")
        log_event(
            date=today_date,
            time=current_time,
            status="skipped_day",
            detail="Today is not an allowed weekday",
        )
        sys.exit()

    scheduled_time, created_new_schedule = get_or_create_daily_schedule()

    if created_new_schedule:
        print(f"[INFO] New scheduled time for today: {scheduled_time}")
        log_event(
            date=today_date,
            time=current_time,
            status="schedule_created",
            scheduled_time=scheduled_time,
            detail="New daily schedule created",
        )

    if MODE == "PROD":
        if not is_within_execution_window(now):
            print(f"[INFO] Outside execution window. Now: {current_time}")
            log_event(
                date=today_date,
                time=current_time,
                status="skipped_window",
                scheduled_time=scheduled_time,
                detail="Outside execution window",
            )
            sys.exit()

        if not is_within_tolerance(scheduled_time, now):
            print(f"[INFO] Outside allowed tolerance. Scheduled: {scheduled_time} | Now: {current_time}")
            log_event(
                date=today_date,
                time=current_time,
                status="skipped_window",
                scheduled_time=scheduled_time,
                detail="Outside tolerance window",
            )
            sys.exit()

    last_sent_date = read_last_sent_date()

    if last_sent_date == today_date and MODE == "PROD":
        print("[INFO] Message already sent today. Skipping execution.")
        log_event(
            date=today_date,
            time=current_time,
            status="skipped_duplicate",
            scheduled_time=scheduled_time,
            detail="Message already sent today",
        )
        sys.exit()

    if last_sent_date == today_date and MODE == "TEST":
        print("[INFO] TEST mode: ignoring duplicate check")

    try:
        final_message = build_message()
        send_whatsapp_message(final_message)
        write_last_sent_date(today_date)

        print("[INFO] Message sent successfully!")

        log_event(
            date=today_date,
            time=current_time,
            status="sent",
            scheduled_time=scheduled_time,
            message=final_message,
            detail="Message sent successfully",
        )

    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

        log_event(
            date=today_date,
            time=current_time,
            status="error",
            scheduled_time=scheduled_time,
            detail=str(e),
        )

        raise


if __name__ == "__main__":
    main()