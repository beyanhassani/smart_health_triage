import unittest
from datetime import datetime

from health.app import create_default_system
from health.domain import (AccessDeniedError, AppointmentNotFoundError, AppointmentType, Clinic,
                           Complaint, InvalidStatusTransitionError, MedicalRecordData, Patient, Role, User)
from health.services import KeywordTriageEngine

CLOCK = lambda: datetime(2026, 10, 28, 10, 0)     # Çarşamba
ALI = Patient("p1", "Ali", 30, email="ali@mail.com")


class KeywordTriageTests(unittest.TestCase):
    def setUp(self):
        self.engine = KeywordTriageEngine()

    def assess(self, text):
        return self.engine.assess(Complaint("p1", text))

    def test_critical_goes_to_emergency(self):
        r = self.assess("Göğüs ağrısı ve nefes darlığı var")
        self.assertEqual(r.appointment_type, AppointmentType.EMERGENCY)
        self.assertGreaterEqual(r.severity_score, 90)

    def test_critical_has_priority_over_clinic_keywords(self):
        self.assertEqual(self.assess("kalp krizi gibi").clinic, Clinic.EMERGENCY)

    def test_clinic_routing(self):
        self.assertEqual(self.assess("sürekli migren oluyor").clinic, Clinic.NEUROLOGY)
        self.assertEqual(self.assess("cildimde kaşıntı").clinic, Clinic.DERMATOLOGY)

    def test_routine_goes_online(self):
        self.assertEqual(self.assess("reçete yenilemek istiyorum").appointment_type, AppointmentType.ONLINE)

    def test_default_is_general_internal(self):
        r = self.assess("kendimi yorgun hissediyorum")
        self.assertEqual((r.clinic, r.appointment_type), (Clinic.INTERNAL_MEDICINE, AppointmentType.GENERAL))


class FacadeTests(unittest.TestCase):
    def setUp(self):
        self.facade, self.notifier = create_default_system(CLOCK)
        self.facade.register_doctor("dr_cardio", Clinic.CARDIOLOGY)
        self.facade.register_doctor("dr_er", Clinic.EMERGENCY)

    def recipients(self):
        return [n.recipient for n in self.notifier.sent]

    def test_emergency_flow_end_to_end(self):
        appt = self.facade.request_appointment(ALI, "Şiddetli göğüs ağrısı")
        self.assertEqual(appt.appointment_type, AppointmentType.EMERGENCY)
        self.assertEqual(appt.scheduled_at, CLOCK())
        self.assertEqual(self.recipients(), ["ali@mail.com"])      # talep alındı bildirimi
        self.facade.confirm_appointment(appt.appointment_id)
        self.assertCountEqual(self.recipients(), ["ali@mail.com", "ali@mail.com", "dr_er"])

    def test_general_flow_notifies_matching_doctor_only(self):
        appt = self.facade.request_appointment(ALI, "kalp çarpıntısı var")
        self.facade.confirm_appointment(appt.appointment_id)
        self.assertIn("dr_cardio", self.recipients())
        self.assertNotIn("dr_er", self.recipients())

    def test_cancel_and_complete(self):
        a = self.facade.request_appointment(ALI, "diz ağrısı")
        self.facade.cancel_appointment(a.appointment_id, "mazeret")
        with self.assertRaises(InvalidStatusTransitionError):
            self.facade.complete_appointment(a.appointment_id)

    def test_unknown_appointment(self):
        with self.assertRaises(AppointmentNotFoundError):
            self.facade.confirm_appointment("yok")

    def test_patient_observer_attached_once(self):
        self.facade.request_appointment(ALI, "diz ağrısı")
        a = self.facade.request_appointment(ALI, "kalp çarpıntısı")
        self.notifier._sent.clear()
        self.facade.confirm_appointment(a.appointment_id)
        self.assertEqual(self.recipients().count("ali@mail.com"), 1)

    def test_medical_record_goes_through_proxy_rbac(self):
        self.facade.add_medical_record(MedicalRecordData("p1", diagnoses=("astım",)))
        self.assertEqual(self.facade.read_medical_record(User("d1", Role.DOCTOR), "p1").diagnoses, ("astım",))
        with self.assertRaises(AccessDeniedError):
            self.facade.read_medical_record(User("p2", Role.PATIENT), "p1")
        with self.assertRaises(LookupError):
            self.facade.read_medical_record(User("d1", Role.DOCTOR), "yok")

    def test_empty_complaint_rejected(self):
        with self.assertRaises(ValueError):
            self.facade.request_appointment(ALI, "  ")


if __name__ == "__main__":
    unittest.main()
