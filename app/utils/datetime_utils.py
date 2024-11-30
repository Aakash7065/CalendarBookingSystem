from datetime import datetime, time


def parse_date(date_str: str, date_format: str = "%Y-%m-%d") -> datetime:
    """
    Parse a date string into a datetime object.

    Args:
        date_str (str): Date string in "YYYY-MM-DD" format.
        date_format (str, optional): Date format string. Defaults to "%Y-%m-%d".

    Returns:
        datetime: Parsed datetime object.

    Raises:
        ValueError: If the date format is invalid.
    """
    try:
        print(date_str, date_format)
        return datetime.strptime(date_str, date_format)
    except ValueError:
        print(f"Invalid date format: '{date_str}', expected '{date_format}'.")
        raise ValueError(f"Invalid date format: '{date_str}', expected '{date_format}'.")


def parse_time(time_str: str) -> time:
    """
    Parse a time string into a time object.

    Args:
        time_str (str): Time string in "HH:MM" format.

    Returns:
        time: Parsed time object.

    Raises:
        ValueError: If the time format is invalid.
    """
    if len(time_str) != 5 or time_str[2] != ':':
        raise ValueError(f"Invalid time format: '{time_str}', expected 'HH:MM'.")

    try:
        parsed_time = datetime.strptime(time_str, "%H:%M").time()
    except ValueError as v:
        print(v)
        print(f"Invalid time format: '{time_str}', expected 'HH:MM'.")
        raise ValueError(f"Invalid time format: '{time_str}', expected 'HH:MM'.")

        # Validate hour and minute ranges
    if parsed_time.hour < 0 or parsed_time.hour > 23:
        raise ValueError(f"Invalid hour value: {parsed_time.hour}. Hour must be between 00 and 23.")
    if parsed_time.minute < 0 or parsed_time.minute > 59:
        raise ValueError(f"Invalid minute value: {parsed_time.minute}. Minute must be between 00 and 59.")

    return parsed_time