import unittest
from datetime import datetime, time
from unittest.mock import patch
from app.exceptions.exceptions import NoCalenderFoundException, NoAvailableSlotsInCacheException
from app.models.book_time_slot_request import BookTimeSlotRequest
from app.models.models import Calendar, Appointment, available_slots_cache, AvailabilityRule
from app.models.search_available_request import SearchAvailabilityRequest
from app.services.booking_service import search_time_slots, book_time_slot


class TestBookingService(unittest.TestCase):
    def setUp(self):
        available_slots_cache.clear()

        self.test_owner = "test_owner"
        self.test_date = datetime(2024, 1, 15)
        self.test_calendar = Calendar(owner=self.test_owner)

        # Set up mock calendar with availability
        self.test_calendar.availability_rules = [
            AvailabilityRule(
                start_date=self.test_date,
                end_date=self.test_date,
                start_time=time(9, 0),
                end_time=time(17, 0)
            )
        ]

    def tearDown(self):
        """Clean up after each test method."""
        available_slots_cache.clear()

    @patch('app.services.booking_service.get_calendar')
    def test_search_time_slots_success(self, mock_get_calendar):
        """Test successful search for time slots"""
        mock_get_calendar.return_value = self.test_calendar

        request = SearchAvailabilityRequest(
            owner=self.test_owner,
            request_date=self.test_date
        )

        result = search_time_slots(request)

        self.assertIn("available_slots", result)
        self.assertIsInstance(result["available_slots"], list)
        # Verify cache was updated
        self.assertIn(self.test_owner, available_slots_cache)

    @patch('app.services.booking_service.get_calendar')
    def test_search_time_slots_no_calendar(self, mock_get_calendar):
        """Test search when no calendar exists"""
        mock_get_calendar.return_value = None

        request = SearchAvailabilityRequest(
            owner=self.test_owner,
            request_date=self.test_date
        )

        with self.assertRaises(NoCalenderFoundException):
            search_time_slots(request)

    @patch('app.services.booking_service.get_calendar')
    def test_search_time_slots_no_availability(self, mock_get_calendar):
        """Test search when no availability exists"""
        empty_calendar = Calendar(owner=self.test_owner)
        mock_get_calendar.return_value = empty_calendar

        request = SearchAvailabilityRequest(
            owner=self.test_owner,
            request_date=self.test_date
        )

        result = search_time_slots(request)
        self.assertEqual(result["available_slots"], [])

    @patch('app.services.booking_service.get_calendar')
    def test_book_time_slot_success(self, mock_get_calendar):
        """Test successful booking of a time slot"""
        mock_get_calendar.return_value = self.test_calendar

        # First search to populate cache
        search_request = SearchAvailabilityRequest(
            owner=self.test_owner,
            request_date=self.test_date
        )
        search_time_slots(search_request)

        # Then book a slot
        book_request = BookTimeSlotRequest(
            owner=self.test_owner,
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            invitee="test_invitee"
        )

        result = book_time_slot(book_request)

        self.assertIn("message", result)
        self.assertIn("appointment", result)
        self.assertEqual(result["appointment"]["owner"], self.test_owner)
        self.assertEqual(result["appointment"]["invitee"], "test_invitee")

    @patch('app.services.booking_service.get_calendar')
    def test_book_time_slot_not_available(self, mock_get_calendar):
        """Test booking when slot is not available"""
        mock_get_calendar.return_value = self.test_calendar

        book_request = BookTimeSlotRequest(
            owner=self.test_owner,
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            invitee="test_invitee"
        )

        with self.assertRaises(NoAvailableSlotsInCacheException):
            book_time_slot(book_request)

    @patch('app.services.booking_service.get_calendar')
    def test_double_booking_prevention(self, mock_get_calendar):
        """Test prevention of double booking"""
        mock_get_calendar.return_value = self.test_calendar

        # First search to populate cache
        search_request = SearchAvailabilityRequest(
            owner=self.test_owner,
            request_date=self.test_date
        )
        search_time_slots(search_request)

        # Book the slot first time
        book_request = BookTimeSlotRequest(
            owner=self.test_owner,
            start_time=datetime(2024, 1, 15, 9, 0),
            end_time=datetime(2024, 1, 15, 10, 0),
            invitee="test_invitee"
        )

        book_time_slot(book_request)

        # Try to book the same slot again
        with self.assertRaises(NoAvailableSlotsInCacheException):
            book_time_slot(book_request)
