# 🚀 WhatsApp Automated Messaging System

A cloud-based automation system that sends **randomized WhatsApp messages** using the Twilio API.

> ⚙️ Designed for **reliability**, **clean architecture**, and **easy customization**  
> ☁️ Runs automatically via **GitHub Actions**

---

# ✨ Features

- 📲 Automated WhatsApp message delivery via Twilio API
- ☁️ Cloud execution with GitHub Actions
- 🎲 Daily randomized schedule selection
- 📅 Weekday-only execution
- ⏱️ Time window validation with tolerance
- 🚫 Duplicate message prevention
- 🗂️ Persistent execution state
- 📊 Structured logging system
- 🔁 Environment modes (`TEST` / `PROD`)
- 📝 Editable message templates (`.txt`)
- 🧱 Modular and scalable architecture

---

# 📁 Project Structure

WhatsApp_Good_Morning/  
├── .github/  
│   └── workflows/  
│       └── send_message.yml  
├── config/  
│   ├── greetings.txt  
│   └── messages.txt  
├── data/  
│   ├── history.json  
│   ├── last_sent.txt  
│   └── schedule.txt  
├── config.py  
├── logger.py  
├── main.py  
├── messaging.py  
├── scheduler.py  
├── storage.py  
├── requirements.txt  
├── README.md  
└── .gitignore

---

# 🧠 Architecture

|Module|Responsibility|
|---|---|
|`main.py`|Application orchestration|
|`scheduler.py`|Schedule generation & validation|
|`storage.py`|State persistence|
|`messaging.py`|Message loading & Twilio sending|
|`logger.py`|Structured logging|
|`config.py`|Environment loading & validation|

---

# 📝 Message Customization

Messages are fully customizable via text files:

config/greetings.txt  
config/messages.txt

Each line = one possible message.

### Example

#### greetings.txt

Good morning!  
Hello, good morning!  
Have a wonderful morning!

#### messages.txt

Wishing you a productive and positive day ahead.  
May today bring good energy and great moments.

> 💡 No code changes required — just edit the files

---

# ⚙️ Execution Modes

|Mode|Behavior|
|---|---|
|🟢 PROD|Enforces schedule, validation, and duplicate prevention|
|🟡 TEST|Bypasses restrictions for development|

---

# 🔐 Environment Variables

Create a `.env` file:

TWILIO_SID=your_sid  
TWILIO_TOKEN=your_token  
TWILIO_WHATSAPP_NUMBER=+14155238886  
MY_WHATSAPP_NUMBER=+5511999999999  
MODE=TEST

---

# 🛠️ Installation

## 1️⃣ Create virtual environment

python -m venv venv

---

## 2️⃣ Activate environment

### 🐧 Git Bash

source venv/Scripts/activate

### 🟦 PowerShell

.\venv\Scripts\Activate.ps1

---

## 3️⃣ Install dependencies

pip install -r requirements.txt

---

# ▶️ Local Run

python main.py

---

# ☁️ GitHub Actions Deployment

Runs automatically using cron scheduling.

### 🔑 Required Secrets

- `TWILIO_SID`
- `TWILIO_TOKEN`
- `TWILIO_WHATSAPP_NUMBER`
- `MY_WHATSAPP_NUMBER`
- `MODE`

---

# 📊 Logging

Execution history is stored in:

data/history.json

### Possible statuses:

- `schedule_created`
- `sent`
- `skipped_window`
- `skipped_duplicate`
- `error`

---

# 💡 Why this project matters

This project demonstrates:

- 🔌 API integration (Twilio)
- ☁️ Cloud automation (GitHub Actions)
- 🧱 Modular Python architecture
- ⚙️ Environment-based configuration
- ♻️ Idempotent execution control
- 💾 Persistent state management
- 📊 Structured logging

---

## 🗺️ Roadmap

### v1.1

Planned focus areas:

- Migrate persistence to SQLite
- Add automated tests
- Improve error handling
- Build dashboard / API layer

---

## 📌 Status

✅ **Stable v1.0 release**
🚧 v1.1 planned

---

## 👨‍💻 Author

Developed by **Fill "Filipe Maschio"**

If this project helped you, give it a star on GitHub ⭐