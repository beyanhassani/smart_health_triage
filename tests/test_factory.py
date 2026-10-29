import unittest
from datetime import datetime

from health.domain import AppointmentType, Clinic, Patient, TriageResult
from health.interfaces import Appointment, AppointmentCreator
from health.patterns.factory import (EmergencyAppointment, EmergencyAppointmentCreator,
                                     GeneralAppointment, GeneralAppointmentCreator,
                                     OnlineAppointment, OnlineAppointmentCreator, creator_for)

FRIDAY_EVENING = datetime(2026, 10, 30, 18, 30)   # Cuma
PATIENT = Patient("p1", "Ali", 30)


def triage(kind: AppointmentType, clinic=Clinic.INTERNAL_MEDICINE, score=50.0):
    return TriageResult(score, clinic, kind)


class FactoryTests(unittest.TestCase):
    def setUp(self):
        self.clock = lambda: FRIDAY_EVENING

    def test_each_creator_builds_its_own_product(self):
        cases = [
            (EmergencyAppointmentCreator, AppointmentType.EMERGENCY, EmergencyAppointment),
            (GeneralAppointmentCreator, AppointmentType.GENERAL, GeneralAppointment),
            (OnlineAppointmentCreator, AppointmentType.ONLINE, OnlineAppointment),
        ]
        for creator_cls, kind, product_cls in cases:
            with self.subTest(kind=kind):
                appt = creator_cls(self.clock).book(PATIENT, triage(kind))
                self.assertIsInstance(appt, product_cls)
                self.assertEqual(appt.appointment_type, kind)

    def test_priority_order_emergency_first(self):
        appts = [c(self.clock).book(PATIENT, triage(k)) for c, k in [
            (OnlineAppointmentCreator, AppointmentType.ONLINE),
            (EmergencyAppointmentCreator, AppointmentType.EMERGENCY),
            (GeneralAppointmentCreator, AppointmentType.GENERAL)]]
        ordered = sorted(appts, key=lambda a: a.priority)
        self.assertEqual([type(a) for a in ordered],
                         [EmergencyAppointment, GeneralAppointment, OnlineAppointment])

    def test_emergency_is_immediate(self):
        appt = EmergencyAppointmentCreator(self.clock).book(
            PATIENT, triage(AppointmentType.EMERGENCY, Clinic.EMERGENCY, 95))
        self.assertEqual(appt.scheduled_at, FRIDAY_EVENING)

    def test_general_skips_weekend(self):
        appt = GeneralAppointmentCreator(self.clock).book(PATIENT, triage(AppointmentType.GENERAL))
        self.assertEqual(appt.scheduled_at, datetime(2026, 11, 2, 9, 0))   # Pazartesi 09:00
        self.assertEqual(appt.scheduled_at.weekday(), 0)

    def test_online_has_unique_meeting_link(self):
        c = OnlineAppointmentCreator(self.clock)
        a, b = (c.book(PATIENT, triage(AppointmentType.ONLINE)) for _ in range(2))
        self.assertNotEqual(a.meeting_link, b.meeting_link)
        self.assertIn(a.meeting_link, a.describe())

    def test_creator_for_selects_by_triage(self):
        self.assertIsInstance(creator_for(triage(AppointmentType.ONLINE)), OnlineAppointmentCreator)
        self.assertIsInstance(creator_for(triage(AppointmentType.EMERGENCY)), EmergencyAppointmentCreator)

    def test_client_code_depends_only_on_abstractions(self):
        def client(creator: AppointmentCreator) -> Appointment:
            return creator.book(PATIENT, triage(AppointmentType.GENERAL))
        self.assertIsInstance(client(GeneralAppointmentCreator(self.clock)), Appointment)


if __name__ == "__main__":
    unittest.main()
