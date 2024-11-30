from dataclasses import dataclass
from datetime import date, datetime

@dataclass
class SearchAvailabilityRequest:
    owner: str
    request_date: date