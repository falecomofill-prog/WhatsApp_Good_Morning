from __future__ import annotations

import os
import random
import time
from datetime import datetime
from urllib.parse import quote

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


POST_SEND_TIMEOUT_SECONDS = 30
SESSION_STABILIZATION_SECONDS = 3
RETRY_MODAL_TIMEOUT_SECONDS = 8


class WhatsAppSendError(Exception):
    """Base exception for WhatsApp Web sending failures."""


class WhatsAppLoginError(WhatsAppSendError):
    """Raised when WhatsApp Web is not authenticated or ready."""


class WhatsAppChatError(WhatsAppSendError):
    """Raised when the target chat cannot be opened or validated."""


class WhatsAppMessageError(WhatsAppSendError):
    """Raised when the message cannot be typed or sent."""


class WhatsAppDeliveryError(WhatsAppSendError):
    """Raised when the UI shows a failed delivery state."""


def _remove_non_bmp_characters(text: str) -> str:
    """
    Remove Unicode characters outside the Basic Multilingual Plane (BMP).

    ChromeDriver send_keys may fail with characters above U+FFFF,
    which commonly includes some emojis and rare symbols.
    """
    return "".join(char for char in text if ord(char) <= 0xFFFF)


def send_whatsapp_message(config, message: str, logger) -> None:
    """
    Send a WhatsApp message using Selenium.

    Strategy:
    1. Try the configured mode (headless or visible)
    2. If headless fails and fallback is enabled, retry in visible mode
    """
    headless_requested = bool(getattr(config, "headless", False))
    fallback_enabled = bool(getattr(config, "enable_headless_fallback", True))

    if headless_requested:
        logger.info("HEADLESS mode requested. Starting first attempt in headless mode.")
        try:
            _send_whatsapp_message(config=config, message=message, logger=logger, headless=True)
            logger.success("Message sent successfully in headless mode.")
            return
        except Exception as exc:
            logger.warning(f"Headless attempt failed: {exc}")

            if fallback_enabled:
                logger.warning("Falling back automatically to visible browser mode.")
                _send_whatsapp_message(config=config, message=message, logger=logger, headless=False)
                logger.success("Message sent successfully after fallback to visible mode.")
                return

            raise

    logger.info("Starting in visible browser mode.")
    _send_whatsapp_message(config=config, message=message, logger=logger, headless=False)
    logger.success("Message sent successfully in visible mode.")


def _send_whatsapp_message(config, message: str, logger, headless: bool = False) -> None:
    """
    Internal send flow with full browser lifecycle handling.
    """
    driver = None

    try:
        _validate_input(config=config, message=message)

        driver = _build_driver(config=config, logger=logger, headless=headless)
        wait = WebDriverWait(driver, int(getattr(config, "element_timeout", 60)))

        phone_number = _normalize_phone_number(getattr(config, "my_whatsapp_number", ""))
        logger.info(f"Opening chat for target number: {phone_number}")

        _open_chat(driver=driver, config=config, phone_number=phone_number, logger=logger)
        _stabilize_session(driver=driver, wait=wait, logger=logger)
        _apply_configured_delay(config=config, logger=logger, stage="open")

        before_count = _count_outgoing_messages(driver=driver)
        logger.info(f"Outgoing message count before send: {before_count}")

        message_box = _wait_for_message_box(driver=driver, wait=wait, logger=logger)
        _apply_configured_delay(config=config, logger=logger, stage="pre_send")

        _clear_message_box(message_box=message_box, logger=logger)
        _type_message(message_box=message_box, message=message, logger=logger)
        _send_message(message_box=message_box, logger=logger)

        _apply_configured_delay(config=config, logger=logger, stage="post_send")
        _validate_delivery(
            driver=driver,
            logger=logger,
            previous_outgoing_count=before_count,
        )

    except Exception as exc:
        if driver is not None:
            _save_failure_artifacts(driver=driver, logger=logger)
        raise exc

    finally:
        keep_browser_open = bool(getattr(config, "keep_browser_open", False))

        if driver is not None:
            if keep_browser_open:
                logger.info("KEEP_BROWSER_OPEN enabled. Waiting for manual close.")
                input("Press ENTER to close the browser...")
            logger.info("Closing browser driver.")
            driver.quit()


