from __future__ import annotations

from datetime import datetime
from pathlib import Path


LOG_DIR = Path("logs")
EXECUTION_LOG = LOG_DIR / "execution.log"
ERROR_LOG = LOG_DIR / "error.log"


def _ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write_line(file_path: Path, level: str, message: str) -> None:
    _ensure_log_dir()
    with file_path.open("a", encoding="utf-8") as f:
        f.write(f"[{_timestamp()}] [{level}] {message}\n")


def log_info(message: str) -> None:
    line = f"[INFO] {message}"
    print(line)
    _write_line(EXECUTION_LOG, "INFO", message)


def log_success(message: str) -> None:
    line = f"[SUCCESS] {message}"
    print(line)
    _write_line(EXECUTION_LOG, "SUCCESS", message)


def log_warning(message: str) -> None:
    line = f"[WARNING] {message}"
    print(line)
    _write_line(EXECUTION_LOG, "WARNING", message)


def log_error(message: str) -> None:
    line = f"[ERROR] {message}"
    print(line)
    _write_line(ERROR_LOG, "ERROR", message)
    _write_line(EXECUTION_LOG, "ERROR", message)