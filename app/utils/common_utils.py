from datetime import datetime
from typing import List

from app.constans import constants
from app.exceptions.exceptions import NoCalenderFoundException
from app.models.models import Calendar, calendars


def get_calendar(owner: str) -> Calendar:
    """
    Retrieve the calendar for the given owner.
    Raises NoCalenderFoundException if the calendar is not found.
    """
    calendar = calendars.get(owner)
    if not calendar:
        raise NoCalenderFoundException(f"Calendar not found for owner: {owner}")
    return calendar


def is_slot_booked(start_datetime: datetime, end_datetime: datetime, calendar: Calendar):
    """
    Check if a specific time slot is booked for a given owner.

    Args:
        start_datetime : datetime object representing the start time of the slot
        end_datetime : datetime object representing the end time of the slot
        calendar: Calendar object containing the appointments

    Returns:
        bool: True if the slot is booked, False otherwise

    """

    # Get the date to check in the appointments dictionary
    check_date = start_datetime.date()

    # If the date exists in appointments
    if check_date in calendar.appointments:
        # Check all appointments for that date for any overlap
        for appointment in calendar.appointments[check_date]:
            # Check for any type of overlap:
            # 1. New slot starts during an existing appointment
            # 2. New slot ends during an existing appointment
            # 3. New slot completely contains an existing appointment
            # 4. New slot is completely contained within an existing appointment
            if (
                    (appointment.end_time > start_datetime >= appointment.start_time) or
                    (appointment.start_time < end_datetime <= appointment.end_time) or
                    (start_datetime <= appointment.start_time and
                     end_datetime >= appointment.end_time) or
                    (start_datetime >= appointment.start_time and
                     end_datetime <= appointment.end_time)
            ):
                return True
    return False

def get_slot_in_cache(requested_slot: dict, cached_slots: List[dict]) -> dict:
    """
    Check if the requested slot exists within the cached slots.

    Args:
        requested_slot (dict): The slot being requested
        cached_slots (List[dict]): List of available slots in cache

    Returns:
        bool: True if slot is available, False otherwise
    """
    try:
        for cached_slot in cached_slots:
            cached_start = datetime.strptime(cached_slot[constants.SLOT_START_KEY], constants.DATETIME_FORMAT)
            cached_end = datetime.strptime(cached_slot[constants.SLOT_END_KEY], constants.DATETIME_FORMAT)
            requested_start = datetime.strptime(requested_slot[constants.SLOT_START_KEY], constants.DATETIME_FORMAT)
            requested_end = datetime.strptime(requested_slot[constants.SLOT_END_KEY], constants.DATETIME_FORMAT)

            # Check if requested slot fits within a cached slot
            if (cached_start == requested_start and
                    cached_end == requested_end):
                print(f'slot exists in cache: {cached_slot}')
                return cached_slot

        return {}
    except ValueError as e:
        print(f"Invalid datetime format in cache: {str(e)}")
        raise e