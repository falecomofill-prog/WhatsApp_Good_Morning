from twilio.rest import Client
import random
import os
from dotenv import load_dotenv
from messages import saudacoes, mensagens

# =========================
# CONFIG
# =========================

# Load .env
load_dotenv()

# Retrieve safe variables from .env
account_sid = os.getenv("TWILIO_SID")
auth_token = os.getenv("TWILIO_TOKEN")

# Your phone number 
numero = "whatsapp:+554198489999"

client = Client(account_sid, auth_token)

# =========================
# LISTS
# =========================



# =========================
# GERAR MENSAGEM
# =========================

saudacao = random.choice(saudacoes)
mensagem_random = random.choice(mensagens)

mensagem = f"{saudacao}\n{mensagem_random}"

print("Mensagem gerada:\n")
print(mensagem)

# =========================
# ENVIO
# =========================

message = client.messages.create(
    body=mensagem,
    from_="whatsapp:+14155238886",
    to=numero
)

print("\nMensagem enviada com sucesso!")
