"""Factory Method - Concrete Product'lar.

Üç randevu türü yalnızca etiketle değil, davranışla da farklıdır:
öncelik, süre ve açıklama (describe) her tür için ayrı tanımlanır.
"""
from __future__ import annotations

from datetime import datetime

from ...domain import AppointmentType, Patient
from ...interfaces import Appointment


# Kalıp: Factory Method | Rol: ConcreteProduct
class EmergencyAppointment(Appointment):
    """Acil randevu: en yüksek öncelik, en uzun muayene süresi, sıra beklemez."""

    @property
    def appointment_type(self) -> AppointmentType:
        return AppointmentType.EMERGENCY

    @property
    def priority(self) -> int:
        return 0

    @property
    def duration_minutes(self) -> int:
        return 45

    def describe(self) -> str:
        return (f"[ACİL] {self.patient.name} - {self.clinic_name} - "
                f"hemen ({self.scheduled_at:%H:%M})")


# Kalıp: Factory Method | Rol: ConcreteProduct
class GeneralAppointment(Appointment):
    """Genel randevu: sıradaki ilk uygun iş gününe planlanır."""

    @property
    def appointment_type(self) -> AppointmentType:
        return AppointmentType.GENERAL

    @property
    def priority(self) -> int:
        return 2

    @property
    def duration_minutes(self) -> int:
        return 20

    def describe(self) -> str:
        return (f"[GENEL] {self.patient.name} - {self.clinic_name} - "
                f"{self.scheduled_at:%d.%m.%Y %H:%M}")


# Kalıp: Factory Method | Rol: ConcreteProduct
class OnlineAppointment(Appointment):
    """Online randevu: fiziksel gitmek gerekmez, görüşme bağlantısı vardır."""

    def __init__(self, appointment_id: str, patient: Patient, clinic_name: str,
                 scheduled_at: datetime, meeting_link: str) -> None:
        super().__init__(appointment_id, patient, clinic_name, scheduled_at)
        self.meeting_link = meeting_link

    @property
    def appointment_type(self) -> AppointmentType:
        return AppointmentType.ONLINE

    @property
    def priority(self) -> int:
        return 3

    @property
    def duration_minutes(self) -> int:
        return 15

    def describe(self) -> str:
        return (f"[ONLINE] {self.patient.name} - {self.clinic_name} - "
                f"{self.scheduled_at:%d.%m.%Y %H:%M} - {self.meeting_link}")
