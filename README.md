# WhatsApp Automated Messaging System  
  
This project is a cloud-based automation system that sends personalized WhatsApp messages using the Twilio API.

The system runs fully in the cloud using GitHub Actions and includes intelligent scheduling, randomness, execution control, and a robust scheduler design. It was built as a resilient system.

## Features

- Sends automated WhatsApp messages via Twilio API;
- Runs entirely in the cloud (no local dependency);
- Randomized daily scheduling within a predefined time window;
- Weekday-only execution (Monday–Friday);
- Prevents duplicate messages using state control;
- Handles invalid or corrupted state files gracefully;
- Uses environment variables for secure credential management;
- Designed with a robust scheduler and resilient execution logic.

## Architecture
  
- **Python** → Core logic;
- **Twilio API** → Message delivery;
- **GitHub Actions** → Scheduler & execution engine;
- **Flat files (TXT)** → State persistence.

## Scheduling Logic
  
- Multiple execution windows per day;
- A random time is selected daily;
- Only one message is sent per day;
- Tolerance window avoids missed execution due to delays;
- Designed with a robust scheduler and resilient execution logic.

## Security
  
- Credentials stored using environment variables;
- `.env` excluded via `.gitignore`;
- No sensitive data exposed in code.

## Project Structure
   ├── main.py  
   ├── messages.py  
   ├── requirements.txt  
   ├── schedule.txt  
   ├── last_sent.txt  
   └── .github/workflows/send_message.yml

## Setup  
  
### 1. Install dependencies

```markdown
pip install -r requirements.txt
```

### 2. Configure environment variables

```markdown
TWILIO_SID=your_sid  
TWILIO_TOKEN=your_token
```

### 3. Run locally  

```markdown
python main.py
```

## Deployment  
  
- Hosted on GitHub Actions;
- Runs automatically based on cron schedule;
- No server required.

## Author  
  
Developed as part of a personal automation and backend learning project.
