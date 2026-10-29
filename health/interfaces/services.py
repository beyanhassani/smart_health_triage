"""Facade'ın arkasında gizlenen alt sistem sözleşmeleri."""
from __future__ import annotations

from typing import Protocol

from ..domain import AppointmentStatus, Complaint, TriageResult
from .appointment import Appointment


# Kalıp: Facade | Rol: Subsystem arayüzü
class ITriageEngine(Protocol):
    def assess(self, complaint: Complaint) -> TriageResult: ...


# Kalıp: Facade | Rol: Subsystem arayüzü
class IAppointmentService(Protocol):
    def schedule(self, appointment: Appointment) -> None: ...

    def change_status(self, appointment_id: str, new_status: AppointmentStatus,
                      message: str = "") -> None: ...

    def get(self, appointment_id: str) -> Appointment: ...


# Kalıp: Facade | Rol: Subsystem arayüzü
class INotificationService(Protocol):
    def send(self, recipient: str, message: str) -> None: ...
