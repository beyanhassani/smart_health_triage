"""Factory Method - Concrete Creator'lar.

Her Creator, `create_appointment` (factory method) içinde hangi ürünün
üretileceğine ve ona özgü bilgilerin (zaman, bağlantı) nasıl hesaplanacağına karar verir.
`book()` ortak iş akışı AppointmentCreator'da olduğu için değişmez.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from typing import Callable

from ...domain import AppointmentType, Patient, TriageResult
from ...interfaces import Appointment, AppointmentCreator
from .appointments import EmergencyAppointment, GeneralAppointment, OnlineAppointment

Clock = Callable[[], datetime]


class _ClockedCreator(AppointmentCreator):
    """Yalnızca saat bağımlılığını (test edilebilirlik için enjekte edilebilir) tutan yardımcı taban."""

    def __init__(self, clock: Clock = datetime.now) -> None:
        self._clock = clock

    @staticmethod
    def _new_id() -> str:
        return uuid.uuid4().hex[:8]


# Kalıp: Factory Method | Rol: ConcreteCreator
class EmergencyAppointmentCreator(_ClockedCreator):
    def create_appointment(self, patient: Patient, triage: TriageResult) -> Appointment:
        return EmergencyAppointment(self._new_id(), patient, triage.clinic.value,
                                    scheduled_at=self._clock())  # hemen


# Kalıp: Factory Method | Rol: ConcreteCreator
class GeneralAppointmentCreator(_ClockedCreator):
    def create_appointment(self, patient: Patient, triage: TriageResult) -> Appointment:
        return GeneralAppointment(self._new_id(), patient, triage.clinic.value,
                                  scheduled_at=self._next_working_day_9am())

    def _next_working_day_9am(self) -> datetime:
        day = (self._clock() + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
        while day.weekday() >= 5:      # cumartesi (5) ve pazar (6) atlanır
            day += timedelta(days=1)
        return day


# Kalıp: Factory Method | Rol: ConcreteCreator
class OnlineAppointmentCreator(_ClockedCreator):
    def create_appointment(self, patient: Patient, triage: TriageResult) -> Appointment:
        appointment_id = self._new_id()
        link = f"https://meet.health.example/{appointment_id}"
        return OnlineAppointment(appointment_id, patient, triage.clinic.value,
                                 scheduled_at=self._clock() + timedelta(hours=2),
                                 meeting_link=link)


_CREATORS: dict[AppointmentType, type[AppointmentCreator]] = {
    AppointmentType.EMERGENCY: EmergencyAppointmentCreator,
    AppointmentType.GENERAL: GeneralAppointmentCreator,
    AppointmentType.ONLINE: OnlineAppointmentCreator,
}


def creator_for(triage: TriageResult, clock: Clock = datetime.now) -> AppointmentCreator:
    """Triage sonucuna göre doğru Creator'ı seçer."""
    return _CREATORS[triage.appointment_type](clock)
