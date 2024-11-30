from app.models.models import AvailabilityRule


def is_rules_overlapping(rule1: AvailabilityRule, rule2: AvailabilityRule) -> bool:
    """
    Check if two availability rules overlap in both date and time ranges.

    Args:
        rule1 (AvailabilityRule): First rule to compare
        rule2 (AvailabilityRule): Second rule to compare

    Returns:
        bool: True if rules overlap, False otherwise
    """
    # Check if date ranges overlap
    dates_overlap = (
            rule1.start_date <= rule2.end_date and
            rule2.start_date <= rule1.end_date
    )

    if not dates_overlap:
        return False

    # If dates overlap, check if times overlap
    times_overlap = (
            rule1.start_time < rule2.end_time and
            rule2.start_time < rule1.end_time
    )

    return times_overlap