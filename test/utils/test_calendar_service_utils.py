import unittest
from datetime import datetime, time

from app.models.models import AvailabilityRule
from app.utils.calendar_service_utils import is_rules_overlapping


class TestRulesOverlapping(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.base_date = datetime(2024, 1, 15)
        self.base_rule = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

    def test_exact_same_rules(self):
        """Test rules that are exactly the same"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_completely_different_dates(self):
        """Test rules with non-overlapping dates"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 2, 1),
            end_date=datetime(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.assertFalse(is_rules_overlapping(rule1, rule2))

    def test_completely_different_times(self):
        """Test rules with same dates but non-overlapping times"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(17, 0),  # Starts when rule1 ends
            end_time=time(22, 0)
        )

        self.assertFalse(is_rules_overlapping(rule1, rule2))

    def test_overlapping_dates_different_times(self):
        """Test rules with overlapping dates but different times"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 1, 20),  # Overlaps with rule1
            end_date=datetime(2024, 2, 15),
            start_time=time(17, 0),  # Doesn't overlap with rule1 times
            end_time=time(22, 0)
        )

        self.assertFalse(is_rules_overlapping(rule1, rule2))

    def test_different_dates_overlapping_times(self):
        """Test rules with different dates but overlapping times"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 2, 1),  # Different from rule1
            end_date=datetime(2024, 2, 15),
            start_time=time(10, 0),  # Would overlap with rule1 if dates overlapped
            end_time=time(16, 0)
        )

        self.assertFalse(is_rules_overlapping(rule1, rule2))

    def test_partial_date_overlap(self):
        """Test rules with partially overlapping dates"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 1, 20),
            end_date=datetime(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_partial_time_overlap(self):
        """Test rules with partially overlapping times"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(13, 0),  # Overlaps with rule1
            end_time=time(19, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_contained_dates(self):
        """Test rules where one date range contains the other"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 1, 20),  # Inside rule1's date range
            end_date=datetime(2024, 1, 25),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_contained_times(self):
        """Test rules where one time range contains the other"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(11, 0),  # Inside rule1's time range
            end_time=time(15, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_touching_dates(self):
        """Test rules with touching but not overlapping dates"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=datetime(2024, 1, 31),  # Starts on rule1's end date
            end_date=datetime(2024, 2, 15),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.assertTrue(is_rules_overlapping(rule1, rule2))

    def test_touching_times(self):
        """Test rules with touching but not overlapping times"""
        rule1 = self.base_rule
        rule2 = AvailabilityRule(
            start_date=self.base_date,
            end_date=datetime(2024, 1, 31),
            start_time=time(17, 0),  # Starts exactly when rule1 ends
            end_time=time(22, 0)
        )

        self.assertFalse(is_rules_overlapping(rule1, rule2))

    def test_edge_cases(self):
        """Test various edge cases"""
        test_cases = [
            # Single day rules
            (
                AvailabilityRule(
                    start_date=self.base_date,
                    end_date=self.base_date,
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                ),
                AvailabilityRule(
                    start_date=self.base_date,
                    end_date=self.base_date,
                    start_time=time(13, 0),
                    end_time=time(19, 0)
                ),
                True  # Should overlap
            ),
            # Midnight spanning rules
            (
                AvailabilityRule(
                    start_date=self.base_date,
                    end_date=self.base_date,
                    start_time=time(22, 0),
                    end_time=time(23, 59)
                ),
                AvailabilityRule(
                    start_date=datetime(2024, 1, 16),
                    end_date=datetime(2024, 1, 16),
                    start_time=time(0, 0),
                    end_time=time(2, 0)
                ),
                False  # Should not overlap
            )
        ]

        for rule1, rule2, expected in test_cases:
            result = is_rules_overlapping(rule1, rule2)
            self.assertEqual(result, expected)