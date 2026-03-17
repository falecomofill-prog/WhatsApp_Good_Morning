from twilio.rest import Client
import random
import os
import time
from dotenv import load_dotenv
from messages import greetings, messages

# =========================
# CONFIGURATION
# =========================

# Load environment variables from .env file
load_dotenv()

# Retrieve secure credentials
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")

# Target phone number (WhatsApp format)
to_number = "whatsapp:+554198489999"

# Initialize Twilio client
client = Client(account_sid, auth_token)

# =========================
# MESSAGE GENERATION
# =========================

# Select random greeting and message
greeting = random.choice(greetings)
message = random.choice(messages)

# Combine final message
final_message = f"{greeting} {message}"

# =========================
# RANDOM DELAY
# =========================

# Wait between 0 and 60 minutes (in seconds)
delay = random.randint(5, 10)
print(f"Waiting {delay} seconds before sending...")
time.sleep(delay)

# =========================
# SEND MESSAGE
# =========================

# Send WhatsApp message via Twilio
client.messages.create(
    body=final_message,
    from_="whatsapp:+14155238886",  # Twilio sandbox number
    to=to_number
)

print("Message sent successfully!")