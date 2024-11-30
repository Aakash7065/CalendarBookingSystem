import unittest
from datetime import datetime, date, time, timedelta

from app.constans import constants
from app.exceptions.exceptions import NoAvailableSlotsInCacheException
from app.models.models import Calendar, AvailabilityRule, available_slots_cache, Appointment
from app.utils.booking_service_utils import (
    generate_daily_available_slots,
    check_slots_in_cache,
    get_available_slots
)


class TestBookingServiceUtils(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear cache before each test
        available_slots_cache.clear()

        self.test_owner = "test_owner"
        self.test_date = date(2024, 1, 15)
        self.test_calendar = Calendar(owner=self.test_owner)

        # Set up test availability rule
        self.test_rule = AvailabilityRule(
            start_date=self.test_date,
            end_date=self.test_date,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.test_calendar.availability_rules.append(self.test_rule)

    def tearDown(self):
        """Clean up after each test method."""
        available_slots_cache.clear()

    def test_generate_daily_slots_success(self):
        """Test successful generation of daily slots"""
        slots = generate_daily_available_slots(self.test_date, self.test_calendar)

        self.assertIsInstance(slots, list)
        self.assertTrue(len(slots) > 0)

        # Verify slot format
        first_slot = slots[0]
        self.assertIn(constants.SLOT_START_KEY, first_slot)
        self.assertIn(constants.SLOT_END_KEY, first_slot)

        # Verify slot duration
        start_time = datetime.strptime(first_slot[constants.SLOT_START_KEY], constants.DATETIME_FORMAT)
        end_time = datetime.strptime(first_slot[constants.SLOT_END_KEY], constants.DATETIME_FORMAT)
        self.assertEqual(end_time - start_time, timedelta(hours=1))

    def test_generate_daily_slots_no_rules(self):
        """Test slot generation with no availability rules"""
        empty_calendar = Calendar(owner=self.test_owner)
        slots = generate_daily_available_slots(self.test_date, empty_calendar)

        self.assertEqual(slots, [])

    def test_generate_daily_slots_outside_rule_dates(self):
        """Test slot generation for date outside rule range"""
        outside_date = date(2025, 1, 15)
        slots = generate_daily_available_slots(outside_date, self.test_calendar)

        self.assertEqual(slots, [])

    def test_generate_daily_slots_with_appointments(self):
        """Test slot generation with existing appointments"""
        # Add an appointment
        appointment = Appointment(
            start_time=datetime.combine(self.test_date, time(9, 0)),
            end_time=datetime.combine(self.test_date, time(10, 0)),
            invitee="test_invitee"
        )
        self.test_calendar.add_appointment(appointment)

        slots = generate_daily_available_slots(self.test_date, self.test_calendar)

        # Verify the 9-10 slot is not available
        nine_am_slot = {
            constants.SLOT_START_KEY: datetime.combine(self.test_date, time(9, 0)).strftime(constants.DATETIME_FORMAT),
            constants.SLOT_END_KEY: datetime.combine(self.test_date, time(10, 0)).strftime(constants.DATETIME_FORMAT)
        }
        self.assertNotIn(nine_am_slot, slots)

    def test_check_slots_in_cache_success(self):
        """Test successful cache check"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)
        available_slots_cache[self.test_owner] = {
            date_key: [{"start": "2024-01-15 09:00", "end": "2024-01-15 10:00"}]
        }

        slots = check_slots_in_cache(self.test_owner, date_key)
        self.assertIsInstance(slots, list)
        self.assertEqual(len(slots), 1)

    def test_check_slots_in_cache_no_owner(self):
        """Test cache check with non-existent owner"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)

        with self.assertRaises(NoAvailableSlotsInCacheException):
            check_slots_in_cache("non_existent_owner", date_key)

    def test_check_slots_in_cache_no_date(self):
        """Test cache check with non-existent date"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)
        available_slots_cache[self.test_owner] = {}

        with self.assertRaises(NoAvailableSlotsInCacheException):
            check_slots_in_cache(self.test_owner, date_key)

    def test_get_available_slots_success(self):
        """Test successful retrieval of available slots"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)
        test_slots = [{"start": "2024-01-15 09:00", "end": "2024-01-15 10:00"}]
        available_slots_cache[self.test_owner] = {date_key: test_slots}

        slots = get_available_slots(self.test_owner, date_key)
        self.assertEqual(slots, test_slots)

    def test_get_available_slots_no_owner(self):
        """Test slot retrieval with non-existent owner"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)

        with self.assertRaises(NoAvailableSlotsInCacheException):
            get_available_slots("non_existent_owner", date_key)

    def test_get_available_slots_no_date(self):
        """Test slot retrieval with non-existent date"""
        date_key = self.test_date.strftime(constants.DATE_FORMAT)
        available_slots_cache[self.test_owner] = {}

        with self.assertRaises(NoAvailableSlotsInCacheException):
            get_available_slots(self.test_owner, date_key)