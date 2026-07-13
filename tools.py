import sqlite3
import requests

DB_NAME = "appointments.db"
WEBHOOK_URL = "https://webhook.site/f97d7240-1173-41a5-8d84-15fffbc54b1d"

# Available slots for every day
DEFAULT_SLOTS = [
    "09:00",
    "10:00",
    "11:00",
    "14:00",
    "15:00",
    "16:00"
]


def check_availability(date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT time FROM appointments WHERE date = ?",
        (date,)
    )

    booked_slots = [row[0] for row in cursor.fetchall()]
    conn.close()

    available_slots = [
        slot for slot in DEFAULT_SLOTS
        if slot not in booked_slots
    ]

    return available_slots

def reserve_slot(date, time, email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check if the slot is already booked
    cursor.execute(
        "SELECT * FROM appointments WHERE date = ? AND time = ?",
        (date, time)
    )

    existing_booking = cursor.fetchone()

    if existing_booking:
        conn.close()
        return {
            "success": False,
            "message": "This slot is already booked."
        }

    # Save the booking
    cursor.execute(
        """
        INSERT INTO appointments (date, time, email)
        VALUES (?, ?, ?)
        """,
        (date, time, email)
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Appointment booked successfully."
    }

def send_booking_notification(email, details):
    try:
        payload = {
            "email": email,
            "booking_details": details
        }

        response = requests.post(
            WEBHOOK_URL,
            json=payload
        )

        if response.status_code == 200:
            return {
                "success": True,
                "message": "Notification sent successfully."
            }

        return {
            "success": False,
            "message": f"Webhook returned status code {response.status_code}"
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }
    
def get_booking_details(email):

    conn = sqlite3.connect("appointments.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT date, time
        FROM appointments
        WHERE email = ?
        ORDER BY date, time
        """,
        (email,)
    )

    bookings = cursor.fetchall()

    conn.close()

    return bookings