import os

from dotenv import load_dotenv


load_dotenv()

MODE = os.getenv("MODE", "PROD").upper()

if MODE not in {"TEST", "PROD"}:
    raise ValueError("MODE must be either 'TEST' or 'PROD'.")

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_TOKEN = os.getenv("TWILIO_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_WHATSAPP_NUMBER = os.getenv("MY_WHATSAPP_NUMBER")

if not TWILIO_SID or not TWILIO_TOKEN:
    raise ValueError("Twilio credentials not found in environment variables.")

if not TWILIO_WHATSAPP_NUMBER or not MY_WHATSAPP_NUMBER:
    raise ValueError("WhatsApp numbers not found in environment variables.")

FROM_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
TO_NUMBER = f"whatsapp:{MY_WHATSAPP_NUMBER}"