from __future__ import annotations

import os
import time
import random
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


POST_SEND_TIMEOUT_SECONDS = 5


class WhatsAppSendError(Exception):
    """Generic send error for WhatsApp automation."""


class WhatsAppLoginError(WhatsAppSendError):
    """Raised when WhatsApp session is not authenticated or page is not ready."""


class WhatsAppChatError(WhatsAppSendError):
    """Raised when the target chat could not be opened."""


class WhatsAppMessageError(WhatsAppSendError):
    """Raised when the message box or send action fails."""


def send_whatsapp_message(config, message, logger) -> None:
    """
    Public entrypoint.

    Strategy:
    1. Try configured mode (headless or visible)
    2. If headless fails and fallback is enabled, retry once in visible mode
    """
    headless_requested = bool(getattr(config, "headless", False))
    fallback_enabled = bool(getattr(config, "enable_headless_fallback", True))

    if headless_requested:
        logger.info("HEADLESS mode enabled. Starting first attempt in headless mode.")
        try:
            _send_whatsapp_message(config, message, logger, headless=True)
            logger.success("Message sent successfully in headless mode.")
            return
        except Exception as exc:
            logger.warning(f"Headless attempt failed: {exc}")

            if fallback_enabled:
                logger.warning("Falling back automatically to visible browser mode...")
                _send_whatsapp_message(config, message, logger, headless=False)
                logger.success("Message sent successfully after fallback to visible mode.")
                return

            raise

    logger.info("Starting in visible browser mode.")
    _send_whatsapp_message(config, message, logger, headless=False)
    logger.success("Message sent successfully in visible mode.")


def _send_whatsapp_message(config, message, logger, headless: bool = False) -> None:
    driver = None

    try:
        driver = _build_driver(config, logger, headless=headless)

        critical_wait_seconds = int(getattr(config, "element_timeout", 60))
        critical_wait = WebDriverWait(driver, critical_wait_seconds)
        post_send_wait = WebDriverWait(driver, POST_SEND_TIMEOUT_SECONDS)

        phone_number = _normalize_phone_number(getattr(config, "my_whatsapp_number", ""))
        if not phone_number:
            raise WhatsAppChatError("Target WhatsApp number is empty or invalid.")

        if not message or not message.strip():
            raise WhatsAppMessageError("Message is empty after validation.")

        logger.info(f"Opening WhatsApp chat for target number: {phone_number}")

        _open_chat(driver, config, phone_number, message, logger)
        _apply_configured_delay(config, logger, "open")

        _wait_for_whatsapp_ready(driver, critical_wait, logger)
        message_box = _wait_for_message_box(driver, critical_wait, logger)

        _apply_configured_delay(config, logger, "pre_send")
        _type_message_if_needed(message_box, message, logger)

        _send_message(message_box, logger)

        _apply_configured_delay(config, logger, "post_send")
        _validate_post_send_state(driver, post_send_wait, logger)

    except Exception:
        if driver is not None:
            _save_failure_artifacts(driver, logger)
        raise
    finally:
        if driver is not None:
            logger.info("Closing browser driver...")
            driver.quit()


def _build_driver(config, logger, headless: bool = False):
    chrome_options = webdriver.ChromeOptions()

    user_data_dir = getattr(config, "chrome_profile_path", "").strip()
    if user_data_dir:
        user_data_dir = os.path.abspath(user_data_dir)
        os.makedirs(user_data_dir, exist_ok=True)
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
        logger.info(f"Using Chrome user data dir: {user_data_dir}")

    profile_directory = getattr(config, "chrome_profile_directory", "").strip()
    if profile_directory:
        chrome_options.add_argument(f"--profile-directory={profile_directory}")
        logger.info(f"Using Chrome profile directory: {profile_directory}")
    else:
        logger.info("No Chrome profile directory specified. Using root of user-data-dir.")

    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--no-default-browser-check")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--remote-debugging-port=0")

    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1600,1000")
        logger.info("Chrome configured for headless mode.")
    else:
        logger.info("Chrome configured for visible mode.")

    driver_path = getattr(config, "chromedriver_path", "").strip()
    if driver_path:
        logger.info("Using explicit ChromeDriver path from config.")
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        logger.info("Using system/default ChromeDriver resolution.")
        driver = webdriver.Chrome(options=chrome_options)

    page_load_timeout = int(getattr(config, "page_load_timeout", 60))
    script_timeout = int(getattr(config, "script_timeout", 60))

    driver.set_page_load_timeout(page_load_timeout)
    driver.set_script_timeout(script_timeout)

    logger.info(
        f"Browser started successfully | headless={headless} | "
        f"page_load_timeout={page_load_timeout}s | script_timeout={script_timeout}s"
    )

    return driver


def _normalize_phone_number(phone_number: str) -> str:
    return "".join(ch for ch in str(phone_number) if ch.isdigit())


def _open_chat(driver, config, phone_number: str, message: str, logger) -> None:
    base_url = getattr(config, "whatsapp_web_url", "https://web.whatsapp.com").rstrip("/")
    encoded_message = quote(message)
    url = f"{base_url}/send?phone={phone_number}&text={encoded_message}"

    logger.info("Navigating to WhatsApp Web send URL...")
    driver.get(url)


