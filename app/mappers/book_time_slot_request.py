from app.constans import constants
from app.models.book_time_slot_request import BookTimeSlotRequest
from app.utils.datetime_utils import parse_date


def map_to_book_time_slot_request(data: dict) -> BookTimeSlotRequest:
    """
    Map dictionary data to BookTimeSlotRequest object.

    Args:
        data (dict): Dictionary containing booking data with format:
            {
                "owner": "owner_name",
                "invitee": "invitee_name",
                "start_time": "YYYY-MM-DDTHH:MM",
                "end_time": "YYYY-MM-DDTHH:MM"
            }

    Returns:
        BookTimeSlotRequest: Transformed request object
    """
    try:
        owner = data["owner"]
        invitee = data["invitee"]
        if not owner or not invitee:
            print("Owner and invitee names cannot be empty.")
            raise ValueError("Owner and invitee names cannot be empty.")
        start_time = parse_date(data["start_time"], constants.DATETIME_FORMAT)
        end_time = parse_date(data["end_time"], constants.DATETIME_FORMAT)
        if not owner or not invitee:
            print("Owner and invitee names cannot be empty.")
            raise ValueError("Owner and invitee names cannot be empty.")

        if start_time >= end_time:
            print("Start time must be before end time.")
            raise ValueError("Start time must be before end time.")

        return BookTimeSlotRequest(
            owner=owner,
            invitee=invitee,
            start_time=start_time,
            end_time=end_time
        )
    except KeyError as e:
        print(f"Missing required field: {str(e)}")
        raise ValueError(f"Missing required field: {str(e)}")