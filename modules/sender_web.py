from __future__ import annotations

import random
import time
from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from modules.logger import log_info, log_success


def _sleep_random(min_seconds: int, max_seconds: int, step_name: str) -> None:
    delay = random.uniform(min_seconds, max_seconds)
    log_info(f"{step_name}. Waiting {delay:.2f} seconds.")
    time.sleep(delay)


def _build_driver(profile_path: str, headless: bool) -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument(f"--user-data-dir={Path(profile_path).resolve()}")
    options.add_argument("--start-maximized")

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--window-size=1600,1000")

    return webdriver.Chrome(options=options)


def _wait_for_login(driver: webdriver.Chrome, timeout: int) -> None:
    wait = WebDriverWait(driver, timeout)
    wait.until(
        EC.presence_of_element_located((By.XPATH, '//div[@id="pane-side" or @id="main"]'))
    )


def _open_chat(driver: webdriver.Chrome, phone: str, message: str, base_url: str) -> None:
    encoded_message = quote(message)
    url = f"{base_url}send?phone={phone}&text={encoded_message}"
    driver.get(url)


def _send_message(driver: webdriver.Chrome, timeout: int) -> None:
    wait = WebDriverWait(driver, timeout)

    message_box = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, '//div[@contenteditable="true"][@data-tab="10" or @data-tab="6"]')
        )
    )
    message_box.send_keys(Keys.ENTER)


def send_whatsapp_web_message(
    *,
    phone: str,
    message: str,
    profile_path: str,
    base_url: str,
    headless: bool,
    login_timeout_seconds: int,
    element_timeout_seconds: int,
    min_open_delay_seconds: int,
    max_open_delay_seconds: int,
    min_pre_send_delay_seconds: int,
    max_pre_send_delay_seconds: int,
    min_post_send_delay_seconds: int,
    max_post_send_delay_seconds: int,
) -> None:
    log_info("Opening Chrome.")
    driver = _build_driver(profile_path, headless)

    try:
        log_info("Opening WhatsApp Web.")
        driver.get(base_url)

        log_info("Checking session/login state.")
        _wait_for_login(driver, login_timeout_seconds)
        log_success("WhatsApp Web is ready.")

        _sleep_random(min_open_delay_seconds, max_open_delay_seconds, "Open delay")

        log_info("Opening destination chat.")
        _open_chat(driver, phone, message, base_url)

        _sleep_random(
            min_pre_send_delay_seconds,
            max_pre_send_delay_seconds,
            "Pre-send delay",
        )

        log_info("Sending message.")
        _send_message(driver, element_timeout_seconds)
        log_success("Message sent successfully.")

        _sleep_random(
            min_post_send_delay_seconds,
            max_post_send_delay_seconds,
            "Post-send delay",
        )

    finally:
        log_info("Closing browser.")
        driver.quit()