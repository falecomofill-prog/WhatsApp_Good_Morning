# WhatsApp_God_Morning

![Python](https://img.shields.io/badge/Python-3.11-blue)  ![Selenium](https://img.shields.io/badge/Selenium-Automation-green)  ![Status](https://img.shields.io/badge/Status-Stable-success)  ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

> WhatsApp Automated Messaging System
> (Selenium + WhatsApp Web)
  
A local automation system that sends **one personalized WhatsApp message per day** using **WhatsApp Web + Selenium**.

Designed for **reliability**, **simplicity**, and **human-like behavior**. Runs locally via **Windows Task Scheduler**.


---  
  
# Demo (What Happens in Practice)  

![Execution Demo](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\demo.gif.gif)

1. Task Scheduler triggers execution  
2. Script starts in PowerShell  
3. System checks if message was already sent  
4. Waits for random time (PROD mode)  
5. Opens WhatsApp Web  
6. Sends message  
7. Closes browser

---  

# ✨ Features  
  
- Automated WhatsApp message delivery via WhatsApp Web  
- Smart daily execution (one message per day)  
- Random send time within configurable window  
- Human-like delays (pre-send, post-send, open delays)  
- Retry mechanism with error handling  
- Execution modes (`TEST` / `PROD`)  
- Modular architecture  
- Structured logging  
- Environment-based configuration (`.env`)  
- Message templates via `.txt`  
- Headless mode with automatic fallback  
- Duplicate prevention (`last_sent.txt`)  
- Failure artifacts (screenshot + HTML)  
  
---  
  
# 📁 Project Structure  

```
WhatsApp_Good_Morning/  
├── chrome_profile/  
├── config/  
│ ├── greetings_private.txt  
│ ├── greetings.example.txt  
│ ├── messages_private.txt  
│ └── messages.example.txt  
├── data/  
│ └── last_sent.txt  
├── logs/  
│ └── execution.log  
├── modules/  
│ ├── config_loader.py  
│ ├── logger.py  
│ ├── message_generator.py  
│ └── sender_web.py  
├── .env  
├── .env.example  
├── .gitignore  
├── main.py  
├── requirements.txt  
├── requirements-lock.txt  
├── run_whatsapp_sender.ps1  
└── task_scheduler_configuration.md
```
  
---  
  
# Architecture  
  
| Module                 | Responsibility                         |     |
| ---------------------- | -------------------------------------- | --- |
| `main.py`              | Orchestration, scheduling, retry logic |     |
| `config_loader.py`     | Environment loading and validation     |     |
| `sender_web.py`        | Selenium automation (WhatsApp Web)     |     |
| `message_generator.py` | Random message generation              |     |
| `logger.py`            | Structured logging                     |     |
  
---  
  
# How It Works  
  
1. Script starts (via Task Scheduler or manual execution)  
2. Loads configuration from `.env`  
3. Checks if a message was already sent today (`last_sent.txt`)  
4. If `MODE=PROD`:  
   - selects a random time inside the configured window  
   - waits until that time  
5. Generates a random message from `.txt` files  
6. Opens WhatsApp Web via Selenium  
7. Sends the message  
8. Validates send (lightweight)  
9. Stores today's date in `last_sent.txt`  
10. Closes browser  
  
---  
  
# Execution Modes  
  
| Mode    | Behavior                                   |     |
| ------- | ------------------------------------------ | --- |
| 🟡 TEST | Ignores send window, runs immediately      |     |
| 🟢 PROD | Enforces time window and random scheduling |     |
  
---  
  
# Smart Scheduling  
  
Configured via `.env`:  

```
SEND_WINDOW_ENABLED=true  
SEND_WINDOW_START=08:30  
SEND_WINDOW_END=09:30
```

### Behavior

- Script starts at beginning of window
- Random send time is selected
- Message is sent once within the window

---

# Duplicate Protection

Uses:

**data/last_sent.txt**

- Stores last successful send date
- Prevents multiple sends in the same day
- Ensures idempotent execution

Example:
![Duplicate Protection](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\duplicate_protection.jpg.jpg)

---

# Human-like Behavior

Delays are randomized:

- open delay
- pre-send delay
- post-send delay

Configured via `.env`:

```
MIN_PRE_SEND_DELAY_SECONDS=3  
MAX_PRE_SEND_DELAY_SECONDS=7
```

---

# 🔐 Configuration (.env)

Example:

```
MODE=TEST

SEND_WINDOW_ENABLED=true  
SEND_WINDOW_START=08:30  
SEND_WINDOW_END=09:30

DESTINATION_PHONE=551199887766 
  
CHROME_PROFILE_PATH=chrome_profile  
CHROME_PROFILE_DIRECTORY=  
  
WHATSAPP_WEB_URL=https://web.whatsapp.com  
  
GREETINGS_FILE=config/greetings_private.txt  
MESSAGES_FILE=config/messages_private.txt  
  
HEADLESS=false  
ENABLE_HEADLESS_FALLBACK=true  
  
USE_RANDOM_DELAY=true  
  
ELEMENT_TIMEOUT_SECONDS=60  
PAGE_LOAD_TIMEOUT_SECONDS=60  
SCRIPT_TIMEOUT_SECONDS=60  
  
MIN_OPEN_DELAY_SECONDS=2  
MAX_OPEN_DELAY_SECONDS=5  
  
MIN_PRE_SEND_DELAY_SECONDS=3  
MAX_PRE_SEND_DELAY_SECONDS=7  
  
MIN_POST_SEND_DELAY_SECONDS=2  
MAX_POST_SEND_DELAY_SECONDS=4  
  
MAX_RETRIES=2  
RETRY_DELAY_SECONDS=5  
```

---

# 📝 Message Customization

Edit:

**config/greetings_private.txt**  
**config/messages_private.txt**

Each line = one possible message.

Example:

```
Good morning!  
Have a great day!
(...)
```

---

# 🛠️ Installation

### 1️⃣ Create virtual environment

```
python -m venv venv
```

### 2️⃣ Activate

```powershell
.\venv\Scripts\Activate.ps1
```

```bash
source venv\scripts\activate
```

### 3️⃣ Install dependencies

```
pip install -r requirements.txt
```

---

# ▶️ Run Locally

```
python main.py
```

---

# 🖥️ Automation (Windows Task Scheduler)

Recommended setup:

- Trigger: daily
- Time: start of send window (e.g., 08:30)
- Action: run `run_whatsapp_sender.ps1`

The script handles:

- randomization
- execution control
- duplicate prevention

---

### Step-by-Step: Task Scheduler Configuration  

#### Create Task

Open: Task Scheduler → Create Task

#### General Tab

Configure:  
Name: WhatsApp Sender
✔ Run only when user is logged on  
✔ Run with highest privileges

![General Tab](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\task_manager_1_general_tab.jpg)

#### Triggers Tab

Click **New**:
Begin the task: On a schedule  
Settings: Daily  
Time: 08:30 (start of your send window)  
✔ Enabled

Note: The script will choose a random time **inside the configured window**, so this should match the **window start time**.

#### Actions Tab

Click **New**
Program/script:
```
powershell
```
Add arguments: 
```
-ExecutionPolicy Bypass -File "C:\Users\YOUR_USER\Path\To\Project\run_whatsapp_sender.ps1"
```

**Important**: Replace with your actual path.  

![General Tab](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\task_manager_2_actions_tab.jpg)

#### Conditions Tab  
  
Uncheck: Start the task only if the computer is on AC power

![General Tab](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\task_manager_3_conditions_tab.jpg)

#### Settings Tab  
  
Recommended:
✔ Allow task to be run on demand

(Optional)  
✔ If the task fails, restart every: 1 minute  
✔ Stop the task if it runs longer than: 1 hour

![General Tab](C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\docs\task_manager_4_settings_tab.jpg)

#### Test the Task  
  
After saving: Right-click → Run

Expected behavior:  
  
- PowerShell window opens  
- Script starts execution  
- Chrome launches  
- WhatsApp Web loads  
- Message is sent  
- Logs are displayed in real time  
  
---  
  
# ⚠️ Important Notes  
  
- The PC must be **powered on**  
- The user must be **logged in**  
- The task **will NOT run properly in background mode**  
- Selenium requires an active desktop session  
- First execution may require scanning the WhatsApp QR code  
  
---  

# Pro Tips  
  
- Use `MODE=TEST` to validate setup quickly  
- Keep logs open during initial tests  
- Avoid running manually + scheduler at the same time  
- Ensure Chrome is fully closed before execution (to avoid profile conflicts

---

# Logging

Logs stored in:

**logs/execution.log**

Includes:

- execution flow
- retries
- errors
- timing

---

# Failure Handling

- Retry system for transient errors
- Automatic headless fallback
- Screenshot + HTML capture on failure
- Graceful exit on non-retryable errors

---

# Dependencies

```
selenium  
python-dotenv
```

---

# Design Principles

- Minimal dependencies
- Local-first execution
- Deterministic behavior
- Config-driven system
- Fail-safe execution
- Clean modular architecture

---

# 🧠 Why This Project Matters  
  
This is not just a script.  
  
It demonstrates **real engineering thinking**:  
  
- deterministic execution  
- system reliability  
- user-behavior simulation  
- safe automation design

---

# 📌 Status

✅ Stable (v1.1)  
🚀 Production-ready for personal automation

---

# 👨‍💻 Author

Developed by Fill (Filipe Maschio)

If this project helped you, consider giving it a star ⭐