"""Observer rolleri: Subject ve Observer."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..domain import AppointmentEvent, AppointmentStatus
from .appointment import Appointment


# Kalıp: Observer | Rol: Observer
class IAppointmentObserver(ABC):
    @abstractmethod
    def update(self, event: AppointmentEvent) -> None: ...


# Kalıp: Observer | Rol: Subject
class IAppointmentSubject(ABC):
    @abstractmethod
    def attach(self, observer: IAppointmentObserver) -> None: ...

    @abstractmethod
    def detach(self, observer: IAppointmentObserver) -> None: ...

    @abstractmethod
    def notify(self, event: AppointmentEvent) -> None: ...

    @abstractmethod
    def change_status(self, appointment: "Appointment", new_status: AppointmentStatus,
                      message: str = "") -> None:
        """Durumu değiştirir ve gözlemcileri bilgilendirir."""
