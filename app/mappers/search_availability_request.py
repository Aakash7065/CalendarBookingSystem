from app.models.search_available_request import SearchAvailabilityRequest
from app.utils.datetime_utils import parse_date


def map_to_search_availability_request(data: dict) -> SearchAvailabilityRequest:
    """
    Map dictionary data to SearchAvailabilityRequest object.

    Args:
        data (dict): Dictionary containing search availability data with format:
            {
                "owner": "owner_name",
                "date": "YYYY-MM-DD"
            }

    Returns:
        SearchAvailabilityRequest: Transformed request object
    """
    try:
        owner = data["owner"]
        request_date = parse_date(data["request_date"])
        if not owner or not request_date:
            raise ValueError("owner field is required")
        return SearchAvailabilityRequest(
            owner=owner,
            request_date=request_date
        )
    except KeyError as e:
        print(f"Missing required field: {str(e)}")
        raise KeyError(f"Missing required field: {str(e)}")