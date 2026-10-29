"""Her kalıp rolünün kodda '# Kalıp: <ad> | Rol: <rol>' yorumuyla işaretlendiğini doğrular (ders şartı)."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED = {
    "health/interfaces/appointment.py": ["Appointment", "AppointmentCreator"],
    "health/interfaces/medical_record.py": ["IMedicalRecord"],
    "health/interfaces/observer.py": ["IAppointmentObserver", "IAppointmentSubject"],
    "health/interfaces/services.py": ["ITriageEngine", "IAppointmentService", "INotificationService"],
    "health/patterns/factory/appointments.py": ["EmergencyAppointment", "GeneralAppointment", "OnlineAppointment"],
    "health/patterns/factory/creators.py": ["EmergencyAppointmentCreator", "GeneralAppointmentCreator", "OnlineAppointmentCreator"],
    "health/patterns/proxy/real_record.py": ["RealMedicalRecord"],
    "health/patterns/proxy/proxy.py": ["MedicalRecordProxy"],
    "health/patterns/observer/subject.py": ["AppointmentSubject"],
    "health/patterns/observer/observers.py": ["PatientObserver", "DoctorObserver"],
    "health/patterns/facade/facade.py": ["HealthSystemFacade"],
    "health/services/appointment_service.py": ["AppointmentService"],
    "health/services/notification.py": ["InMemoryNotificationService"],
    "health/services/triage.py": ["KeywordTriageEngine"],
    "health/interfaces/scoring.py": ["SeverityScoringStrategy"],
    "health/patterns/strategy/strategies.py": ["TopMatchSeverityStrategy", "WeightedAverageSeverityStrategy", "ConservativeSeverityStrategy"],
    "health/ai/rag_triage.py": ["RagTriageEngine"],
}


class PatternTagTests(unittest.TestCase):
    def test_every_role_class_is_tagged(self):
        for rel, classes in EXPECTED.items():
            lines = (ROOT / rel).read_text(encoding="utf-8").split("\n")
            for cls in classes:
                with self.subTest(file=rel, cls=cls):
                    idx = next(i for i, l in enumerate(lines) if l.startswith(f"class {cls}"))
                    while lines[idx - 1].startswith("@"):
                        idx -= 1
                    self.assertTrue(lines[idx - 1].startswith("# Kalıp:"), f"{cls} etiketsiz")


if __name__ == "__main__":
    unittest.main()
