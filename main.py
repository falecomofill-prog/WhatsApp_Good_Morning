# =========================
# IMPORTS
# =========================

from twilio.rest import Client
import random
import os
import sys
import json
from datetime import datetime
import pytz

from messages import greetings, messages

from config import (
    MODE,
    TWILIO_SID,
    TWILIO_TOKEN,
    FROM_NUMBER,
    TO_NUMBER
)

# =========================
# INITIALIZATION
# =========================

print(f"[INFO] Running in {MODE} mode")

client = Client(TWILIO_SID, TWILIO_TOKEN)


# =========================
# TIME CONFIGURATION
# =========================

# Time (Brazil)
tz = pytz.timezone("America/Sao_Paulo")

# Current datetime
now = datetime.now(tz)

# Format
current_time = now.strftime("%H:%M")
today_date = now.strftime("%Y-%m-%d")


# =========================
# EXECUTION WINDOW CONTROL
# =========================

# Define allowed execution window
start_window = datetime.strptime("07:30", "%H:%M").time()
end_window = datetime.strptime("08:30", "%H:%M").time()

# Only enforce in production mode
if MODE == "PROD":
    if not (start_window <= now.time() <= end_window):
        print(f"[INFO] Outside execution window. Now: {current_time}")
        sys.exit()


# =========================
# SCHEDULING CONFIGURATION
# =========================

# Possible execution times (randomized daily)
allowed_times = [
    "07:30", "07:40", "07:50",
    "08:00", "08:10", "08:20", "08:30"
]


# =========================
# DAILY SCHEDULING LOGIC
# =========================

schedule_file = "schedule.txt"

saved_date, scheduled_time = None, None

# Read existing schedule file
if os.path.exists(schedule_file):
    with open(schedule_file, "r") as file:
        content = file.read().strip()

        # Validate format (date|time)
        if "|" in content:
            saved_date, scheduled_time = content.split("|")
        else:
            print("[WARN] Invalid schedule format. Resetting...")

# Generate new schedule if: New day or corrupted/missing data
if saved_date != today_date or not scheduled_time:
    scheduled_time = random.choice(allowed_times)

    with open(schedule_file, "w") as file:
        file.write(f"{today_date}|{scheduled_time}")

    print(f"[INFO] New scheduled time for today: {scheduled_time}")


# =========================
# EXECUTION TOLERANCE
# =========================

# Convert scheduled time into datetime
scheduled_naive = datetime.strptime(scheduled_time, "%H:%M")

scheduled_datetime = tz.localize(
    scheduled_naive.replace(year=now.year, month=now.month, day=now.day)
)

# Calculate time difference in seconds
time_difference = abs((now - scheduled_datetime).total_seconds())

# Only enforce tolerance in production
if MODE == "PROD":
    if time_difference > 600:  # 10 minutes tolerance
        print(f"[INFO] Outside allowed window. Scheduled: {scheduled_time} | Now: {current_time}")
        sys.exit()


# =========================
# DUPLICATE CONTROL
# =========================

control_file = "last_sent.txt"

if os.path.exists(control_file):
    with open(control_file, "r") as file:
        last_sent_date = file.read().strip()

    # Prevent duplicate sends in production
    if last_sent_date == today_date and MODE == "PROD":
        print("[INFO] Message already sent today. Skipping execution.")
        sys.exit()

    elif last_sent_date == today_date:
        print("[INFO] TEST mode: ignoring duplicate check")


# =========================
# MESSAGE GENERATION
# =========================

# Select random greeting and message
greeting = random.choice(greetings)
message = random.choice(messages)

# Combine final message
final_message = f"{greeting}\n{message}"


# =========================
# SEND MESSAGE (TWILIO)
# =========================

client.messages.create(
    body=final_message,
    from_=FROM_NUMBER,
    to=TO_NUMBER
)

print("[INFO] Message sent successfully!")


# =========================
# STATE UPDATE
# =========================

# Save today's date to prevent duplicate sends
with open(control_file, "w") as file:
    file.write(today_date)

print("[INFO] State updated")


# =========================
# LOGGING SYSTEM (history.json)
# =========================

history_file = "history.json"

status = "sent"

# Create structured log entry
log_entry = {
    "date": today_date,
    "time": current_time,
    "scheduled_time": scheduled_time,
    "status": status,
    "message": final_message
}

# Load existing history safely
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        try:
            history = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load history: {e}")
            history = []
else:
    history = []

# Append new log entry
history.append(log_entry)

# Save updated history
with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

print("[INFO] Log updated")