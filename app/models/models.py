from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import List, Dict

from app.constans import constants


@dataclass
class AvailabilityRule:
    start_time: time
    end_time: time
    start_date: date
    end_date: date

    def to_dict(self):
        return {
            "start_date": self.start_date.strftime(constants.DATE_FORMAT),
            "end_date": self.end_date.strftime(constants.DATE_FORMAT),
            "start_time": self.start_time.strftime(constants.TIME_FORMAT),
            "end_time": self.end_time.strftime(constants.TIME_FORMAT)
        }


@dataclass
class Appointment:
    invitee: str
    start_time: datetime
    end_time: datetime

    def to_dict(self):
        return {
            "invitee": self.invitee,
            "start_time": self.start_time.strftime(constants.DATETIME_FORMAT),
            "end_time": self.end_time.strftime(constants.DATETIME_FORMAT)
        }


@dataclass
class Calendar:
    owner: str
    availability_rules: List[AvailabilityRule] = field(default_factory=list)
    appointments: Dict[date, List[Appointment]] = field(default_factory=dict)

    def add_appointment(self, appointment: Appointment) -> bool:
        appointment_date = appointment.start_time.date()
        if appointment_date not in self.appointments:
            self.appointments[appointment_date] = []
        self.appointments[appointment_date].append(appointment)
        return True

    def get_upcoming_appointments(self) -> List[Appointment]:
        today = datetime.now().date()
        time_now = datetime.now()
        upcoming_appointments = []
        for appointment_date, appointments in self.appointments.items():
            if appointment_date >= today:
                upcoming_appointments.extend({
                                                 "invitee": appointment.invitee,
                                                 "start_time": appointment.start_time.strftime(constants.DATETIME_FORMAT),
                                                 "end_time": appointment.end_time.strftime(constants.DATETIME_FORMAT)
                                             } for appointment in appointments if appointment.start_time >= time_now)
        return upcoming_appointments


calendars = {}  # Key: owner_id, Value: Calendar instance

# Temporary cache for available slots (to be validated during booking)
available_slots_cache = {}
