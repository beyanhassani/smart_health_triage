"""Proxy rolü: Subject. Hem RealMedicalRecord hem MedicalRecordProxy bunu gerçekler."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from ..domain import MedicalRecordData, User


# Kalıp: Proxy | Rol: Subject
@runtime_checkable
class IMedicalRecord(Protocol):
    def read(self, user: User) -> MedicalRecordData: ...

    def update(self, user: User, notes: str) -> None: ...
