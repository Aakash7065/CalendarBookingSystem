from typing import Dict, Any

from app.models.models import AvailabilityRule
from app.models.set_availability_request import SetAvailabilityRequest
from app.utils.datetime_utils import parse_date, parse_time


def map_to_set_availability_request(data: Dict[str, Any]) -> SetAvailabilityRequest:
    """
    Map dictionary data to SetAvailabilityRequest object with proper AvailabilityRule transformations.

    Args:
        data (dict): Dictionary containing availability data with format:
            {
                "availability_rules": [
                    {
                        "start_date": "YYYY-MM-DD",
                        "end_date": "YYYY-MM-DD",
                        "start_time": "HH:MM",
                        "end_time": "HH:MM"
                    },
                    ...
                ]
            }

    Returns:
        SetAvailabilityRequest: Transformed request object.

    Raises:
        ValueError: If date or time format is invalid.
        KeyError: If required fields are missing.
    """
    print("inside map_to_set_availability_request")
    print(data)
    if not isinstance(data, dict) or "availability_rules" not in data:
        raise ValueError("Invalid input: 'availability_rules' key is missing or data is not a dictionary.")

    try:
        transformed_rules = [
            AvailabilityRule(
                start_date=parse_date(rule["start_date"]),
                end_date=parse_date(rule["end_date"]),
                start_time=parse_time(rule["start_time"]),
                end_time=parse_time(rule["end_time"]),
            )
            for rule in data["availability_rules"]
        ]
        return SetAvailabilityRequest(availability_rules=transformed_rules)

    except KeyError as e:
        print(f"Missing required field in availability rule: {e.args[0]}")
        raise KeyError(f"Missing required field in availability rule: {e.args[0]}") from e
