# =========================
# CONFIGURATION MODULE
# =========================

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =========================
# EXECUTION MODE
# =========================

# Define execution mode (TEST or PROD)
MODE = os.getenv("MODE", "PROD")


# =========================
# TWILIO CREDENTIALS
# =========================

# Load Twilio API credentials from environment variables
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")

# Validate credentials to prevent runtime errors
if not TWILIO_SID or not TWILIO_TOKEN:
    raise ValueError("Twilio credentials not found in environment variables.")


# =========================
# WHATSAPP CONFIGURATION
# =========================

# Load WhatsApp phone numbers from environment variables
# TWILIO_WHATSAPP_NUMBER: sender (Twilio sandbox/number)
# MY_WHATSAPP_NUMBER: recipient (your personal number)
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

# Validate numbers
if not TWILIO_WHATSAPP_NUMBER or not MY_WHATSAPP_NUMBER:
    raise ValueError("WhatsApp numbers not found in environment variables.")


# =========================
# FORMATTED VALUES
# =========================

# Format numbers according to Twilio WhatsApp API requirements
# (must include 'whatsapp:' prefix)
FROM_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
TO_NUMBER = f"whatsapp:{MY_WHATSAPP_NUMBER}"