import unittest
from datetime import datetime

from health.domain import (AppointmentStatus as S, AppointmentType, Clinic, InvalidStatusTransitionError,
                           Patient, TriageResult)
from health.interfaces import IAppointmentObserver
from health.patterns.factory import creator_for
from health.patterns.observer import AppointmentSubject, DoctorObserver, PatientObserver
from health.services import InMemoryNotificationService

CLOCK = lambda: datetime(2026, 10, 28, 10, 0)
ALI = Patient("p1", "Ali", 30, email="ali@mail.com")
VELI = Patient("p2", "Veli", 40)


def make_appointment(patient=ALI, clinic=Clinic.CARDIOLOGY):
    t = TriageResult(40, clinic, AppointmentType.GENERAL)
    return creator_for(t, CLOCK).book(patient, t)


class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.notifier = InMemoryNotificationService()
        self.subject = AppointmentSubject()
        self.patient_obs = PatientObserver(ALI, self.notifier)
        self.doctor_obs = DoctorObserver("dr1", "cardiology", self.notifier)
        self.subject.attach(self.patient_obs)
        self.subject.attach(self.doctor_obs)
        self.appt = make_appointment()

    def recipients(self):
        return [n.recipient for n in self.notifier.sent]

    def test_confirm_notifies_patient_and_doctor(self):
        self.subject.change_status(self.appt, S.CONFIRMED)
        self.assertEqual(self.appt.status, S.CONFIRMED)
        self.assertCountEqual(self.recipients(), ["ali@mail.com", "dr1"])

    def test_completed_notifies_only_patient(self):
        self.subject.change_status(self.appt, S.CONFIRMED)
        self.notifier._sent.clear()
        self.subject.change_status(self.appt, S.COMPLETED)
        self.assertEqual(self.recipients(), ["ali@mail.com"])

    def test_patient_ignores_other_patients_events(self):
        other = make_appointment(VELI)
        self.subject.change_status(other, S.CONFIRMED)
        self.assertNotIn("ali@mail.com", self.recipients())

    def test_doctor_ignores_other_clinics(self):
        other = make_appointment(ALI, Clinic.NEUROLOGY)
        self.subject.change_status(other, S.CONFIRMED)
        self.assertNotIn("dr1", self.recipients())

    def test_detach_stops_notifications(self):
        self.subject.detach(self.doctor_obs)
        self.subject.change_status(self.appt, S.CONFIRMED)
        self.assertEqual(self.recipients(), ["ali@mail.com"])

    def test_attach_is_idempotent(self):
        self.subject.attach(self.patient_obs)
        self.subject.change_status(self.appt, S.CONFIRMED)
        self.assertEqual(self.recipients().count("ali@mail.com"), 1)

    def test_invalid_transition_rejected_without_notification(self):
        with self.assertRaises(InvalidStatusTransitionError):
            self.subject.change_status(self.appt, S.COMPLETED)   # PENDING -> COMPLETED yok
        self.assertEqual(self.appt.status, S.PENDING)
        self.assertEqual(self.notifier.sent, ())

    def test_terminal_state_cannot_change(self):
        self.subject.change_status(self.appt, S.CANCELLED)
        with self.assertRaises(InvalidStatusTransitionError):
            self.subject.change_status(self.appt, S.CONFIRMED)

    def test_failing_observer_does_not_block_others(self):
        class Broken(IAppointmentObserver):
            def update(self, event):
                raise RuntimeError("boom")
        broken = Broken()
        fresh = AppointmentSubject()
        fresh.attach(broken)
        fresh.attach(self.patient_obs)
        fresh.change_status(self.appt, S.CONFIRMED)
        self.assertEqual(self.recipients(), ["ali@mail.com"])
        self.assertEqual(len(fresh.failures), 1)
        self.assertIs(fresh.failures[0][0], broken)

    def test_message_contains_appointment_info(self):
        self.subject.change_status(self.appt, S.CONFIRMED, message="Lütfen 10 dk erken geliniz")
        text = self.notifier.sent[0].message
        self.assertIn(self.appt.appointment_id, text)
        self.assertIn("erken", text)


if __name__ == "__main__":
    unittest.main()
