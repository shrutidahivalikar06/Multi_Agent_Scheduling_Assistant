from unittest import result

from dotenv import load_dotenv
import os

from utils import normalize_date, normalize_time
from pydantic import BaseModel
from langchain_groq import ChatGroq
from tools import (
    check_availability,
    reserve_slot,
    send_booking_notification,
    get_booking_details
)


load_dotenv()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


from typing import Literal

class TriageResponse(BaseModel):
    intent: Literal[
        "book",
        "availability",
        "booking_details",
        "general"
    ]

class BookingDetails(BaseModel):
    date: str | None = None
    time: str | None = None
    email: str | None = None
structured_llm = llm.with_structured_output(TriageResponse)
booking_llm = llm.with_structured_output(BookingDetails)

def triage_agent(state):

    user_message = state["messages"][-1].content

    prompt = f"""
You are a triage agent for a scheduling assistant.

Classify the user's request into EXACTLY ONE of these intents.

1. book
- User wants to schedule, reserve or book an appointment.

Examples:
- Book tomorrow at 10 AM
- Schedule a meeting
- Reserve Friday 2 PM

2. availability
- User wants to know available slots or free timings.

Examples:
- Which slots are available?
- Is Friday free?
- Show available times tomorrow

3. booking_details
- User wants information about an existing booking.

Examples:
- When was Raghu's session booked?
- Show my appointment
- What is my booking?
- Do I have an appointment tomorrow?

4. general
- Any other question.

Return ONLY one intent.

User:
{user_message}
"""

    result = structured_llm.invoke(prompt)
    print("Detected Intent:", result.intent) 


    state["intent"] = result.intent

    return state

booking_llm = llm.with_structured_output(BookingDetails)

def extract_booking_details(state):

    user_message = state["messages"][-1].content

    prompt = f"""
    You are an information extraction assistant.

    Extract ONLY the booking details present in the latest user message.

    Fields:
    - date
    - time
    - email

    Rules:
    - If a field is missing, return null.
    - Do NOT invent information.
    - Do NOT reuse previous conversation.
    - Only extract what the latest message contains.

    Latest user message:

    {user_message}
    """

    details = booking_llm.invoke(prompt)

    print("\n===== LLM Extraction =====")
    print(details)
    print(f"Date  : {details.date}")
    print(f"Time  : {details.time}")
    print(f"Email : {details.email}")
    print("==========================\n")

    if details.date:
        state["date"] = details.date

    if details.time:
        state["time"] = details.time

    if details.email:
        state["email"] = details.email

    return state

def check_missing_information(state):

    missing = []

    if not state.get("date"):
        missing.append("date")

    if not state.get("time"):
        missing.append("time")

    if not state.get("email"):
        missing.append("email")

    return missing

def booking_specialist(state):

    intent = state["intent"]

    # Extract information from the user's message
    state = extract_booking_details(state)

    if state.get("date"):
        state["date"] = normalize_date(state["date"])

    if state.get("time"):
        state["time"] = normalize_time(state["time"])
        print("Normalized Time:", state["time"])

    # -------------------------
    # Availability
    # -------------------------
    if intent == "availability":

        if not state.get("date"):
            state["response"] = (
                "Which date would you like to check availability for?"
            )
            return state

        available_slots = check_availability(state["date"])

        if available_slots:
            state["response"] = (
                f"Available slots for {state['date']}:\n\n"
                + "\n".join(available_slots)
            )
        else:
            state["response"] = (
                f"No slots are available on {state['date']}."
            )

        return state

    # -------------------------
    # Booking Details
    # -------------------------
    if intent == "booking_details":

        if not state.get("email"):
            state["response"] = (
                "Please provide the email address used for the booking."
            )
            return state

        bookings = get_booking_details(state["email"])

        if not bookings:
            state["response"] = (
                f"No booking found for {state['email']}."
            )
            return state

        response = f"Bookings for {state['email']}:\n\n"

        for date, time in bookings:
            response += f"📅 {date} at {time}\n"

        state["response"] = response

        return state

    # -------------------------
    # Book Appointment
    # -------------------------

    missing = check_missing_information(state)

    if missing:
        state["response"] = (
            f"Please provide the following information: {', '.join(missing)}"
        )
        return state

    available_slots = check_availability(state["date"])
    state["available_slots"] = available_slots

    if state["time"] not in available_slots:

        state["response"] = (
            f"Sorry, {state['time']} is not available.\n\n"
            f"Available slots are:\n"
            + "\n".join(available_slots)
            + "\n\nWhich slot would you like to book?"
        )

        return state

    booking = reserve_slot(
        state["date"],
        state["time"],
        state["email"]
    )

    if not booking["success"]:
        state["response"] = booking["message"]
        return state

    notification = send_booking_notification(
        state["email"],
        {
            "date": state["date"],
            "time": state["time"]
        }
    )

    state["booking_status"] = "confirmed"

    state["response"] = (
        "✅ Appointment booked successfully!\n\n"
        f"Date: {state['date']}\n"
        f"Time: {state['time']}\n\n"
        f"{notification['message']}"
    )

    return state

def general_agent(state):

    user_message = state["messages"][-1].content

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question naturally and concisely.

User:
{user_message}
"""

    response = llm.invoke(prompt)

    state["response"] = response.content

    return state
