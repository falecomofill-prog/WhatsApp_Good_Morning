from __future__ import annotations

import time

from modules.config_loader import load_config
from modules.logger import log_error, log_info, log_success
from modules.message_generator import generate_message
from modules.sender_twilio import send_whatsapp_twilio_message
from modules.sender_web import send_whatsapp_web_message


def main() -> None:
    start_time = time.time()

    try:
        config = load_config()
        log_success("Configuration loaded and validated.")

        message = generate_message(
            greetings_file=config.greetings_file,
            messages_file=config.messages_file,
        )
        log_success("Message generated successfully.")

        for attempt in range(1, config.max_retries + 2):
            try:
                log_info(f"Starting send attempt {attempt}.")

                if config.sender_mode == "selenium":
                    send_whatsapp_web_message(
                        phone=config.destination_phone,
                        message=message,
                        profile_path=config.chrome_profile_path,
                        base_url=config.whatsapp_web_url,
                        headless=config.headless,
                        login_timeout_seconds=config.login_timeout_seconds,
                        element_timeout_seconds=config.element_timeout_seconds,
                        min_open_delay_seconds=config.min_open_delay_seconds,
                        max_open_delay_seconds=config.max_open_delay_seconds,
                        min_pre_send_delay_seconds=config.min_pre_send_delay_seconds,
                        max_pre_send_delay_seconds=config.max_pre_send_delay_seconds,
                        min_post_send_delay_seconds=config.min_post_send_delay_seconds,
                        max_post_send_delay_seconds=config.max_post_send_delay_seconds,
                    )

                elif config.sender_mode == "twilio":
                    send_whatsapp_twilio_message(
                        sid=config.twilio_sid,
                        token=config.twilio_token,
                        from_number=config.twilio_whatsapp_number,
                        to_number=config.destination_phone,
                        body=message,
                    )

                log_success("Flow completed successfully.")
                return

            except Exception as exc:
                log_error(f"Attempt {attempt} failed: {exc}")

                if attempt <= config.max_retries:
                    log_info(f"Retrying in {config.retry_delay_seconds} seconds...")
                    time.sleep(config.retry_delay_seconds)
                else:
                    raise

    except Exception as exc:
        log_error(f"Fatal error: {exc}")
        raise

    finally:
        end_time = time.time()
        total_time = end_time - start_time
        minutes = int(total_time // 60)
        seconds = int(total_time % 60)
        log_info(f"============ Total execution time: {minutes}m{seconds:02d}s ===============")

        
if __name__ == "__main__":
    main()