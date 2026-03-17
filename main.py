from twilio.rest import Client
import random
import os
import sys
from datetime import datetime
import pytz
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

# Allowed execution times
allowed_times = ["07:51", "08:02", "08:13", "08:24", "08:35", "08:46", "08:57", "09:08"]

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
# EXECUTION DECISION (WITH TOLERANCE)
# =========================

scheduled_datetime = datetime.strptime(scheduled_time, "%H:%M").replace(
    year=now.year, month=now.month, day=now.day, tzinfo=tz
)

time_difference = abs((now - scheduled_datetime).total_seconds())

if time_difference > 120:
    print(f"Outside allowed window. Scheduled: {scheduled_time} | Now: {current_time}")
    sys.exit()

# =========================
# DAILY SEND CONTROL
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