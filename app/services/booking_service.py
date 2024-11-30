from app.constans import constants
from app.exceptions.exceptions import NoCalenderFoundException, NoAvailableSlotsInCacheException
from app.models.book_time_slot_request import BookTimeSlotRequest
from app.models.models import Appointment, available_slots_cache
from app.models.search_available_request import SearchAvailabilityRequest
from app.utils.booking_service_utils import generate_daily_available_slots, get_available_slots
from app.utils.common_utils import get_slot_in_cache, get_calendar


def search_time_slots(search_availability_request: SearchAvailabilityRequest):
    """
    Search available time slots for a specific owner, updating cache only for the requested date.
    """
    try:
        owner = search_availability_request.owner
        requested_date = search_availability_request.request_date
        owner_calender = get_calendar(owner)
        available_owner_cache = available_slots_cache.get(owner) or {}
        date_key = requested_date.strftime(constants.DATE_FORMAT)
        if not owner_calender:
            print(f'no availability set for the user {owner}, available calender: {owner_calender}')
            raise NoCalenderFoundException(f"No calendar found for owner: {owner}")

        # Generate new slots for the requested date
        new_slots = generate_daily_available_slots(requested_date, owner_calender)
        print(f'new_slots: {new_slots}')
        if new_slots:
            available_owner_cache[date_key] = new_slots
        else:
            # If no new slots, remove the date from cache if it exists
            available_owner_cache.pop(date_key, None)
        slots = available_owner_cache.get(date_key, [])
        available_slots_cache[owner] = available_owner_cache
        print(f'available_owner_cache: {available_slots_cache}')
        return {"available_slots": slots}
    except NoCalenderFoundException as e:
        print(f"Error: {str(e)}")
        raise e


def book_time_slot(book_time_slot_request: BookTimeSlotRequest) -> dict:
    """
    Book a time slot for a specific owner if it's available in the cache.
    """
    try:
        start_datetime = book_time_slot_request.start_time
        end_datetime = book_time_slot_request.end_time
        date_key = start_datetime.date().strftime(constants.DATE_FORMAT)
        owner = book_time_slot_request.owner
        calendar = get_calendar(owner)

        available_slots = get_available_slots(owner, date_key)

        print(f'available_slots: {available_slots}')
        # Find the requested slot in cache
        requested_slot = {
            constants.SLOT_START_KEY: start_datetime.strftime(constants.DATETIME_FORMAT),
            constants.SLOT_END_KEY: end_datetime.strftime(constants.DATETIME_FORMAT)
        }
        slot_in_cache = get_slot_in_cache(requested_slot, available_slots)
        print(f'slot_in_cache: {slot_in_cache}')
        if not slot_in_cache:
            raise NoAvailableSlotsInCacheException(f"Requested time slot {requested_slot} is not available")
        appointment = Appointment(
            start_time=start_datetime,
            end_time=end_datetime,
            invitee=book_time_slot_request.invitee,
        )
        calendar.add_appointment(appointment)
        available_slots_cache[owner][date_key].remove(slot_in_cache)
        return {
            "message": "Appointment booked successfully",
            "appointment": {
                "start": start_datetime.strftime(constants.DATETIME_FORMAT),
                "end": end_datetime.strftime(constants.DATETIME_FORMAT),
                "invitee": book_time_slot_request.invitee,
                "owner": owner
            }
        }
    except ValueError as e:
        print("Invalid datetime format: {str(e)}")
        raise e