def _validate_input(config, message: str) -> None:
    """
    Validate critical runtime inputs before starting Selenium.
    """
    phone_number = _normalize_phone_number(getattr(config, "my_whatsapp_number", ""))
    if not phone_number:
        raise WhatsAppChatError("Target WhatsApp number is empty or invalid.")

    if not message or not message.strip():
        raise WhatsAppMessageError("Message is empty after validation.")


def _build_driver(config, logger, headless: bool = False):
    """
    Build and configure Chrome WebDriver.
    """
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
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("Using explicit ChromeDriver path from config.")
    else:
        driver = webdriver.Chrome(options=chrome_options)
        logger.info("Using Selenium Manager / system ChromeDriver resolution.")

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
    """
    Keep digits only in the phone number.
    """
    return "".join(ch for ch in str(phone_number) if ch.isdigit())


def _open_chat(driver, config, phone_number: str, logger) -> None:
    """
    Open the target chat using phone number only.

    We avoid pre-filling the message in the URL because it can create
    ambiguous UI states after long idle sessions.
    """
    base_url = getattr(config, "whatsapp_web_url", "https://web.whatsapp.com").rstrip("/")
    url = f"{base_url}/send?phone={quote(phone_number)}"

    logger.info("Navigating to WhatsApp Web chat URL.")
    driver.get(url)


def _stabilize_session(driver, wait, logger) -> None:
    """
    Make sure the WhatsApp Web session is truly ready.

    This method waits for the page to settle, validates that login is not required,
    and performs one refresh if the first readiness pass looks stale.
    """
    logger.info("Stabilizing WhatsApp Web session.")
    time.sleep(SESSION_STABILIZATION_SECONDS)

    try:
        _wait_for_whatsapp_ready(driver=driver, wait=wait, logger=logger)
        logger.info("Initial readiness check passed.")
    except WhatsAppLoginError:
        raise
    except Exception as exc:
        logger.warning(f"Initial readiness check failed: {exc}. Refreshing once.")
        driver.refresh()
        time.sleep(SESSION_STABILIZATION_SECONDS)
        _wait_for_whatsapp_ready(driver=driver, wait=wait, logger=logger)
        logger.info("Session recovered after refresh.")


def _wait_for_whatsapp_ready(driver, wait, logger) -> None:
    """
    Wait until WhatsApp Web is authenticated and the chat UI is usable.
    """
    logger.info("Waiting for WhatsApp Web to become ready.")

    readiness_selectors = [
        (By.XPATH, '//footer//div[@contenteditable="true"]'),
        (By.XPATH, '//div[@contenteditable="true"][@role="textbox"]'),
        (By.XPATH, '//header'),
    ]

    last_exception = None

    for by, selector in readiness_selectors:
        try:
            wait.until(EC.presence_of_element_located((by, selector)))
            logger.info(f"Readiness selector matched: {selector}")
            break
        except TimeoutException as exc:
            last_exception = exc
    else:
        page_source = driver.page_source.lower()

        login_indicators = [
            "qr code",
            "scan the qr code",
            "use whatsapp on your computer",
            "mantenha seu celular conectado",
            "use o whatsapp no computador",
        ]
        if any(indicator in page_source for indicator in login_indicators):
            raise WhatsAppLoginError("WhatsApp login is required. QR/login screen detected.")

        raise WhatsAppLoginError(
            f"WhatsApp Web did not become ready within the expected time. Last error: {last_exception}"
        )

    time.sleep(1.5)


def _wait_for_message_box(driver, wait, logger):
    """
    Wait until the message input box is clickable.
    """
    logger.info("Waiting for message input box.")

    selectors = [
        (By.XPATH, '//footer//div[@contenteditable="true"][@role="textbox"]'),
        (By.XPATH, '//footer//div[@contenteditable="true"][@data-tab]'),
        (By.XPATH, '//div[@contenteditable="true"][@role="textbox"]'),
    ]

    last_exception = None

    for by, selector in selectors:
        try:
            element = wait.until(EC.element_to_be_clickable((by, selector)))
            logger.info(f"Message box found using selector: {selector}")
            return element
        except TimeoutException as exc:
            last_exception = exc

    raise WhatsAppMessageError(
        f"Could not locate a clickable message box. Last error: {last_exception}"
    )


