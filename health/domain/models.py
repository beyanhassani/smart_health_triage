"""Değiştirilemez (immutable) veri taşıyıcıları. Yalnızca veri tutarlar; davranış kalıplarda yer alır."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .enums import AppointmentStatus, AppointmentType, Clinic, Role


@dataclass(frozen=True)
class Patient:
    patient_id: str
    name: str
    age: int
    email: str = ""

    def __post_init__(self) -> None:
        if self.age < 0:
            raise ValueError("yaş negatif olamaz")


@dataclass(frozen=True)
class User:
    """Bir kaynağa erişmeye çalışan aktör (RBAC Proxy tarafından kullanılır)."""
    user_id: str
    role: Role


@dataclass(frozen=True)
class Complaint:
    """Hastanın serbest metin olarak yazdığı semptomlar."""
    patient_id: str
    text: str
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("şikâyet metni boş olamaz")


@dataclass(frozen=True)
class TriageResult:
    """TriageEngine çıktısı: hangi poliklinik ve aciliyet düzeyi."""
    severity_score: float            # 0 (zararsız) .. 100 (hayati tehlike)
    clinic: Clinic
    appointment_type: AppointmentType
    rationale: str = ""
    sources: tuple[str, ...] = ()    # RAG ile getirilen dokümanların id'leri

    def __post_init__(self) -> None:
        if not 0.0 <= self.severity_score <= 100.0:
            raise ValueError("severity_score [0, 100] aralığında olmalıdır")


@dataclass(frozen=True)
class MedicalRecordData:
    patient_id: str
    diagnoses: tuple[str, ...] = ()
    medications: tuple[str, ...] = ()
    notes: str = ""


@dataclass(frozen=True)
class AppointmentEvent:
    """Randevu durumu değiştiğinde gözlemcilere (observer) iletilen bilgi paketi."""
    appointment_id: str
    patient_id: str
    old_status: AppointmentStatus
    new_status: AppointmentStatus
    clinic_name: str = ""
    message: str = ""


@dataclass(frozen=True)
class KnowledgeDocument:
    """RAG bilgi tabanındaki tek bir klinik doküman (eğitim amaçlı, sentetik)."""
    doc_id: str
    text: str
    clinic: Clinic
    severity: float                  # 0 .. 100

    def __post_init__(self) -> None:
        if not 0.0 <= self.severity <= 100.0:
            raise ValueError("severity [0, 100] aralığında olmalıdır")


@dataclass(frozen=True)
class RetrievedDocument:
    """Vektör aramasından dönen doküman ve kosinüs benzerliği."""
    document: KnowledgeDocument
    similarity: float
