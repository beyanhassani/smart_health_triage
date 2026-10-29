"""Facade kalıbı.

İstemci (arayüz/demo) tek bir giriş noktasıyla konuşur. Arkada şu zincir gizlenir:
şikâyet -> triage -> doğru Creator'ın seçimi -> randevu üretimi -> kayıt ->
gözlemci kaydı -> ilk bildirim. Alt sistemler soyutlamalarla (Protocol/ABC)
enjekte edilir; Facade somut servis sınıflarını bilmez.
"""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from ...domain import (Clinic, Complaint, AppointmentStatus, MedicalRecordData, Patient, User)
from ...interfaces import (Appointment, IAppointmentService, IAppointmentSubject, IMedicalRecord,
                           INotificationService, ITriageEngine)
from ..factory import creator_for
from ..observer import DoctorObserver, PatientObserver
from ..proxy import MedicalRecordProxy, RealMedicalRecord


# Kalıp: Facade | Rol: Facade
class HealthSystemFacade:
    def __init__(self, triage: ITriageEngine, appointments: IAppointmentService,
                 notifier: INotificationService, subject: IAppointmentSubject,
                 clock: Callable[[], datetime] = datetime.now) -> None:
        self._triage = triage
        self._appointments = appointments
        self._notifier = notifier
        self._subject = subject
        self._clock = clock
        self._records: dict[str, IMedicalRecord] = {}
        self._observed_patients: set[str] = set()

    # --- Kurulum ---------------------------------------------------------
    def register_doctor(self, doctor_id: str, clinic: Clinic) -> None:
        self._subject.attach(DoctorObserver(doctor_id, clinic.value, self._notifier))

    def add_medical_record(self, data: MedicalRecordData) -> None:
        # Gerçek kayıt Proxy'nin arkasında, ilk yetkili erişimde yüklenir.
        self._records[data.patient_id] = MedicalRecordProxy(
            data.patient_id, lambda: RealMedicalRecord(data))

    # --- İstemcinin kullandığı basit işlemler ----------------------------
    def request_appointment(self, patient: Patient, complaint_text: str) -> Appointment:
        complaint = Complaint(patient.patient_id, complaint_text)
        triage = self._triage.assess(complaint)
        appointment = creator_for(triage, self._clock).book(patient, triage)
        self._appointments.schedule(appointment)
        self._observe(patient)
        self._notifier.send(patient.email or patient.patient_id,
                            f"Sayın {patient.name}, randevu talebiniz alındı: {appointment.describe()}")
        return appointment

    def confirm_appointment(self, appointment_id: str, message: str = "") -> None:
        self._appointments.change_status(appointment_id, AppointmentStatus.CONFIRMED, message)

    def cancel_appointment(self, appointment_id: str, reason: str = "") -> None:
        self._appointments.change_status(appointment_id, AppointmentStatus.CANCELLED, reason)

    def complete_appointment(self, appointment_id: str) -> None:
        self._appointments.change_status(appointment_id, AppointmentStatus.COMPLETED)

    def read_medical_record(self, user: User, patient_id: str) -> MedicalRecordData:
        record = self._records.get(patient_id)
        if record is None:
            raise LookupError(f"tıbbi kayıt bulunamadı: {patient_id}")
        return record.read(user)

    # --- İç yardımcı -----------------------------------------------------
    def _observe(self, patient: Patient) -> None:
        if patient.patient_id not in self._observed_patients:
            self._subject.attach(PatientObserver(patient, self._notifier))
            self._observed_patients.add(patient.patient_id)
