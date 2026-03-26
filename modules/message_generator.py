from __future__ import annotations

import random
from pathlib import Path


def _read_non_empty_lines(file_path: str) -> list[str]:
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Message file not found: {file_path}")

    lines = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    if not lines:
        raise ValueError(f"Message file is empty: {file_path}")

    return lines


def generate_message(greetings_file: str, messages_file: str) -> str:
    greetings = _read_non_empty_lines(greetings_file)
    messages = _read_non_empty_lines(messages_file)

    greeting = random.choice(greetings)
    message = random.choice(messages)

    return f"{greeting}\n{message}"