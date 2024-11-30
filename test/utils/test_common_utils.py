import unittest
from datetime import datetime, date, time

from app.constans import constants
from app.exceptions.exceptions import NoCalenderFoundException
from app.models.models import Calendar, Appointment, calendars
from app.utils.common_utils import get_calendar, is_slot_booked, get_slot_in_cache


class TestCommonUtils(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear calendars before each test
        calendars.clear()

        self.test_owner = "test_owner"
        self.test_date = datetime(2024, 1, 15)
        self.test_calendar = Calendar(owner=self.test_owner)

    def tearDown(self):
        """Clean up after each test method."""
        calendars.clear()

    def test_get_calendar_success(self):
        """Test successful calendar retrieval"""
        calendars[self.test_owner] = self.test_calendar

        result = get_calendar(self.test_owner)
        self.assertEqual(result, self.test_calendar)
        self.assertEqual(result.owner, self.test_owner)

    def test_get_calendar_not_found(self):
        """Test calendar retrieval when calendar doesn't exist"""
        with self.assertRaises(NoCalenderFoundException) as context:
            get_calendar("non_existent_owner")

        self.assertIn("Calendar not found", str(context.exception))

    def test_is_slot_booked_no_appointments(self):
        """Test slot booking check with no existing appointments"""
        start_time = datetime(2024, 1, 15, 9, 0)
        end_time = datetime(2024, 1, 15, 10, 0)

        result = is_slot_booked(start_time, end_time, self.test_calendar)
        self.assertFalse(result)

    def test_is_slot_booked_with_overlap(self):
        """Test slot booking check with overlapping appointment"""
        # Add an appointment
        appointment = Appointment(
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            invitee="test_invitee"
        )
        self.test_calendar.appointments[date(2024, 1, 15)] = [appointment]

        # Test overlapping slot
        start_time = datetime(2024, 1, 15, 9, 30)
        end_time = datetime(2024, 1, 15, 10, 30)

        result = is_slot_booked(start_time, end_time, self.test_calendar)
        self.assertTrue(result)

    def test_is_slot_booked_no_overlap(self):
        """Test slot booking check with non-overlapping appointment"""
        # Add an appointment
        appointment = Appointment(
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            invitee="test_invitee"
        )
        self.test_calendar.appointments[date(2024, 1, 15)] = [appointment]

        # Test non-overlapping slot
        start_time = datetime(2024, 1, 15, 10, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        result = is_slot_booked(start_time, end_time, self.test_calendar)
        self.assertFalse(result)

    def test_is_slot_booked_contained_slot(self):
        """Test slot booking check with slot contained within appointment"""
        # Add an appointment
        appointment = Appointment(
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 11, 0),
            invitee="test_invitee"
        )
        self.test_calendar.appointments[date(2024, 1, 15)] = [appointment]

        # Test contained slot
        start_time = datetime(2024, 1, 15, 9, 30)
        end_time = datetime(2024, 1, 15, 10, 30)

        result = is_slot_booked(start_time, end_time, self.test_calendar)
        self.assertTrue(result)

    def test_is_slot_booked_containing_slot(self):
        """Test slot booking check with slot containing appointment"""
        # Add an appointment
        appointment = Appointment(
            start_time=datetime(2024, 1, 15, 9, 30),
            end_time=datetime(2024, 1, 15, 10, 30),
            invitee="test_invitee"
        )
        self.test_calendar.appointments[date(2024, 1, 15)] = [appointment]

        # Test containing slot
        start_time = datetime(2024, 1, 15, 9, 0)
        end_time = datetime(2024, 1, 15, 11, 0)

        result = is_slot_booked(start_time, end_time, self.test_calendar)
        self.assertTrue(result)

    def test_get_slot_in_cache_success(self):
        """Test successful slot retrieval from cache"""
        requested_slot = {
            constants.SLOT_START_KEY: "2024-01-15T09:00",
            constants.SLOT_END_KEY: "2024-01-15T10:00"
        }

        cached_slots = [
            {
                constants.SLOT_START_KEY: "2024-01-15T09:00",
                constants.SLOT_END_KEY: "2024-01-15T10:00"
            }
        ]

        result = get_slot_in_cache(requested_slot, cached_slots)
        self.assertEqual(result, cached_slots[0])

    def test_get_slot_in_cache_not_found(self):
        """Test slot retrieval when slot not in cache"""
        requested_slot = {
            constants.SLOT_START_KEY: "2024-01-15T09:00",
            constants.SLOT_END_KEY: "2024-01-15T10:00"
        }

        cached_slots = [
            {
                constants.SLOT_START_KEY: "2024-01-15T10:00",
                constants.SLOT_END_KEY: "2024-01-15T11:00"
            }
        ]

        result = get_slot_in_cache(requested_slot, cached_slots)
        self.assertEqual(result, {})

    def test_get_slot_in_cache_invalid_format(self):
        """Test slot retrieval with invalid datetime format"""
        requested_slot = {
            constants.SLOT_START_KEY: "invalid_format",
            constants.SLOT_END_KEY: "2024-01-15 10:00"
        }

        cached_slots = [
            {
                constants.SLOT_START_KEY: "2024-01-15 09:00",
                constants.SLOT_END_KEY: "2024-01-15 10:00"
            }
        ]

        with self.assertRaises(ValueError):
            get_slot_in_cache(requested_slot, cached_slots)