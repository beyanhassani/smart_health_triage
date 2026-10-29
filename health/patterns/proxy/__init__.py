"""Proxy kalıbının somut gerçeklemesi."""
from .audit import AccessAuditLog, AccessLogEntry
from .policy import AccessPolicy
from .proxy import MedicalRecordProxy
from .real_record import RealMedicalRecord

__all__ = ["AccessAuditLog", "AccessLogEntry", "AccessPolicy",
           "MedicalRecordProxy", "RealMedicalRecord"]
