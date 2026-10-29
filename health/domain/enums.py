"""Sistem genelinde kullanılan kapalı (sabit) kelime dağarcığı."""
from enum import Enum


class AppointmentType(Enum):
    EMERGENCY = "emergency"   # Acil
    GENERAL = "general"       # Genel
    ONLINE = "online"         # Online


class AppointmentStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Role(Enum):
    """RBAC Proxy tarafından kontrol edilen roller."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"
    ADMIN = "admin"


class Clinic(Enum):
    EMERGENCY = "emergency"
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    ORTHOPEDICS = "orthopedics"
    INTERNAL_MEDICINE = "internal_medicine"
    DERMATOLOGY = "dermatology"


class Permission(Enum):
    """Bir kayıt üzerinde yapılabilecek işlemler."""
    READ = "read"
    WRITE = "write"
