from datetime import datetime

from app.constans import constants
from app.models.models import calendars, Calendar, AvailabilityRule
import json

from app.models.set_availability_request import SetAvailabilityRequest
from app.utils.calendar_service_utils import is_rules_overlapping


def set_availability(owner: str, set_availability_request: SetAvailabilityRequest):
    """
    Set availability for a specific Calendar Owner with a date range.
    Checks for overlapping availability rules before setting.

    Args:
        owner (str): The calendar owner
        set_availability_request (SetAvailabilityRequest): The availability request

    Returns:
        dict: Response containing success message and new slots

    Raises:
        ValueError: If there are overlapping availability rules
    """
    calendar = calendars.get(owner)
    if not calendar:
        calendar = Calendar(owner=owner)
        calendars[owner] = calendar

    # Check each new rule against existing rules and other new rules
    for new_rule in set_availability_request.availability_rules:
        # Check against existing rules
        if calendar.availability_rules:
            for existing_rule in calendar.availability_rules:
                if is_rules_overlapping(new_rule, existing_rule):
                    raise ValueError(
                        f"New availability rule ({new_rule.start_date} to {new_rule.end_date}, "
                        f"{new_rule.start_time} - {new_rule.end_time}) overlaps with existing rule "
                        f"({existing_rule.start_date.date()} to {existing_rule.end_date.date()}, "
                        f"{existing_rule.start_time} - {existing_rule.end_time})"
                    )

        # Check against other new rules
        for other_rule in set_availability_request.availability_rules:
            if new_rule != other_rule and is_rules_overlapping(new_rule, other_rule):
                raise ValueError(
                    f"Overlapping rules in request: "
                    f"({new_rule.start_date} to {new_rule.end_date}, "
                    f"{new_rule.start_time} - {new_rule.end_time}) overlaps with "
                    f"({other_rule.start_date} to {other_rule.end_date}, "
                    f"{other_rule.start_time} - {other_rule.end_time})"
                )

    # If no overlaps found, add all new rules
    for availability_rule in set_availability_request.availability_rules:
        availability = AvailabilityRule(
            start_time=availability_rule.start_time,
            end_time=availability_rule.end_time,
            start_date=availability_rule.start_date,
            end_date=availability_rule.end_date
        )
        calendar.availability_rules.append(availability)

    return {
        "message": f"Availability set for {owner}",
        "new_slots": json.dumps(
            [availability_rule.to_dict() for availability_rule in calendar.availability_rules]
        )
    }


def list_upcoming_appointments_for_owner(owner: str):
    """
    Retrieve all upcoming appointments for a calendar owner.

    Args:
        owner (str): The calendar owner

    Returns:
        list: List of upcoming appointments
    """
    owner_calendar = calendars.get(owner)
    if not owner_calendar:
        return []
    upcoming_appointments = owner_calendar.get_upcoming_appointments()
    upcoming_appointments.sort(key=lambda x: datetime.strptime(x['start_time'], constants.DATETIME_FORMAT))

    return upcoming_appointments
