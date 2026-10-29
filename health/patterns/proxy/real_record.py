"""Proxy - Real Subject.

Gerçek tıbbi kayıt. Yetki kontrolü BİLMEZ; yalnızca veriyi okur/günceller.
Yetki sorumluluğu tamamen Proxy'dedir (Single Responsibility).
"""
from __future__ import annotations

from dataclasses import replace

from ...domain import MedicalRecordData, User
from ...interfaces import IMedicalRecord


# Kalıp: Proxy | Rol: RealSubject
class RealMedicalRecord(IMedicalRecord):
    def __init__(self, data: MedicalRecordData) -> None:
        self._data = data

    def read(self, user: User) -> MedicalRecordData:
        return self._data

    def update(self, user: User, notes: str) -> None:
        # MedicalRecordData değiştirilemez olduğu için yeni bir kopya ile değiştirilir.
        self._data = replace(self._data, notes=notes)
