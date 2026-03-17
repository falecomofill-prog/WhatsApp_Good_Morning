from twilio.rest import Client
import random
import os
import sys
from datetime import datetime
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
# WEEKDAY VALIDATION
# =========================

# Check if today is a weekday (0 = Monday, 6 = Sunday)
today_weekday = datetime.today().weekday()

if today_weekday >= 5:
    print("Weekend detected. Message will not be sent.")
    sys.exit()

# =========================
# DAILY EXECUTION CONTROL
# =========================

# File used to track the last date a message was sent
control_file = "last_sent.txt"

# Get today's date in YYYY-MM-DD format
today_date = datetime.today().strftime("%Y-%m-%d")

# Check if the control file exists
if os.path.exists(control_file):
    with open(control_file, "r") as file:
        last_sent_date = file.read().strip()

    # If message was already sent today, skip execution
    if last_sent_date == today_date:
        print("Message already sent today. Skipping execution.")
        sys.exit()

# =========================
# MESSAGE GENERATION
# =========================

# Select a random greeting and message from predefined lists
greeting = random.choice(greetings)
message = random.choice(messages)

# Combine greeting and message into a formatted message
final_message = f"{greeting}\n\n{message}"

# =========================
# SEND MESSAGE
# =========================

# Send WhatsApp message using Twilio API
client.messages.create(
    body=final_message,
    from_="whatsapp:+14155238886",  # Twilio sandbox number
    to=to_number
)

# Log success message
print(f"Message sent successfully to {to_number}")

# =========================
# UPDATE CONTROL FILE
# =========================

# Save today's date to prevent multiple sends in the same day
with open(control_file, "w") as file:
    file.write(today_date)

print("Control file updated successfully.")