def _wait_for_whatsapp_ready(driver, wait, logger) -> None:
    logger.info("Waiting for WhatsApp Web to become ready...")

    ready_selectors = [
        (By.XPATH, '//div[@contenteditable="true"][@data-tab]'),
        (By.XPATH, '//footer//div[@contenteditable="true"]'),
        (By.XPATH, '//div[contains(@title, "Type a message")]'),
    ]

    last_exception = None

    for by, selector in ready_selectors:
        try:
            logger.info(f"Trying readiness selector: {selector}")
            wait.until(EC.presence_of_element_located((by, selector)))
            logger.info("WhatsApp Web appears ready.")
            return
        except TimeoutException as exc:
            last_exception = exc

    page_source = driver.page_source.lower()

    if "qr code" in page_source or "scan the qr code" in page_source:
        raise WhatsAppLoginError("WhatsApp login is required. QR code screen detected.")

    raise WhatsAppLoginError(
        f"WhatsApp Web did not become ready within the expected time. Last error: {last_exception}"
    )


def _wait_for_message_box(driver, wait, logger):
    logger.info("Waiting for message input box...")

    selectors = [
        (By.XPATH, '//footer//div[@contenteditable="true"][@data-tab]'),
        (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'),
        (By.XPATH, '//div[@contenteditable="true"][@role="textbox"]'),
    ]

    last_exception = None

    for by, selector in selectors:
        try:
            logger.info(f"Trying message box selector: {selector}")
            element = wait.until(EC.element_to_be_clickable((by, selector)))
            logger.info("Message input box found and clickable.")
            return element
        except TimeoutException as exc:
            last_exception = exc

    raise WhatsAppMessageError(
        f"Could not locate clickable message box. Last error: {last_exception}"
    )


def _type_message_if_needed(message_box, message: str, logger) -> None:
    logger.info("Preparing message in the input box...")

    message_box.click()
    time.sleep(0.3)

    existing_text = (message_box.text or "").strip()

    if existing_text:
        logger.info("Message box already contains prefilled text from URL. Skipping manual typing.")
        return

    logger.info("Prefilled text not detected. Typing message manually...")

    lines = message.splitlines()

    for idx, line in enumerate(lines):
        if line:
            message_box.send_keys(line)

        if idx < len(lines) - 1:
            message_box.send_keys(Keys.SHIFT, Keys.ENTER)

        time.sleep(random.uniform(0.05, 0.18))

    logger.info("Message typed successfully.")


def _send_message(message_box, logger) -> None:
    logger.info("Sending message...")
    message_box.send_keys(Keys.ENTER)
    logger.info("ENTER key sent.")


def _validate_post_send_state(driver, wait, logger) -> None:
    logger.info("Validating post-send UI state...")

    possible_success_selectors = [
        (By.XPATH, '//span[@data-icon="msg-time"]'),
        (By.XPATH, '//span[@data-icon="msg-check"]'),
        (By.XPATH, '//span[@data-icon="msg-dblcheck"]'),
        (By.XPATH, '//div[contains(@aria-label, "Message list")]'),
    ]

    for by, selector in possible_success_selectors:
        try:
            wait.until(EC.presence_of_element_located((by, selector)))
            logger.info(f"Post-send validation succeeded using selector: {selector}")
            return
        except TimeoutException:
            continue

    logger.warning(
        f"Post-send confirmation not detected within {POST_SEND_TIMEOUT_SECONDS}s. "
        "Continuing assuming success."
    )


def _apply_configured_delay(config, logger, stage: str) -> None:
    use_random_delay = bool(getattr(config, "use_random_delay", True))

    if not use_random_delay:
        logger.info(f"Random delay disabled for stage: {stage}")
        return

    stage_map = {
        "open": (
            int(getattr(config, "min_open_delay_seconds", 2)),
            int(getattr(config, "max_open_delay_seconds", 5)),
        ),
        "pre_send": (
            int(getattr(config, "min_pre_send_delay_seconds", 3)),
            int(getattr(config, "max_pre_send_delay_seconds", 7)),
        ),
        "post_send": (
            int(getattr(config, "min_post_send_delay_seconds", 2)),
            int(getattr(config, "max_post_send_delay_seconds", 4)),
        ),
    }

    if stage not in stage_map:
        raise ValueError(f"Unknown delay stage: {stage}")

    min_seconds, max_seconds = stage_map[stage]
    delay = random.uniform(min_seconds, max_seconds)

    logger.info(f"{stage}: sleeping for {delay:.2f}s")
    time.sleep(delay)


def _save_failure_artifacts(driver, logger) -> None:
    try:
        os.makedirs("logs", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        screenshot_path = os.path.join("logs", f"whatsapp_error_{timestamp}.png")
        html_path = os.path.join("logs", f"whatsapp_error_{timestamp}.html")

        driver.save_screenshot(screenshot_path)

        with open(html_path, "w", encoding="utf-8") as file:
            file.write(driver.page_source)

        logger.error(f"Failure artifacts saved: {screenshot_path} | {html_path}")
    except Exception as exc:
        logger.error(f"Could not save failure artifacts: {exc}")