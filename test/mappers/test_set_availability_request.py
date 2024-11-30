import unittest
from datetime import datetime, time

from app.mappers.set_availability_request import map_to_set_availability_request
from app.models.models import AvailabilityRule
from app.models.set_availability_request import SetAvailabilityRequest


class TestSetAvailabilityRequestMapper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.valid_data = {
            "availability_rules": [
                {
                    "start_date": "2024-01-15",
                    "end_date": "2024-12-31",
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            ]
        }

    def test_valid_mapping_single_rule(self):
        """Test mapping with a single valid availability rule"""
        result = map_to_set_availability_request(self.valid_data)

        self.assertIsInstance(result, SetAvailabilityRequest)
        self.assertEqual(len(result.availability_rules), 1)

        rule = result.availability_rules[0]
        self.assertIsInstance(rule, AvailabilityRule)
        self.assertEqual(rule.start_date, datetime(2024, 1, 15))
        self.assertEqual(rule.end_date, datetime(2024, 12, 31))
        self.assertEqual(rule.start_time, time(9, 0))
        self.assertEqual(rule.end_time, time(17, 0))

    def test_valid_mapping_multiple_rules(self):
        """Test mapping with multiple valid availability rules"""
        data = {
            "availability_rules": [
                {
                    "start_date": "2024-01-15",
                    "end_date": "2024-06-30",
                    "start_time": "09:00",
                    "end_time": "17:00"
                },
                {
                    "start_date": "2024-07-01",
                    "end_date": "2024-12-31",
                    "start_time": "10:00",
                    "end_time": "18:00"
                }
            ]
        }

        result = map_to_set_availability_request(data)

        self.assertEqual(len(result.availability_rules), 2)
        self.assertEqual(result.availability_rules[0].start_time, time(9, 0))
        self.assertEqual(result.availability_rules[1].start_time, time(10, 0))

    def test_missing_availability_rules_key(self):
        """Test mapping with missing availability_rules key"""
        invalid_data = {"some_other_key": []}

        with self.assertRaises(ValueError) as context:
            map_to_set_availability_request(invalid_data)

        self.assertIn("availability_rules", str(context.exception))

    def test_empty_availability_rules(self):
        """Test mapping with empty availability rules list"""
        data = {"availability_rules": []}

        result = map_to_set_availability_request(data)
        self.assertEqual(len(result.availability_rules), 0)

    def test_missing_required_fields(self):
        """Test mapping with missing required fields in rules"""
        test_cases = [
            ("start_date", {"end_date": "2024-12-31", "start_time": "09:00", "end_time": "17:00"}),
            ("end_date", {"start_date": "2024-01-15", "start_time": "09:00", "end_time": "17:00"}),
            ("start_time", {"start_date": "2024-01-15", "end_date": "2024-12-31", "end_time": "17:00"}),
            ("end_time", {"start_date": "2024-01-15", "end_date": "2024-12-31", "start_time": "09:00"})
        ]

        for missing_field, rule_data in test_cases:
            data = {"availability_rules": [rule_data]}

            with self.assertRaises(KeyError) as context:
                map_to_set_availability_request(data)

            self.assertIn(missing_field, str(context.exception))

    def test_invalid_date_formats(self):
        """Test mapping with invalid date formats"""
        invalid_dates = [
            "2024/01/15",  # Wrong format
            "15-01-2024",  # Wrong order
            "2024-13-01",  # Invalid month
            "2024-01-32",  # Invalid day
            "invalid"  # Not a date
        ]

        for invalid_date in invalid_dates:
            data = {
                "availability_rules": [
                    {
                        "start_date": invalid_date,
                        "end_date": "2024-12-31",
                        "start_time": "09:00",
                        "end_time": "17:00"
                    }
                ]
            }

            with self.assertRaises(ValueError):
                map_to_set_availability_request(data)

    def test_invalid_time_formats(self):
        """Test mapping with invalid time formats"""
        invalid_times = [
            "9:00",  # Missing leading zero
            "09:60",  # Invalid minutes
            "24:00",  # Invalid hours
            "09-00",  # Wrong separator
            "invalid"  # Not a time
        ]

        for invalid_time in invalid_times:
            data = {
                "availability_rules": [
                    {
                        "start_date": "2024-01-15",
                        "end_date": "2024-12-31",
                        "start_time": invalid_time,
                        "end_time": "17:00"
                    }
                ]
            }

            with self.assertRaises(ValueError):
                map_to_set_availability_request(data)

    def test_non_dict_input(self):
        """Test mapping with non-dictionary input"""
        invalid_inputs = [
            None,
            [],
            "string",
            123,
            True
        ]

        for invalid_input in invalid_inputs:
            with self.assertRaises(ValueError) as context:
                map_to_set_availability_request(invalid_input)

            self.assertIn("not a dictionary", str(context.exception))

    def test_valid_edge_cases(self):
        """Test mapping with valid edge cases"""
        edge_cases = [
            # Midnight times
            {
                "availability_rules": [
                    {
                        "start_date": "2024-01-15",
                        "end_date": "2024-12-31",
                        "start_time": "00:00",
                        "end_time": "23:59"
                    }
                ]
            },
            # Same day
            {
                "availability_rules": [
                    {
                        "start_date": "2024-01-15",
                        "end_date": "2024-01-15",
                        "start_time": "09:00",
                        "end_time": "17:00"
                    }
                ]
            }
        ]

        for case in edge_cases:
            result = map_to_set_availability_request(case)
            self.assertIsInstance(result, SetAvailabilityRequest)
            self.assertEqual(len(result.availability_rules), 1)
