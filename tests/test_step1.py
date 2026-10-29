import unittest
from datetime import datetime

from health.domain import (AppointmentType, Clinic, Complaint, Patient, TriageResult)
from health.interfaces import (Appointment, AppointmentCreator, EmbeddingProvider,
                               IAppointmentObserver, IAppointmentSubject, LLMClient)


class DomainTests(unittest.TestCase):
    def test_valid_triage_result(self):
        r = TriageResult(80.0, Clinic.EMERGENCY, AppointmentType.EMERGENCY)
        self.assertEqual(r.clinic, Clinic.EMERGENCY)

    def test_severity_out_of_range(self):
        with self.assertRaises(ValueError):
            TriageResult(101, Clinic.EMERGENCY, AppointmentType.EMERGENCY)

    def test_empty_complaint_rejected(self):
        with self.assertRaises(ValueError):
            Complaint("p1", "   ")

    def test_models_are_immutable(self):
        p = Patient("p1", "Ali", 30)
        with self.assertRaises(Exception):
            p.name = "X"


class InterfaceTests(unittest.TestCase):
    def test_abstract_classes_cannot_be_instantiated(self):
        for cls in (Appointment, AppointmentCreator, IAppointmentObserver, IAppointmentSubject):
            with self.assertRaises(TypeError):
                cls()

    def test_protocol_structural_typing(self):
        class FakeLLM:
            def generate(self, prompt: str) -> str:
                return "ok"
        self.assertIsInstance(FakeLLM(), LLMClient)
        self.assertNotIsInstance(FakeLLM(), EmbeddingProvider)


if __name__ == "__main__":
    unittest.main()