def _clear_message_box(message_box, logger) -> None:
    """
    Clear any leftover text before typing the current message.
    """
    logger.info("Clearing message box before typing.")
    message_box.click()
    time.sleep(0.2)
    message_box.send_keys(Keys.CONTROL, "a")
    time.sleep(0.1)
    message_box.send_keys(Keys.BACKSPACE)
    time.sleep(0.2)


def _remove_non_bmp_characters(text: str) -> str:
    """
    Remove Unicode characters outside the Basic Multilingual Plane (BMP).

    ChromeDriver send_keys may fail with characters above U+FFFF,
    which commonly includes some emojis and rare symbols.
    """
    return "".join(char for char in text if ord(char) <= 0xFFFF)


def _type_message(message_box, message: str, logger) -> None:
    """
    Type the message manually line by line.

    Non-BMP Unicode characters are removed before typing because
    ChromeDriver send_keys does not support them reliably.
    """
    logger.info("Typing message manually.")

    sanitized_message = _remove_non_bmp_characters(message)

    if sanitized_message != message:
        logger.warning(
            "Message contained non-BMP Unicode characters. "
            "Unsupported characters were removed before typing."
        )

    lines = sanitized_message.splitlines()

    for index, line in enumerate(lines):
        if line:
            message_box.send_keys(line)

        if index < len(lines) - 1:
            message_box.send_keys(Keys.SHIFT, Keys.ENTER)

        time.sleep(random.uniform(0.05, 0.18))

    logger.info("Message typed successfully.")


def _send_message(message_box, logger) -> None:
    """
    Trigger message send using ENTER.
    """
    logger.info("Sending message with ENTER.")
    message_box.send_keys(Keys.ENTER)


def _count_outgoing_messages(driver) -> int:
    """
    Count outgoing messages currently visible in the chat.
    """
    return len(driver.find_elements(By.XPATH, '//div[contains(@class, "message-out")]'))


def _get_last_outgoing_message(driver):
    """
    Return the last outgoing message bubble element.
    """
    messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-out")]')
    if not messages:
        raise WhatsAppDeliveryError("No outgoing message bubble was found after sending.")
    return messages[-1]


def _validate_delivery(driver, logger, previous_outgoing_count: int) -> None:
    """
    Validate that the send action produced a new outgoing message and that
    the UI does not show an explicit failed-delivery state.

    Strategy:
    - If a failed icon appears, try automatic retry
    - If a new outgoing bubble appears, accept it as success
    - If a send-status icon appears anywhere in the recent outgoing area, accept it
    """
    logger.info("Validating delivery state of the last outgoing message.")

    deadline = time.time() + POST_SEND_TIMEOUT_SECONDS

    while time.time() < deadline:
        current_count = _count_outgoing_messages(driver)

        if current_count > previous_outgoing_count:
            logger.info(
                f"Detected new outgoing message bubble "
                f"(before={previous_outgoing_count}, now={current_count})."
            )

            last_message = _get_last_outgoing_message(driver)

            if _last_message_has_failed_icon(last_message):
                logger.warning("Detected failed delivery icon on last outgoing message.")

                if _try_retry_failed_message(driver=driver, logger=logger):
                    logger.info("Retry action executed. Waiting for updated status...")
                    time.sleep(3)
                    last_message = _get_last_outgoing_message(driver)

                    if _last_message_has_failed_icon(last_message):
                        raise WhatsAppDeliveryError(
                            "Message still shows failed delivery state after retry."
                        )

                    if _last_message_has_send_status(last_message):
                        logger.info("Valid send status detected after retry.")
                        return

                else:
                    raise WhatsAppDeliveryError(
                        "Message shows failed delivery state and retry could not be triggered."
                    )

            if _last_message_has_send_status(last_message):
                logger.info("Valid send status detected on the last outgoing message.")
                return

            logger.warning(
                "New outgoing message detected, but no explicit send-status icon was found. "
                "Accepting as soft success."
            )
            return

        failure_buttons = driver.find_elements(
            By.XPATH,
            '//*[contains(@aria-label, "não foi enviada") or contains(@aria-label, "Message not sent")]'
        )
        if failure_buttons:
            logger.warning("A failed-delivery indicator was found globally in the page.")
            if _try_retry_failed_message(driver=driver, logger=logger):
                time.sleep(3)
                return
            raise WhatsAppDeliveryError("Failed-delivery indicator detected in the page.")

        global_success_icons = driver.find_elements(
            By.XPATH,
            '//span[@data-icon="msg-time"] | //span[@data-icon="msg-check"] | //span[@data-icon="msg-dblcheck"]'
        )
        if global_success_icons:
            logger.info("Detected WhatsApp send-status icon in page. Accepting as success.")
            return

        time.sleep(1)

    raise WhatsAppDeliveryError(
        "Timed out waiting for a reliable send confirmation on the page."
    )


