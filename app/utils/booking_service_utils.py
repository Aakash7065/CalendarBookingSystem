from datetime import date, datetime, timedelta
from typing import List, Dict

from app.constans import constants
from app.exceptions.exceptions import NoAvailableSlotsInCacheException
from app.models.models import Calendar, available_slots_cache
from app.utils.common_utils import is_slot_booked


def generate_daily_available_slots(current_date: date, calendar: Calendar) -> List[Dict[str, str]]:
    """
    Generate 60-minute slots for a single day based on availability rules.

    Args:
        current_date (date): The date for which to generate slots.
        calendar (Calendar): The calendar containing availability rules and appointments.

    Returns:
        List[Dict[str, str]]: A list of available time slots with start and end times in string format.
    """
    print(f"generating available slots for user : {calendar.owner}")
    daily_slots = []

    for rule in calendar.availability_rules:
        # Check if the rule applies to the current date
        if rule.start_date <= current_date <= rule.end_date:
            start_time = datetime.combine(current_date, rule.start_time)
            end_time = datetime.combine(current_date, rule.end_time)

            while start_time + timedelta(hours=1) <= end_time:
                slot_end_time = start_time + timedelta(hours=1)

                # Format slot start and end times
                slot = {
                    constants.SLOT_START_KEY: start_time.strftime(constants.DATETIME_FORMAT),
                    constants.SLOT_END_KEY: slot_end_time.strftime(constants.DATETIME_FORMAT)
                }

                # Check if the slot is available before adding it
                if not is_slot_booked(start_time, slot_end_time, calendar):
                    daily_slots.append(slot)

                # Move to the next 60-minute slot
                start_time = slot_end_time
    print(f"available slots for user : {calendar.owner} : {daily_slots}")
    return daily_slots

def check_slots_in_cache(owner: str, date_key: str) -> list:
    """
    Check if the date has available slots in the cache for the given owner.
    Raises NoAvailableSlotsInCacheException if no slots are found.
    """
    if owner not in available_slots_cache or date_key not in available_slots_cache[owner]:
        raise NoAvailableSlotsInCacheException(f"No previous slot fetched for owner: {owner} on date {date_key}")
    return available_slots_cache[owner][date_key]

def get_available_slots(owner: str, date_key: str) -> List[Dict[str, str]]:
    """
    Get available slots for a specific owner and date from the cache.
    """
    if owner not in available_slots_cache or date_key not in available_slots_cache[owner]:
        raise NoAvailableSlotsInCacheException(f"No previous slot fetched for owner: {owner} on date {date_key}")
    return available_slots_cache[owner][date_key]

