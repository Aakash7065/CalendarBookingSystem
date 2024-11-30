from dataclasses import dataclass
from typing import List
from app.models.models import AvailabilityRule


@dataclass
class SetAvailabilityRequest:
    availability_rules: List[AvailabilityRule]

    def __str__(self):
        return f"SetAvailabilityRequest(availability_rules={self.availability_rules})"
