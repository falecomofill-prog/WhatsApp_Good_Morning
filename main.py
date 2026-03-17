from twilio.rest import Client
import random
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from messages import greetings, messages

# =========================
# CONFIGURATION
# =========================

# Load environment variables from .env file
load_dotenv()

# Retrieve secure credentials from environment variables
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")

# Target phone number (WhatsApp format)
to_number = "whatsapp:+554198489999"

# Initialize Twilio client
client = Client(account_sid, auth_token)

# =========================
# WEEKDAY VALIDATION
# =========================

# Check if today is a weekday (0 = Monday, 6 = Sunday)
today = datetime.today().weekday()

if today >= 5:
    print("Weekend detected. Message will not be sent.")
    exit()

# =========================
# RANDOM DELAY (0–60 MINUTES)
# =========================

# Generate a random delay between 0 and 60 minutes
delay_minutes = random.randint(0, 60)
delay_seconds = delay_minutes * 60

print(f"Waiting {delay_minutes} minutes before sending the message...")
time.sleep(delay_seconds)

# =========================
# MESSAGE GENERATION
# =========================

# Select a random greeting and message
greeting = random.choice(greetings)
message = random.choice(messages)

# Combine greeting and message into a formatted message
final_message = f"{greeting}\n{message}"

# =========================
# SEND MESSAGE
# =========================

# Send WhatsApp message using Twilio API
client.messages.create(
    body=final_message,
    from_="whatsapp:+14155238886",  # Twilio sandbox number
    to=to_number
)

print("Message sent successfully!")