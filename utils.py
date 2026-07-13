from datetime import datetime, timedelta
import dateparser

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def normalize_date(date_text):

    if not date_text:
        return None

    text = date_text.strip().lower()

    today = datetime.today()

    # today
    if text == "today":
        return today.strftime("%Y-%m-%d")

    # tomorrow
    if text == "tomorrow":
        return (today + timedelta(days=1)).strftime("%Y-%m-%d")

    # next monday, next friday, etc.
    if text.startswith("next "):
        day = text.replace("next ", "").strip()

        if day in WEEKDAYS:
            target = WEEKDAYS[day]

            days_ahead = (target - today.weekday()) % 7

            if days_ahead == 0:
                days_ahead = 7

            return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    # fallback to dateparser
    parsed = dateparser.parse(
        date_text,
        settings={"PREFER_DATES_FROM": "future"}
    )

    if parsed:
        return parsed.strftime("%Y-%m-%d")

    return None

from datetime import datetime


from datetime import datetime
import re


def normalize_time(time_text):

    if not time_text:
        return None

    # Add a space before AM/PM if user writes 10PM or 9AM
    text = re.sub(r"(?i)(\d)(am|pm)$", r"\1 \2", time_text.strip())

    formats = [
        "%I %p",
        "%I:%M %p",
        "%H:%M",
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.strftime("%H:%M")
        except ValueError:
            continue

    return time_text