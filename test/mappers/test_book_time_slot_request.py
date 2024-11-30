import unittest

from app.constans import constants
from app.mappers.book_time_slot_request import map_to_book_time_slot_request
from app.models.book_time_slot_request import BookTimeSlotRequest
from app.utils.datetime_utils import parse_date


class TestBookTimeSlotRequestMapper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.valid_data = {
            "owner": "test_owner",
            "invitee": "test_invitee",
            "start_time": "2024-01-15T09:00",
            "end_time": "2024-01-15T10:00"
        }

    def test_valid_mapping(self):
        """Test mapping with valid data"""
        result = map_to_book_time_slot_request(self.valid_data)

        self.assertIsInstance(result, BookTimeSlotRequest)
        self.assertEqual(result.owner, "test_owner")
        self.assertEqual(result.invitee, "test_invitee")
        self.assertEqual(
            result.start_time,
            parse_date("2024-01-15T09:00", constants.DATETIME_FORMAT)
        )
        self.assertEqual(
            result.end_time,
            parse_date("2024-01-15T10:00", constants.DATETIME_FORMAT)
        )

    def test_missing_owner(self):
        """Test mapping with missing owner field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("owner")

        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("owner", str(context.exception))

    def test_missing_invitee(self):
        """Test mapping with missing invitee field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("invitee")

        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("invitee", str(context.exception))

    def test_missing_start_time(self):
        """Test mapping with missing start_time field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("start_time")

        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("start_time", str(context.exception))

    def test_missing_end_time(self):
        """Test mapping with missing end_time field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("end_time")

        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("end_time", str(context.exception))

    def test_invalid_datetime_format(self):
        """Test mapping with invalid datetime format"""
        invalid_data = self.valid_data.copy()
        invalid_data["start_time"] = "2024/01/15 09:00"  # Invalid format

        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)

        self.assertIn("Invalid date format", str(context.exception))

    def test_empty_fields(self):
        """Test mapping with empty field values"""
        invalid_data = {
            "owner": "",
            "invitee": "",
            "start_time": "2024-01-15T09:00",
            "end_time": "2024-01-15T10:00"
        }
        with self.assertRaises(ValueError) as context:
            map_to_book_time_slot_request(invalid_data)


    def test_extra_fields(self):
        """Test mapping with extra fields in input"""
        data_with_extra = self.valid_data.copy()
        data_with_extra["extra_field"] = "extra_value"

        result = map_to_book_time_slot_request(data_with_extra)
        self.assertIsInstance(result, BookTimeSlotRequest)
        # Extra field should be ignored
        self.assertFalse(hasattr(result, "extra_field"))

    def test_none_values(self):
        """Test mapping with None values"""
        invalid_data = {
            "owner": None,
            "invitee": None,
            "start_time": "2024-01-15T09:00",
            "end_time": "2024-01-15T10:00"
        }

        with self.assertRaises(ValueError):
            map_to_book_time_slot_request(invalid_data)

    def test_invalid_date_range(self):
        """Test mapping with end time before start time"""
        invalid_data = self.valid_data.copy()
        invalid_data["start_time"] = "2024-01-15T10:00"
        invalid_data["end_time"] = "2024-01-15T09:00"

        with self.assertRaises(ValueError):
            map_to_book_time_slot_request(invalid_data)

    def test_different_dates(self):
        """Test mapping with different dates"""
        valid_data = self.valid_data.copy()
        valid_data["start_time"] = "2024-01-15T09:00"
        valid_data["end_time"] = "2024-01-16T09:00"

        result = map_to_book_time_slot_request(valid_data)
        self.assertIsInstance(result, BookTimeSlotRequest)
        self.assertNotEqual(result.start_time.date(), result.end_time.date())

    def test_edge_cases(self):
        """Test various edge cases"""
        test_cases = [
            # Midnight booking
            {
                "data": {
                    "owner": "test_owner",
                    "invitee": "test_invitee",
                    "start_time": "2024-01-15T00:00",
                    "end_time": "2024-01-15T01:00"
                },
                "should_succeed": True
            },
            # Last minute of day
            {
                "data": {
                    "owner": "test_owner",
                    "invitee": "test_invitee",
                    "start_time": "2024-01-15T23:59",
                    "end_time": "2024-01-16T00:59"
                },
                "should_succeed": True
            }
        ]

        for test_case in test_cases:
            if test_case["should_succeed"]:
                result = map_to_book_time_slot_request(test_case["data"])
                self.assertIsInstance(result, BookTimeSlotRequest)
            else:
                with self.assertRaises(ValueError):
                    map_to_book_time_slot_request(test_case["data"])
