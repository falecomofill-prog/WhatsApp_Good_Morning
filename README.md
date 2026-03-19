# WhatsApp Automated Messaging System  
  
A cloud-based automation system that sends personalized WhatsApp messages using the Twilio API.

This project runs fully in the cloud via GitHub Actions and was designed with a focus on **resilience**, **reliability**, and **clean engineering practices**.

## Features

- Automated WhatsApp message delivery via Twilio API;
- Fully serverless execution (GitHub Actions);
- Intelligent daily scheduling with randomized execution;
- Execution restricted to weekdays (Monday–Friday);
- Time window control with tolerance handling;
- Duplicate prevention using state persistence (idempotency);
- Graceful handling of corrupted or missing state files;
- Secure configuration using environment variables;
- Structured logging (`history.json`) for traceability;
- Environment-based behavior (`TEST` vs `PROD` mode).

## Architecture
  
- **Python** → Core application logic;
- **Twilio API** → Message delivery service;
- **GitHub Actions** → Scheduler and execution engine;
- **Flat files (TXT/JSON)** → Lightweight state persistence.

## Scheduling Logic
  
The system implements a resilient scheduling strategy:

- Multiple execution triggers per day (via cron);
- A **random execution time is selected daily**;
- Execution only occurs if within a tolerance window (±10 minutes);
- Ensures **exactly one message per day**;
- Designed to tolerate delays in GitHub Actions execution.

## Security
  
- All credentials stored in environment variables;
- `.env` file excluded via `.gitignore`;
- No sensitive data hardcoded;
- Phone numbers and API credentials externalized.

## Configuration Management

The project uses a dedicated `config.py` module to centralize configuration:

- Loads environment variables;
- Validates required credentials;
- Formats Twilio-compatible values;
- Decouples configuration from business logic.

## Execution Modes

The system supports two execution modes:

| Mode | Behavior |
|------|--------|
| `PROD` | Enforces time window, tolerance, and duplicate prevention |
| `TEST` | Ignores execution restrictions for development/testing |

Set via `.env`:

```.env
MODE=TEST
```

## Project Structure
├── main.py                  # Core application logic
├── config.py                # Configuration management
├── messages.py              # Message templates
├── requirements.txt         # Dependencies
├── schedule.txt             # Daily scheduled time
├── last_sent.txt            # Idempotency control
├── history.json             # Execution logs
└── .github/workflows/
    └── send_message.yml     # Cloud scheduler (GitHub Actions)

## Setup

1. Create virtual environment

```
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies

```
pip install -r requirements.txt
```

3. Configure environment variables

Create a .env file:

```
# Twilio credentials
TWILIO_SID=your_sid
TWILIO_TOKEN=your_token

# WhatsApp numbers
TWILIO_WHATSAPP_NUMBER=+14155238886
MY_WHATSAPP_NUMBER=+5511999999999

# Execution mode
MODE=TEST
```

4. Run locally

```
python main.py
```

## Deployment

Hosted using GitHub Actions;
Triggered via cron schedule;
Runs automatically in the cloud;
No infrastructure or server required.

## Logging

Execution history is stored in:

```
history.json
```

Each entry includes:

- Date and time;
- Scheduled execution time;
- Status (sent, future-ready for skipped, etc.);
- Message content.

## Key Engineering Concepts Demonstrated

- Serverless automation;
- API integration (Twilio);
- Idempotent system design;
- Fault-tolerant scheduling;
- Environment-based configuration;
- Secure credential handling;
- Structured logging.

## Author

Developed as a personal project focused on backend engineering, automation, and cloud execution.
