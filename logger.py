from storage import load_history, save_history


def log_event(
    *,
    date: str,
    time: str,
    status: str,
    scheduled_time: str | None = None,
    message: str | None = None,
    detail: str | None = None,
) -> None:
    history = load_history()

    entry = {
        "date": date,
        "time": time,
        "status": status,
        "scheduled_time": scheduled_time,
        "message": message,
        "detail": detail,
    }

    history.append(entry)
    save_history(history)