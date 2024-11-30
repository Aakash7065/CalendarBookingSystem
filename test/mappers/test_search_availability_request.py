import unittest

from app.mappers.search_availability_request import map_to_search_availability_request
from app.models.search_available_request import SearchAvailabilityRequest
from app.utils.datetime_utils import parse_date


class TestSearchAvailabilityRequestMapper(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.valid_data = {
            "owner": "test_owner",
            "request_date": "2024-01-15"
        }

    def test_valid_mapping(self):
        """Test mapping with valid data"""
        result = map_to_search_availability_request(self.valid_data)

        self.assertIsInstance(result, SearchAvailabilityRequest)
        self.assertEqual(result.owner, "test_owner")
        self.assertEqual(
            result.request_date,
            parse_date("2024-01-15")
        )

    def test_missing_owner(self):
        """Test mapping with missing owner field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("owner")

        with self.assertRaises(KeyError) as context:
            map_to_search_availability_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("owner", str(context.exception))

    def test_missing_request_date(self):
        """Test mapping with missing request_date field"""
        invalid_data = self.valid_data.copy()
        invalid_data.pop("request_date")

        with self.assertRaises(KeyError) as context:
            map_to_search_availability_request(invalid_data)

        self.assertIn("Missing required field", str(context.exception))
        self.assertIn("request_date", str(context.exception))

    def test_invalid_date_format(self):
        """Test mapping with invalid date format"""
        invalid_data = self.valid_data.copy()
        invalid_data["request_date"] = "2024/01/15"  # Invalid format

        with self.assertRaises(ValueError) as context:
            map_to_search_availability_request(invalid_data)

        self.assertIn("Invalid date format", str(context.exception))

    def test_empty_fields(self):
        """Test mapping with empty field values"""
        invalid_data = {
            "owner": "",
            "request_date": "2024-01-15"
        }

        with self.assertRaises(ValueError) as context:
            map_to_search_availability_request(invalid_data)
        self.assertIn("owner field is required", str(context.exception))

    def test_extra_fields(self):
        """Test mapping with extra fields in input"""
        data_with_extra = self.valid_data.copy()
        data_with_extra["extra_field"] = "extra_value"

        result = map_to_search_availability_request(data_with_extra)
        self.assertIsInstance(result, SearchAvailabilityRequest)
        # Extra field should be ignored
        self.assertFalse(hasattr(result, "extra_field"))

    def test_none_values(self):
        """Test mapping with None values"""
        invalid_data = {
            "owner": None,
            "request_date": "2024-01-15"
        }

        with self.assertRaises(ValueError):
            map_to_search_availability_request(invalid_data)

    def test_date_edge_cases(self):
        """Test various date edge cases"""
        test_cases = [
            # Year boundary
            {
                "data": {
                    "owner": "test_owner",
                    "request_date": "2024-12-31"
                },
                "should_succeed": True
            },
            # Year start
            {
                "data": {
                    "owner": "test_owner",
                    "request_date": "2024-01-01"
                },
                "should_succeed": True
            },
            # Invalid month
            {
                "data": {
                    "owner": "test_owner",
                    "request_date": "2024-13-01"
                },
                "should_succeed": False
            },
            # Invalid day
            {
                "data": {
                    "owner": "test_owner",
                    "request_date": "2024-04-31"
                },
                "should_succeed": False
            },
            # Leap year
            {
                "data": {
                    "owner": "test_owner",
                    "request_date": "2024-02-29"
                },
                "should_succeed": True
            }
        ]

        for test_case in test_cases:
            if test_case["should_succeed"]:
                result = map_to_search_availability_request(test_case["data"])
                self.assertIsInstance(result, SearchAvailabilityRequest)
            else:
                with self.assertRaises((ValueError, KeyError)):
                    map_to_search_availability_request(test_case["data"])