import unittest
from datetime import datetime, time, timedelta

from app.constans import constants
from app.models.models import calendars, Calendar, AvailabilityRule, Appointment
from app.models.set_availability_request import SetAvailabilityRequest
from app.services.calendar_service import set_availability, list_upcoming_appointments_for_owner
from app.utils.datetime_utils import parse_date


class TestCalendarService(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear calendars before each test
        calendars.clear()

        self.test_owner = "test_owner"
        self.test_date = datetime(2024, 1, 15)

        # Create test availability rules
        self.test_rule = AvailabilityRule(
            start_date=self.test_date,
            end_date=datetime(2024, 12, 31),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

    def tearDown(self):
        """Clean up after each test method."""
        calendars.clear()

    def test_set_availability_new_calendar(self):
        """Test setting availability for a new calendar"""
        request = SetAvailabilityRequest(
            availability_rules=[self.test_rule]
        )

        result = set_availability(self.test_owner, request)

        self.assertIn("message", result)
        self.assertIn("new_slots", result)
        self.assertIn(self.test_owner, calendars)
        self.assertEqual(len(calendars[self.test_owner].availability_rules), 1)

    def test_set_availability_existing_calendar(self):
        """Test setting availability for an existing calendar"""
        # First create a calendar
        calendars[self.test_owner] = Calendar(owner=self.test_owner)

        request = SetAvailabilityRequest(
            availability_rules=[self.test_rule]
        )

        result = set_availability(self.test_owner, request)

        self.assertIn("message", result)
        self.assertIn("new_slots", result)
        self.assertEqual(len(calendars[self.test_owner].availability_rules), 1)

    def test_set_availability_overlapping_rules(self):
        """Test setting availability with overlapping rules"""
        # Create overlapping rules
        overlapping_rule = AvailabilityRule(
            start_date=self.test_date,
            end_date=datetime(2024, 12, 31),
            start_time=time(10, 0),  # Overlaps with test_rule
            end_time=time(18, 0)
        )

        request = SetAvailabilityRequest(
            availability_rules=[self.test_rule, overlapping_rule]
        )

        with self.assertRaises(ValueError) as context:
            set_availability(self.test_owner, request)

        self.assertIn("overlaps", str(context.exception))

    def test_set_availability_multiple_non_overlapping_rules(self):
        """Test setting multiple non-overlapping availability rules"""
        non_overlapping_rule = AvailabilityRule(
            start_date=self.test_date,
            end_date=datetime(2024, 12, 31),
            start_time=time(18, 0),  # Doesn't overlap with test_rule
            end_time=time(22, 0)
        )

        request = SetAvailabilityRequest(
            availability_rules=[self.test_rule, non_overlapping_rule]
        )

        result = set_availability(self.test_owner, request)

        self.assertIn("message", result)
        self.assertEqual(len(calendars[self.test_owner].availability_rules), 2)

    def test_list_upcoming_appointments_no_calendar(self):
        """Test listing appointments when no calendar exists"""
        result = list_upcoming_appointments_for_owner(self.test_owner)
        self.assertEqual(result, [])

    def test_list_upcoming_appointments_no_appointments(self):
        """Test listing appointments when calendar exists but has no appointments"""
        calendars[self.test_owner] = Calendar(owner=self.test_owner)

        result = list_upcoming_appointments_for_owner(self.test_owner)
        self.assertEqual(result, [])

    def test_list_upcoming_appointments_with_appointments(self):
        """Test listing appointments when appointments exist"""
        calendar = Calendar(owner=self.test_owner)
        now = datetime.now()
        # Add some test appointments
        appointment1 = Appointment(
            start_time=(now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0),
            end_time=(now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0),
            invitee="test_invitee1"
        )
        appointment2 = Appointment(
            start_time=(now + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0),
            end_time=(now + timedelta(hours=4)).replace(minute=0, second=0, microsecond=0),
            invitee="test_invitee2"
        )

        calendar.appointments = {
            now.date(): [appointment1, appointment2]
        }
        calendars[self.test_owner] = calendar

        result = list_upcoming_appointments_for_owner(self.test_owner)

        self.assertEqual(len(result), 2)
