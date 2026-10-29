"""Observer - Concrete Subject.

Randevu durumunu değiştiren tek yer burasıdır. Durum değişince kayıtlı tüm
gözlemcilere haber verir; gözlemcilerin kim olduğunu veya ne yaptığını bilmez
(yalnızca IAppointmentObserver soyutlamasına bağlıdır).
"""
from __future__ import annotations

from ...domain import (AppointmentEvent, AppointmentStatus, InvalidStatusTransitionError)
from ...interfaces import Appointment, IAppointmentObserver, IAppointmentSubject

# Geçerli durum geçişleri. COMPLETED ve CANCELLED son durumlardır.
_ALLOWED_TRANSITIONS: dict[AppointmentStatus, frozenset[AppointmentStatus]] = {
    AppointmentStatus.PENDING: frozenset({AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED}),
    AppointmentStatus.CONFIRMED: frozenset({AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED}),
    AppointmentStatus.CANCELLED: frozenset(),
    AppointmentStatus.COMPLETED: frozenset(),
}


# Kalıp: Observer | Rol: ConcreteSubject
class AppointmentSubject(IAppointmentSubject):
    def __init__(self) -> None:
        self._observers: list[IAppointmentObserver] = []
        self._failures: list[tuple[IAppointmentObserver, Exception]] = []

    def attach(self, observer: IAppointmentObserver) -> None:
        if observer not in self._observers:      # aynı gözlemci iki kez eklenmez
            self._observers.append(observer)

    def detach(self, observer: IAppointmentObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, event: AppointmentEvent) -> None:
        for observer in list(self._observers):   # kopya: döngü sırasında detach güvenli olsun
            try:
                observer.update(event)
            except Exception as exc:             # bir gözlemcinin hatası diğerlerini engellemesin
                self._failures.append((observer, exc))

    @property
    def failures(self) -> tuple[tuple[IAppointmentObserver, Exception], ...]:
        return tuple(self._failures)

    def change_status(self, appointment: Appointment, new_status: AppointmentStatus,
                      message: str = "") -> None:
        old_status = appointment.status
        if new_status not in _ALLOWED_TRANSITIONS[old_status]:
            raise InvalidStatusTransitionError(
                f"{old_status.value} -> {new_status.value} geçişine izin verilmiyor")
        appointment.status = new_status
        self.notify(AppointmentEvent(
            appointment_id=appointment.appointment_id,
            patient_id=appointment.patient.patient_id,
            old_status=old_status,
            new_status=new_status,
            clinic_name=appointment.clinic_name,
            message=message,
        ))
