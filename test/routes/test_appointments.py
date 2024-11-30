import json
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask

from app.constans import constants
from app.routes.appointments import bp
from app.models.models import calendars, Calendar


class TestAppointmentsRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = Flask(__name__)
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

        # Clear calendars before each test
        calendars.clear()

        # Set up test data
        self.test_owner = "test_owner"
        self.test_date = datetime.now()
        self.valid_search_payload = {
            "owner": self.test_owner,
            "request_date": self.test_date.strftime("%Y-%m-%d")
        }

        self.valid_booking_payload = {
            "owner": self.test_owner,
            "start_time": (self.test_date + timedelta(days=1)).strftime(constants.DATETIME_FORMAT),
            "end_time": (self.test_date + timedelta(days=1, hours=1)).strftime(constants.DATETIME_FORMAT),
            "invitee": "Test Customer",
        }

    def tearDown(self):
        """Clean up after each test method."""
        calendars.clear()

    @patch('app.routes.appointments.search_time_slots')
    def test_search_available_slots_success(self, mock_search):
        """Test successful search for available slots"""
        # Mock successful response
        mock_search.return_value = {
            "available_slots": [
                {
                    "start": "2024-01-15T09:00",
                    "end": "2024-01-15T10:00"
                }
            ]
        }

        response = self.client.get(
            '/search_slots',
            json=self.valid_search_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("available_slots", data)
        self.assertEqual(len(data["available_slots"]), 1)

    def test_search_available_slots_missing_fields(self):
        """Test search with missing required fields"""
        invalid_payload = {
            # missing owner
            "date": self.test_date.strftime("%Y-%m-%d")
        }

        response = self.client.get(
            '/search_slots',
            json=invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Missing required field", data["error"])

    def test_search_available_slots_invalid_date(self):
        """Test search with invalid date format"""
        invalid_payload = {
            "owner": self.test_owner,
            "date": "invalid-date"
        }

        response = self.client.get(
            '/search_slots',
            json=invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch('app.routes.appointments.search_time_slots')
    def test_search_available_slots_service_error(self, mock_search):
        """Test handling of service layer errors"""
        mock_search.side_effect = Exception("Service error")

        response = self.client.get(
            '/search_slots',
            json=self.valid_search_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "An internal server error occurred.")

    @patch('app.routes.appointments.book_time_slot')
    def test_book_time_slot_success(self, mock_book):
        """Test successful booking"""
        mock_book.return_value = {
            "message": "Booking successful",
            "appointment": self.valid_booking_payload
        }

        response = self.client.post(
            '/book_slot',
            json=self.valid_booking_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("appointment", data)

    def test_book_time_slot_empty_payload(self):
        """Test booking with empty payload"""
        response = self.client.post(
            '/book_slot',
            json={},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Request payload is empty")

    def test_book_time_slot_missing_fields(self):
        """Test booking with missing required fields"""
        invalid_payload = {
            "owner": self.test_owner,
            # missing other required fields
        }

        response = self.client.post(
            '/book_slot',
            json=invalid_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertIn("Missing required field", data["error"])

    @patch('app.routes.appointments.book_time_slot')
    def test_book_time_slot_service_error(self, mock_book):
        """Test handling of service layer errors during booking"""
        mock_book.side_effect = Exception("Service error")

        response = self.client.post(
            '/book_slot',
            json=self.valid_booking_payload,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)