"""Factory Method rolleri: Product (Appointment) ve Creator (AppointmentCreator)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from ..domain import AppointmentStatus, AppointmentType, Patient, TriageResult


# Kalıp: Factory Method | Rol: Product
class Appointment(ABC):
    """Product. Somut ürünler yalnızca etiketle değil, davranışla da farklılaşır."""

    def __init__(self, appointment_id: str, patient: Patient, clinic_name: str,
                 scheduled_at: datetime) -> None:
        self.appointment_id = appointment_id
        self.patient = patient
        self.clinic_name = clinic_name
        self.scheduled_at = scheduled_at
        self.status = AppointmentStatus.PENDING

    @property
    @abstractmethod
    def appointment_type(self) -> AppointmentType: ...

    @property
    @abstractmethod
    def priority(self) -> int:
        """Küçük sayı = önce hizmet alır."""

    @property
    @abstractmethod
    def duration_minutes(self) -> int: ...

    @abstractmethod
    def describe(self) -> str: ...


# Kalıp: Factory Method | Rol: Creator
class AppointmentCreator(ABC):
    """Creator. Hangi Appointment'ın üretileceğine alt sınıflar karar verir (factory method)."""

    @abstractmethod
    def create_appointment(self, patient: Patient, triage: TriageResult) -> Appointment:
        """Factory method."""

    def book(self, patient: Patient, triage: TriageResult) -> Appointment:
        """Ürün sınıfını bilmeden factory method'u kullanan ortak iş akışı."""
        appointment = self.create_appointment(patient, triage)
        if appointment.patient.patient_id != patient.patient_id:
            raise ValueError("fabrika başka bir hasta için randevu üretti")
        return appointment
