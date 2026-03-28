from __future__ import annotations

import os
import random
import time
from datetime import datetime, timedelta

from modules.config_loader import load_config
from modules.logger import log_error, log_info, log_success, log_warning
from modules.message_generator import generate_message
from modules.sender_web import (
    WhatsAppChatError,
    WhatsAppDeliveryError,
    WhatsAppLoginError,
    WhatsAppMessageError,
    WhatsAppSendError,
    send_whatsapp_message,
)


LAST_SENT_FILE = "data/last_sent.txt"


class SimpleLogger:
    @staticmethod
    def info(message: str) -> None:
        log_info(message)

    @staticmethod
    def warning(message: str) -> None:
        log_warning(message)

    @staticmethod
    def error(message: str) -> None:
        log_error(message)

    @staticmethod
    def success(message: str) -> None:
        log_success(message)


def format_seconds_to_mmss(seconds: int) -> str:
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m{remaining_seconds:02d}s"


def _parse_hhmm_to_datetime(time_str: str, base_date: datetime) -> datetime:
    hour_str, minute_str = time_str.split(":")
    return base_date.replace(
        hour=int(hour_str),
        minute=int(minute_str),
        second=0,
        microsecond=0,
    )


def _sleep_until_random_time_in_window(config, logger: SimpleLogger) -> None:
    mode = getattr(config, "mode", "PROD").strip().upper()

    if mode == "TEST":
        logger.info("MODE=TEST detected. Send window will be ignored and execution will continue immediately.")
        return

    if not config.send_window_enabled:
        logger.info("Send window disabled. Proceeding immediately.")
        return

    now = datetime.now()
    window_start = _parse_hhmm_to_datetime(config.send_window_start, now)
    window_end = _parse_hhmm_to_datetime(config.send_window_end, now)

    if window_end <= window_start:
        raise ValueError("SEND_WINDOW_END must be later than SEND_WINDOW_START on the same day.")

    if now > window_end:
        logger.warning(
            f"Current time is already past the configured send window "
            f"({config.send_window_start} - {config.send_window_end}). "
            f"This execution will skip sending."
        )
        raise RuntimeError("Execution started after the send window ended.")

    effective_start = max(now, window_start)
    available_seconds = int((window_end - effective_start).total_seconds())

    if available_seconds <= 0:
        logger.warning("No time remaining in the configured send window. Skipping send.")
        raise RuntimeError("No time remaining in the send window.")

    random_delay_seconds = random.randint(0, available_seconds)
    scheduled_time = effective_start + timedelta(seconds=random_delay_seconds)

    logger.info(
        f"MODE=PROD detected. Random send window enabled. "
        f"Selected send time: {scheduled_time.strftime('%H:%M:%S')} "
        f"(window: {config.send_window_start} - {config.send_window_end})"
    )

    formatted_time = format_seconds_to_mmss(random_delay_seconds)
    logger.info(f"Waiting {formatted_time} before sending...")
    time.sleep(random_delay_seconds)


def _ensure_data_directory() -> None:
    os.makedirs("data", exist_ok=True)


def _today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _already_sent_today(logger: SimpleLogger) -> bool:
    if not os.path.exists(LAST_SENT_FILE):
        logger.info("last_sent.txt not found. No send recorded for today yet.")
        return False

    try:
        with open(LAST_SENT_FILE, "r", encoding="utf-8") as file:
            last_sent_date = file.read().strip()

        if not last_sent_date:
            logger.warning("last_sent.txt is empty. No valid send record found for today.")
            return False

        if last_sent_date == _today_str():
            logger.warning(f"Message has already been sent today ({last_sent_date}). Skipping execution.")
            return True

        logger.info(f"Last recorded send date: {last_sent_date}. Sending is allowed today.")
        return False

    except Exception as exc:
        logger.warning(f"Could not read {LAST_SENT_FILE}: {exc}. Continuing execution for safety.")
        return False


def _mark_sent_today(logger: SimpleLogger) -> None:
    _ensure_data_directory()

    with open(LAST_SENT_FILE, "w", encoding="utf-8") as file:
        file.write(_today_str())

    logger.info(f"Updated {LAST_SENT_FILE} with today's date.")


def main() -> None:
    start_time = time.time()
    logger = SimpleLogger()

    try:
        config = load_config()
        logger.success("Configuration loaded and validated.")

        if _already_sent_today(logger):
            return

        _sleep_until_random_time_in_window(config, logger)

        message = generate_message(
            greetings_file=config.greetings_file,
            messages_file=config.messages_file,
        )
        logger.success("Message generated successfully.")

        total_attempts = config.max_retries + 1

        for attempt in range(1, total_attempts + 1):
            try:
                logger.info(f"Starting send attempt {attempt}/{total_attempts}...")

                send_whatsapp_message(
                    config=config,
                    message=message,
                    logger=logger,
                )

                _mark_sent_today(logger)
                logger.success("Flow completed successfully.")
                return

            except Exception as exc:
                logger.error(f"Attempt {attempt}/{total_attempts} failed: {exc}")

                error_message = str(exc)

                if "ChromeDriver only supports characters in the BMP" in error_message:
                    logger.error(
                        "Non-retryable ChromeDriver Unicode limitation detected. "
                        "Aborting without new attempts."
                    )
                    raise

                non_retryable_errors = (
                    FileNotFoundError,
                    NameError,
                    SyntaxError,
                    TypeError,
                )

                retryable_whatsapp_errors = (
                    WhatsAppSendError,
                    WhatsAppLoginError,
                    WhatsAppChatError,
                    WhatsAppMessageError,
                    WhatsAppDeliveryError,
                )

                if isinstance(exc, non_retryable_errors):
                    logger.error("Non-retryable application error detected. Aborting without new attempts.")
                    raise

                if isinstance(exc, retryable_whatsapp_errors):
                    if attempt < total_attempts:
                        logger.info(
                            f"Retryable WhatsApp/Selenium error detected. "
                            f"Retrying in {config.retry_delay_seconds} seconds..."
                        )
                        time.sleep(config.retry_delay_seconds)
                        continue

                    logger.error("Retry limit reached for WhatsApp/Selenium error.")
                    raise

                if attempt < total_attempts:
                    logger.info(
                        f"Unexpected runtime error detected. "
                        f"Retrying in {config.retry_delay_seconds} seconds..."
                    )
                    time.sleep(config.retry_delay_seconds)
                else:
                    raise

    except Exception as exc:
        logger.error(f"Fatal error: {exc}")
        raise

    finally:
        total_time = time.time() - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        logger.info(f"============================================================================")
        logger.info(f"====================== Total execution time: {minutes}m{seconds:02d}s =========================")
        logger.info(f"============================================================================")


if __name__ == "__main__":
    main()