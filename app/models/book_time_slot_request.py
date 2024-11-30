from dataclasses import dataclass
from datetime import datetime


@dataclass
class BookTimeSlotRequest:
    owner: str
    invitee: str
    start_time: datetime
    end_time: datetime
