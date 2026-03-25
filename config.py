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

missing_vars = []

if not TWILIO_SID:
    missing_vars.append("TWILIO_SID")

if not TWILIO_TOKEN:
    missing_vars.append("TWILIO_TOKEN")

if not TWILIO_WHATSAPP_NUMBER:
    missing_vars.append("TWILIO_WHATSAPP_NUMBER")

if not MY_WHATSAPP_NUMBER:
    missing_vars.append("MY_WHATSAPP_NUMBER")

if missing_vars:
    raise ValueError(
        f"Missing environment variables: {', '.join(missing_vars)}"
    )

FROM_NUMBER = f"whatsapp:{TWILIO_WHATSAPP_NUMBER}"
TO_NUMBER = f"whatsapp:{MY_WHATSAPP_NUMBER}"