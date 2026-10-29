import unittest

from health.domain import AccessDeniedError, MedicalRecordData, Role, User
from health.interfaces import IMedicalRecord
from health.patterns.proxy import AccessAuditLog, MedicalRecordProxy, RealMedicalRecord

DATA = MedicalRecordData("p1", diagnoses=("hipertansiyon",), medications=("X",), notes="ilk not")
DOCTOR = User("d1", Role.DOCTOR)
NURSE = User("n1", Role.NURSE)
ADMIN = User("a1", Role.ADMIN)
OWNER = User("p1", Role.PATIENT)
STRANGER = User("p2", Role.PATIENT)


class ProxyTests(unittest.TestCase):
    def setUp(self):
        self.loads = 0
        self.audit = AccessAuditLog()

        def loader():
            self.loads += 1
            return RealMedicalRecord(DATA)

        self.proxy = MedicalRecordProxy("p1", loader, audit_log=self.audit)

    def test_doctor_can_read_and_write(self):
        self.assertEqual(self.proxy.read(DOCTOR).diagnoses, ("hipertansiyon",))
        self.proxy.update(DOCTOR, "yeni not")
        self.assertEqual(self.proxy.read(DOCTOR).notes, "yeni not")

    def test_nurse_can_read_but_not_write(self):
        self.proxy.read(NURSE)
        with self.assertRaises(AccessDeniedError):
            self.proxy.update(NURSE, "x")

    def test_patient_reads_only_own_record(self):
        self.proxy.read(OWNER)
        with self.assertRaises(AccessDeniedError):
            self.proxy.read(STRANGER)

    def test_patient_cannot_write_even_own(self):
        with self.assertRaises(AccessDeniedError):
            self.proxy.update(OWNER, "x")

    def test_admin_has_no_medical_access(self):
        with self.assertRaises(AccessDeniedError):
            self.proxy.read(ADMIN)

    def test_denied_request_never_loads_real_record(self):
        with self.assertRaises(AccessDeniedError):
            self.proxy.read(STRANGER)
        self.assertEqual(self.loads, 0)

    def test_real_record_loaded_once_lazily(self):
        self.assertEqual(self.loads, 0)
        self.proxy.read(DOCTOR)
        self.proxy.read(NURSE)
        self.assertEqual(self.loads, 1)

    def test_audit_log_records_allowed_and_denied(self):
        self.proxy.read(DOCTOR)
        with self.assertRaises(AccessDeniedError):
            self.proxy.read(STRANGER)
        self.assertEqual(len(self.audit.entries), 2)
        self.assertEqual([e.user_id for e in self.audit.denied], ["p2"])

    def test_proxy_and_real_share_the_same_interface(self):
        self.assertIsInstance(self.proxy, IMedicalRecord)
        self.assertIsInstance(RealMedicalRecord(DATA), IMedicalRecord)


if __name__ == "__main__":
    unittest.main()
