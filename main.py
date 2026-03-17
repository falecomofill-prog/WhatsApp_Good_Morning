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

# Allowed execution times (must match GitHub Actions schedule)
allowed_times = ["07:51", "08:02", "08:13", "08:24", "08:35", "08:46", "08:57", "09:08"]

# =========================
# DAILY SCHEDULING LOGIC
# =========================

# File used to store the randomly selected time for the day
schedule_file = "schedule.txt"

# Read existing schedule if file exists
if os.path.exists(schedule_file):
    with open(schedule_file, "r") as file:
        saved_date, scheduled_time = file.read().strip().split("|")
else:
    saved_date, scheduled_time = None, None

# If it's a new day, generate and persist a new random time
if saved_date != today_date:
    scheduled_time = random.choice(allowed_times)

    with open(schedule_file, "w") as file:
        file.write(f"{today_date}|{scheduled_time}")

    print(f"New scheduled time for today: {scheduled_time}")

# =========================
# EXECUTION DECISION (WITH TOLERANCE)
# =========================

# Convert scheduled time to datetime
scheduled_datetime = datetime.strptime(scheduled_time, "%H:%M").replace(
    year=now.year, month=now.month, day=now.day, tzinfo=tz
)

# Calculate time difference in seconds
time_difference = abs((now - scheduled_datetime).total_seconds())

# Allow execution within a 2-minute window (120 seconds)
if time_difference > 120:
    print(f"Outside allowed time window. Scheduled: {scheduled_time} | Current: {current_time}")
    sys.exit()

# =========================
# DAILY SEND CONTROL
# =========================

# File used to ensure only one message is sent per day
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

# Select random greeting and message
greeting = random.choice(greetings)
message = random.choice(messages)

# Format final message with spacing
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

# Record today's date to prevent duplicate sends
with open(control_file, "w") as file:
    file.write(today_date)

print("Execution state updated successfully.")