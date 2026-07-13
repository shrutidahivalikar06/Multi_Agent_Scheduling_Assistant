# 📅 Multi-Agent Scheduling Assistant

A LangGraph-powered Multi-Agent Scheduling Assistant that intelligently routes user requests between a Triage Agent and a Booking Specialist. The assistant can schedule appointments, check availability, retrieve booking details, validate user input, and send mock booking notifications.

---

## Features

- Multi-Agent workflow using LangGraph
- Triage Agent for intent classification
- Booking Specialist for appointment management
- General-purpose assistant for non-booking queries
- Relative date normalization (Tomorrow, Next Monday, Friday, etc.)
- Time normalization (2 PM → 14:00)
- SQLite database for appointment storage
- LangGraph SQLite Checkpointer for persistent conversation memory
- Mock notification using Webhook.site
- Streamlit chat interface

---

## Architecture

```
                User
                  │
                  ▼
          ┌────────────────┐
          │ Triage Agent   │
          └────────────────┘
             │      │
      General│      │Booking Related
             ▼      ▼
      ┌──────────┐ ┌────────────────────┐
      │ General  │ │ Booking Specialist │
      │  Agent   │ └────────────────────┘
      └──────────┘           │
                             ▼
                 ┌─────────────────────────┐
                 │ Booking Tools           │
                 │ • check_availability()  │
                 │ • reserve_slot()        │
                 │ • get_booking_details() │
                 │ • send_notification()   │
                 └─────────────────────────┘
                             │
                             ▼
                   SQLite + Webhook.site
```

---

## Project Structure

```
SchedulingAssistant/
│
├── app.py
├── graph.py
├── agents.py
├── state.py
├── tools.py
├── utils.py
├── appointments.db
├── conversation_memory.db
├── requirements.txt
├── README.md
└── .env
```

---

## Technologies Used

- Python
- LangGraph
- LangChain
- Groq (Llama 3.3 70B)
- Streamlit
- SQLite
- Webhook.site
- Dateparser

---

## Installation

Clone the repository

```bash
git clone <YOUR_GITHUB_LINK>
```

Create a virtual environment

```bash
python -m venv venv
```

Activate it

Windows

```bash
venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```
GROQ_API_KEY=your_api_key
WEBHOOK_URL=your_webhook_url
```

Run the application

```bash
streamlit run app.py
```

---

## Example Queries

### Booking

```
Book tomorrow at 10 AM. My email is shruti@gmail.com
```

### Check Availability

```
Which slots are available on Friday?
```

### Booking Details

```
Show booking for shruti@gmail.com
```

### General Question

```
What is artificial intelligence?
```

---

## Assignment Requirements Covered

- Multi-Agent Architecture
- LangGraph StateGraph
- Tool Validation
- Input Normalization
- Error Handling
- SQLite Persistence
- LangGraph SQLite Checkpointer
- Mock Notification API
- Streamlit Deployment Ready

---

## Future Improvements

- Google Calendar Integration
- Email Notifications
- Appointment Cancellation
- Appointment Rescheduling
- User Authentication
