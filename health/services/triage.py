"""Triage alt sistemi: kural tabanlı motor.

Bu motor iki iş görür:
1. RAG motoru gelene kadar çalışan basit bir ITriageEngine gerçeklemesidir.
2. RAG eklendikten sonra da KRİTİK SEMPTOM güvenlik ağı olarak kalır: ölümcül
   belirtiler LLM'e sorulmadan doğrudan acile yönlendirilir.
"""
from __future__ import annotations

from ..domain import AppointmentType, Clinic, Complaint, TriageResult
from ..interfaces import ITriageEngine

_CRITICAL = ("göğüs ağrısı", "nefes darlığı", "bilinç kaybı", "bayıl", "felç",
             "şiddetli kanama", "kalp krizi")

_CLINIC_KEYWORDS: tuple[tuple[Clinic, tuple[str, ...]], ...] = (
    (Clinic.CARDIOLOGY, ("çarpıntı", "kalp", "tansiyon")),
    (Clinic.NEUROLOGY, ("baş ağrısı", "migren", "baş dönmesi", "uyuşma")),
    (Clinic.ORTHOPEDICS, ("diz", "kemik", "bel ağrısı", "eklem", "kırık")),
    (Clinic.DERMATOLOGY, ("cilt", "kaşıntı", "döküntü", "sivilce")),
)

_ONLINE_KEYWORDS = ("rapor", "reçete", "kontrol", "sonuç")


# Kalıp: Facade | Rol: Subsystem (TriageEngine)
class KeywordTriageEngine(ITriageEngine):
    def assess(self, complaint: Complaint) -> TriageResult:
        text = complaint.text.casefold()

        hit = next((k for k in _CRITICAL if k in text), None)
        if hit:
            return TriageResult(95.0, Clinic.EMERGENCY, AppointmentType.EMERGENCY,
                                rationale=f"kritik semptom: {hit}")

        for clinic, words in _CLINIC_KEYWORDS:
            hit = next((w for w in words if w in text), None)
            if hit:
                return TriageResult(50.0, clinic, AppointmentType.GENERAL,
                                    rationale=f"semptom anahtar kelimesi: {hit}")

        if any(w in text for w in _ONLINE_KEYWORDS):
            return TriageResult(15.0, Clinic.INTERNAL_MEDICINE, AppointmentType.ONLINE,
                                rationale="rutin işlem (rapor/reçete/kontrol)")

        return TriageResult(30.0, Clinic.INTERNAL_MEDICINE, AppointmentType.GENERAL,
                            rationale="belirgin semptom yok, dahiliyeye yönlendirildi")
