import json
import unittest
from unittest.mock import patch

from flask import Flask

from app.models.models import Calendar, AvailabilityRule, calendars
from app.routes.calendar import bp

class TestCalendarRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create Flask test app
        self.app = Flask(__name__)
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

        # Clear calendars before each test
        calendars.clear()

        # Set up test data
        self.test_owner = "test_owner"
        self.valid_availability_data = {
            "availability_rules": [
                {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            ]
        }

    def tearDown(self):
        """Clean up after each test method."""
        calendars.clear()

    def test_set_calendar_availability_success(self):
        """Test successful availability setting"""
        response = self.client.post(
            f'/set_availability/{self.test_owner}',
            json=self.valid_availability_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn("message", data)
        self.assertIn("new_slots", data)
        self.assertIn(self.test_owner, calendars)

    def test_set_calendar_availability_invalid_json(self):
        """Test setting availability with invalid JSON"""
        response = self.client.post(
            f'/set_availability/{self.test_owner}',
            data="invalid json",
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_set_calendar_availability_missing_fields(self):
        """Test setting availability with missing required fields"""
        invalid_data = {
            "owner": self.test_owner
            # missing availability_rules
        }

        response = self.client.post(
            f'/set_availability/{self.test_owner}',
            json=invalid_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_set_calendar_availability_invalid_dates(self):
        """Test setting availability with invalid date formats"""
        invalid_data = {
            "owner": self.test_owner,
            "availability_rules": [
                {
                    "start_date": "2024/01/01",  # invalid format
                    "end_date": "2024-12-31",
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            ]
        }

        response = self.client.post(
            f'/set_availability/{self.test_owner}',
            json=invalid_data,
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_list_upcoming_appointments_success(self):
        """Test successful retrieval of upcoming appointments"""
        # Set up a calendar with appointments
        calendar = Calendar(owner=self.test_owner)
        calendars[self.test_owner] = calendar

        # Mock the service function
        mock_appointments = [
            {
                "start": "2024-01-15 09:00",
                "end": "2024-01-15 10:00",
                "customer": "Test Customer",
                "service": "Test Service"
            }
        ]

        with patch('app.routes.calendar.list_upcoming_appointments_for_owner',
                   return_value=mock_appointments):
            response = self.client.get(
                '/appointments/list_upcoming',
                query_string={'owner': self.test_owner}
            )

            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn("upcoming_appointments", data)
            self.assertEqual(len(data["upcoming_appointments"]), 1)

    def test_list_upcoming_appointments_missing_owner(self):
        """Test listing appointments without owner parameter"""
        response = self.client.get('/appointments/list_upcoming')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Owner parameter is required")

    def test_list_upcoming_appointments_owner_not_found(self):
        """Test listing appointments for non-existent owner"""
        response = self.client.get(
            '/appointments/list_upcoming',
            query_string={'owner': 'non_existent_owner'}
        )

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn("error", data)
        self.assertEqual(data["error"], "Calendar owner not found")

    def test_list_upcoming_appointments_service_error(self):
        """Test handling of service errors"""
        # Set up a calendar
        calendar = Calendar(owner=self.test_owner)
        calendars[self.test_owner] = calendar

        # Mock service error
        with patch('app.routes.calendar.list_upcoming_appointments_for_owner',
                   side_effect=Exception("Service error")):
            response = self.client.get(
                '/appointments/list_upcoming',
                query_string={'owner': self.test_owner}
            )

            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Service error")
