# Task Scheduler Configuration — WhatsApp Sender

This section describes how to configure Windows Task Scheduler to execute the WhatsApp Sender automatically using a PowerShell script.

---

## 🗓️ Create Task

Open:

```
Task Scheduler → Create Task
```

---

## 🔹 General Tab

```
Name: WhatsApp Sender

✔ Run only when user is logged on
✔ Run with highest privileges
```

This is required to allow the script to open a visible window and interact with the desktop.

---

## 🔹 Triggers Tab

```
New → Daily (or preferred schedule)

Set desired time (e.g., 09:00)
✔ Enabled
```

---

## 🔹 Actions Tab

**Program/script:**

```
powershell
```

**Add arguments:**

```
-ExecutionPolicy Bypass -File "C:\Users\Falec\OneDrive\Documentos\Python\WhatsApp_Good_Morning\run_whatsapp_sender.ps1"
```

This executes the PowerShell script responsible for launching the automation.

---

## 🔹 Conditions Tab

Uncheck:

```
Start the task only if the computer is on AC power
```

Prevents the task from being blocked when running on battery.

---

## 🔹 Settings Tab

```
✔ Allow task to be run on demand
✔ If the task fails, restart every: 1 minute (optional)
✔ Stop the task if it runs longer than: (optional, e.g., 1 hour)
```

---

## ⚠️ Important Notes

- The user must be logged in
- The PC must be powered on
- The task will not display a window if configured to run in background mode
- The PowerShell script handles window behavior and execution flow

---

## ✅ Test Execution

After saving the task:

```
Right-click → Run
```

Expected behavior:

- PowerShell script is executed
- CMD window opens
- Automation runs and logs are displayed
- Message is sent via WhatsApp