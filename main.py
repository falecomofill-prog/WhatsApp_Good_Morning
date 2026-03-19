from twilio.rest import Client
import random
import os
import sys
from datetime import datetime
import pytz
import json
from dotenv import load_dotenv
from messages import greetings, messages

# =========================
# CONFIGURATION
# =========================

# Load environment variables from .env file
load_dotenv()

# Retrieve Twilio credentials from environment variables
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")

# Validate credentials
if not account_sid or not auth_token:
    raise ValueError("Twilio credentials not found. Check environment variables.")

# Target phone number (WhatsApp format)
to_number = "whatsapp:+554198489999"

# Initialize Twilio client
client = Client(account_sid, auth_token)

# =========================
# TIME CONFIGURATION
# =========================

# Define Brazil timezone
tz = pytz.timezone("America/Sao_Paulo")

# Get current date and time in Brazil timezone
now = datetime.now(tz)
current_time = now.strftime("%H:%M")
today_date = now.strftime("%Y-%m-%d")

# =========================
# EXECUTION WINDOW (07:30 → 08:30)
# =========================

start_window = datetime.strptime("07:30", "%H:%M").time()
end_window = datetime.strptime("08:30", "%H:%M").time()

#if not (start_window <= now.time() <= end_window):
#    print(f"Outside execution window. Now: {current_time}")
#    sys.exit()

# =========================
# ALLOWED TIMES (SCHEDULER)
# =========================

allowed_times = [
    "07:30", "07:40", "07:50",
    "08:00", "08:10", "08:20", "08:30"
]

# =========================
# DAILY SCHEDULING LOGIC
# =========================

schedule_file = "schedule.txt"

saved_date, scheduled_time = None, None

if os.path.exists(schedule_file):
    with open(schedule_file, "r") as file:
        content = file.read().strip()

        if "|" in content:
            saved_date, scheduled_time = content.split("|")
        else:
            print("Invalid schedule file format. Resetting...")

# Generate new schedule if needed
if saved_date != today_date or not scheduled_time:
    scheduled_time = random.choice(allowed_times)

    with open(schedule_file, "w") as file:
        file.write(f"{today_date}|{scheduled_time}")

    print(f"New scheduled time for today: {scheduled_time}")

# =========================
# EXECUTION DECISION (TOLERANCE)
# =========================

scheduled_naive = datetime.strptime(scheduled_time, "%H:%M")
scheduled_datetime = tz.localize(
    scheduled_naive.replace(year=now.year, month=now.month, day=now.day)
)

time_difference = abs((now - scheduled_datetime).total_seconds())

if time_difference > 600:  # 10 minutos
    print(f"Outside allowed window. Scheduled: {scheduled_time} | Now: {current_time}")
    sys.exit()

# =========================
# DUPLICATE CONTROL
# =========================

control_file = "last_sent.txt"

if os.path.exists(control_file):
    with open(control_file, "r") as file:
        last_sent_date = file.read().strip()

    if last_sent_date == today_date:
        print("Message already sent today. Skipping execution.")
        sys.exit()

# =========================
# MESSAGE GENERATION
# =========================

greeting = random.choice(greetings)
message = random.choice(messages)

final_message = f"{greeting}\n{message}"

# =========================
# SEND MESSAGE
# =========================

client.messages.create(
    body=final_message,
    from_="whatsapp:+14155238886",
    to=to_number
)

print("Message sent successfully!")

# =========================
# STATE UPDATE
# =========================

with open(control_file, "w") as file:
    file.write(today_date)

print("Execution state updated successfully.")

# =========================
# LOGGING (history.json)
# =========================

history_file = "history.json"

log_entry = {
    "date": today_date,
    "time": current_time,
    "scheduled_time": scheduled_time,
    "status": "sent",
    "message": final_message
}

if os.path.exists(history_file):
    with open(history_file, "r") as f:
        try:
            history = json.load(f)
        except:
            history = []
else:
    history = []

history.append(log_entry)

with open(history_file, "w") as f:
    json.dump(history, f, indent=2)

print("Log updated successfully.")