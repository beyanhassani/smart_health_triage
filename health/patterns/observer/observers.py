"""Observer - Concrete Observer'lar.

İki gözlemci aynı olaya FARKLI tepki verir: hasta kendi randevusunun her
değişikliğini görür; doktor yalnızca kendi kliniğini ilgilendiren, henüz
sonuçlanmamış değişiklikleri görür.
"""
from __future__ import annotations

from ...domain import AppointmentEvent, AppointmentStatus, Patient
from ...interfaces import IAppointmentObserver, INotificationService

_PATIENT_TEXT = {
    AppointmentStatus.CONFIRMED: "Randevunuz onaylandı.",
    AppointmentStatus.CANCELLED: "Randevunuz iptal edildi.",
    AppointmentStatus.COMPLETED: "Randevunuz tamamlandı. Geçmiş olsun.",
}


# Kalıp: Observer | Rol: ConcreteObserver
class PatientObserver(IAppointmentObserver):
    def __init__(self, patient: Patient, notifier: INotificationService) -> None:
        self._patient = patient
        self._notifier = notifier

    def update(self, event: AppointmentEvent) -> None:
        if event.patient_id != self._patient.patient_id:
            return                                    # başkasının randevusu
        text = _PATIENT_TEXT.get(event.new_status)
        if text is None:
            return
        message = f"Sayın {self._patient.name}, {text} (No: {event.appointment_id})"
        if event.message:
            message += f" Not: {event.message}"
        self._notifier.send(self._patient.email or self._patient.patient_id, message)


# Kalıp: Observer | Rol: ConcreteObserver
class DoctorObserver(IAppointmentObserver):
    def __init__(self, doctor_id: str, clinic_name: str, notifier: INotificationService) -> None:
        self._doctor_id = doctor_id
        self._clinic_name = clinic_name
        self._notifier = notifier

    def update(self, event: AppointmentEvent) -> None:
        if event.clinic_name != self._clinic_name:
            return                                    # başka klinik
        if event.new_status is AppointmentStatus.COMPLETED:
            return                                    # doktorun kendi bitirdiği iş için bildirim gerekmez
        message = (f"[{self._clinic_name}] Randevu {event.appointment_id}: "
                   f"{event.old_status.value} -> {event.new_status.value}")
        self._notifier.send(self._doctor_id, message)
