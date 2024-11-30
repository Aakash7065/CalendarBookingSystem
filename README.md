python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
# Calendar Booking System

A robust calendar booking system that allows users to manage availability and handle appointment bookings efficiently.

## Features

- Set availability rules for calendar owners
- Search available time slots
- Book appointments
- List upcoming appointments
- Handle overlapping availability rules
- Cache management for better performance

## System Requirements

- Python 3.8+
- Flask
- pytest (for running tests)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/calendar-booking-system.git
cd calendar-booking-system

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


pip install -r requirements.txt

cp .env.example .env

Start the Flask server:
flask run
API Documentation

Set Availability
Set availability rules for a calendar owner.
POST /api/calendar/set_availability/<userId>
{
   {
    "availability_rules": [
        {
            "start_date": "2024-11-29",
            "end_date": "2024-12-01",
            "start_time": "09:00",
            "end_time": "17:00"
        }
    ]
}
}

{
    "message": "Availability set for user1",
    "new_slots": "[{\"start_date\": \"2024-11-29\", \"end_date\": \"2024-12-01\", \"start_time\": \"09:00\", \"end_time\": \"17:00\"}]"
}


Search Available Slots
Search for available time slots.
GET api/appointments/search_slots
Request Body:
{
    "owner": "user1",
    "request_date": "2024-12-01"
}
Response:
{
    "available_slots": [
        {
            "end": "2024-12-01T10:00",
            "start": "2024-12-01T09:00"
        },
        {
            "end": "2024-12-01T11:00",
            "start": "2024-12-01T10:00"
        },
        {
            "end": "2024-12-01T12:00",
            "start": "2024-12-01T11:00"
        },
        {
            "end": "2024-12-01T13:00",
            "start": "2024-12-01T12:00"
        },
        {
            "end": "2024-12-01T14:00",
            "start": "2024-12-01T13:00"
        },
        {
            "end": "2024-12-01T15:00",
            "start": "2024-12-01T14:00"
        },
        {
            "end": "2024-12-01T16:00",
            "start": "2024-12-01T15:00"
        },
        {
            "end": "2024-12-01T17:00",
            "start": "2024-12-01T16:00"
        }
    ]
}

Book Time Slot
Book an available time slot.
POST api/appointments/book_slot
Request Body:
{
    "owner": "user1",
    "invitee": "invitee1",
    "start_time": "2024-12-01T09:00",
    "end_time": "2024-12-01T10:00"
}
Response:
{
    "appointment": {
        "end": "2024-12-01T10:00",
        "invitee": "invitee1",
        "owner": "user1",
        "start": "2024-12-01T09:00"
    },
    "message": "Appointment booked successfully"
}

List Upcoming Appointments
GET GET /appointments/list_upcoming/{ownerId}

Response:
{
    "upcoming_appointments": [
        {
            "end_time": "2024-12-01T10:00",
            "invitee": "invitee1",
            "start_time": "2024-12-01T09:00"
        }
    ]
}


