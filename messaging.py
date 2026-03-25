import random
from pathlib import Path

from twilio.rest import Client

from config import TWILIO_SID, TWILIO_TOKEN, FROM_NUMBER, TO_NUMBER


CONFIG_DIR = Path("config")
GREETINGS_FILE = CONFIG_DIR / "greetings.txt"
MESSAGES_FILE = CONFIG_DIR / "messages.txt"


def load_lines(file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    lines = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError(f"File is empty: {file_path}")

    return lines


def build_message() -> str:
    greetings = load_lines(GREETINGS_FILE)
    messages = load_lines(MESSAGES_FILE)

    greeting = random.choice(greetings)
    message = random.choice(messages)

    return f"{greeting}\n{message}"


def send_whatsapp_message(body: str) -> None:
    client = Client(TWILIO_SID, TWILIO_TOKEN)

    client.messages.create(
        body=body,
        from_=FROM_NUMBER,
        to=TO_NUMBER,
    )