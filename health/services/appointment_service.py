"""Randevu alt sistemi (Facade'ın arkasındaki servislerden biri)."""
from __future__ import annotations

from ..domain import AppointmentNotFoundError, AppointmentStatus
from ..interfaces import Appointment, IAppointmentService, IAppointmentSubject


# Kalıp: Facade | Rol: Subsystem (AppointmentService)
class AppointmentService(IAppointmentService):
    def __init__(self, subject: IAppointmentSubject) -> None:
        self._subject = subject
        self._appointments: dict[str, Appointment] = {}

    def schedule(self, appointment: Appointment) -> None:
        self._appointments[appointment.appointment_id] = appointment

    def get(self, appointment_id: str) -> Appointment:
        try:
            return self._appointments[appointment_id]
        except KeyError:
            raise AppointmentNotFoundError(f"randevu bulunamadı: {appointment_id}") from None

    def change_status(self, appointment_id: str, new_status: AppointmentStatus,
                      message: str = "") -> None:
        self._subject.change_status(self.get(appointment_id), new_status, message)