def _last_message_has_send_status(message_element) -> bool:
    """
    Check whether the last outgoing message contains a valid send-state icon.
    """
    success_selectors = [
        './/span[@data-icon="msg-time"]',
        './/span[@data-icon="msg-check"]',
        './/span[@data-icon="msg-dblcheck"]',
    ]

    for selector in success_selectors:
        try:
            message_element.find_element(By.XPATH, selector)
            return True
        except NoSuchElementException:
            continue

    return False


def _last_message_has_failed_icon(message_element) -> bool:
    """
    Check whether the last outgoing message contains a visible failed-delivery icon.
    """
    failure_selectors = [
        './/span[@data-icon="alert-error"]',
        './/span[@data-icon="msg-error"]',
        './/*[@role="button" and (@aria-label="Não foi enviada" or @aria-label="Message not sent")]',
        './/*[contains(@aria-label, "não foi enviada")]',
        './/*[contains(@aria-label, "Message not sent")]',
    ]

    for selector in failure_selectors:
        try:
            message_element.find_element(By.XPATH, selector)
            return True
        except NoSuchElementException:
            continue

    return False


def _try_retry_failed_message(driver, logger) -> bool:
    """
    Try to click the failed message icon and then click the retry button in the modal.

    Supports both Portuguese and English labels when possible.
    """
    logger.info("Attempting automatic retry for failed message.")

    clickable_failure_selectors = [
        (By.XPATH, '(//div[contains(@class, "message-out")]//*[contains(@aria-label, "não foi enviada")])[last()]'),
        (By.XPATH, '(//div[contains(@class, "message-out")]//*[contains(@aria-label, "Message not sent")])[last()]'),
        (By.XPATH, '(//div[contains(@class, "message-out")]//*[@role="button"])[last()]'),
    ]

    for by, selector in clickable_failure_selectors:
        try:
            failed_icon = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((by, selector))
            )
            failed_icon.click()
            logger.info(f"Clicked failed message icon using selector: {selector}")
            break
        except Exception:
            continue
    else:
        logger.warning("Could not click the failed message icon.")
        return False

    retry_button_selectors = [
        (By.XPATH, '//div[@role="button"][.//div[text()="Tentar novamente"]]'),
        (By.XPATH, '//div[@role="button"][.//div[text()="Try again"]]'),
        (By.XPATH, '//button[normalize-space()="Tentar novamente"]'),
        (By.XPATH, '//button[normalize-space()="Try again"]'),
    ]

    for by, selector in retry_button_selectors:
        try:
            retry_button = WebDriverWait(driver, RETRY_MODAL_TIMEOUT_SECONDS).until(
                EC.element_to_be_clickable((by, selector))
            )
            retry_button.click()
            logger.info(f"Clicked retry button using selector: {selector}")
            return True
        except Exception:
            continue

    logger.warning("Retry modal appeared, but no retry button could be clicked.")
    return False


def _apply_configured_delay(config, logger, stage: str) -> None:
    """
    Apply optional randomized delays to mimic human interaction.
    """
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
    """
    Save screenshot and page source to help diagnose failures.
    """
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