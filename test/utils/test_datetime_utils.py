import unittest
from datetime import datetime, time

from app.utils.datetime_utils import parse_date, parse_time


class TestDateTimeParsing(unittest.TestCase):

    # Tests for parse_date
    def test_valid_date(self):
        """Test parsing a valid date."""
        self.assertEqual(parse_date("2024-11-30"), datetime(2024, 11, 30))

    def test_valid_date_with_custom_format(self):
        """Test parsing a valid date with a custom format."""
        self.assertEqual(parse_date("30-11-2024", "%d-%m-%Y"), datetime(2024, 11, 30))

    def test_invalid_date_format(self):
        """Test handling an invalid date format."""
        with self.assertRaises(ValueError) as context:
            parse_date("30/11/2024")
        self.assertIn("expected '%Y-%m-%d'", str(context.exception))

    def test_invalid_date_value(self):
        """Test handling an invalid date value."""
        with self.assertRaises(ValueError) as context:
            parse_date("2024-13-01")
        self.assertIn("Invalid date format", str(context.exception))

    # Tests for parse_time
    def test_valid_time(self):
        """Test parsing a valid time."""
        self.assertEqual(parse_time("14:30"), time(14, 30))

    def test_invalid_time_format_length(self):
        """Test handling an invalid time format with incorrect length."""
        with self.assertRaises(ValueError) as context:
            parse_time("9:30")  # Missing leading zero
        self.assertIn("Invalid time format", str(context.exception))

    def test_invalid_time_format_separator(self):
        """Test handling an invalid time format with the wrong separator."""
        with self.assertRaises(ValueError) as context:
            parse_time("14-30")  # Wrong separator
        self.assertIn("Invalid time format", str(context.exception))

    def test_invalid_time_value(self):
        """Test handling an invalid time value."""
        with self.assertRaises(ValueError) as context:
            parse_time("25:01")  # Invalid hour
        self.assertIn("Invalid time format", str(context.exception))

    def test_invalid_minute_value(self):
        """Test handling an invalid minute value."""
        with self.assertRaises(ValueError) as context:
            parse_time("14:60")  # Invalid minute
        self.assertIn("Invalid time format", str(context.exception))