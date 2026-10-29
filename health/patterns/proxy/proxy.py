"""Proxy - Proxy rolü (Protection Proxy + Lazy Loading).

İki sorunu çözer:
1. Koruma: RBAC kontrolü yapılmadan gerçek kayda hiç dokunulmaz.
2. Tembel yükleme: pahalı/hassas gerçek kayıt yalnızca İLK YETKİLİ erişimde yüklenir.
   Reddedilen bir istek gerçek kaydı hiç belleğe getirmez.
"""
from __future__ import annotations

from typing import Callable

from ...domain import AccessDeniedError, MedicalRecordData, Permission, User
from ...interfaces import IMedicalRecord
from .audit import AccessAuditLog, AccessLogEntry
from .policy import AccessPolicy


# Kalıp: Proxy | Rol: Proxy
class MedicalRecordProxy(IMedicalRecord):
    def __init__(self, patient_id: str,
                 record_loader: Callable[[], IMedicalRecord],
                 policy: AccessPolicy | None = None,
                 audit_log: AccessAuditLog | None = None) -> None:
        self._patient_id = patient_id
        self._record_loader = record_loader
        self._policy = policy or AccessPolicy()
        self._audit = audit_log or AccessAuditLog()
        self._real: IMedicalRecord | None = None     # henüz yüklenmedi

    def read(self, user: User) -> MedicalRecordData:
        self._check(user, Permission.READ)
        return self._real_record().read(user)

    def update(self, user: User, notes: str) -> None:
        self._check(user, Permission.WRITE)
        self._real_record().update(user, notes)

    def _check(self, user: User, permission: Permission) -> None:
        allowed = self._policy.is_allowed(user, permission, self._patient_id)
        self._audit.record(AccessLogEntry(user.user_id, user.role, permission,
                                          self._patient_id, allowed))
        if not allowed:
            raise AccessDeniedError(
                f"{user.role.value} rolü '{permission.value}' işlemi için yetkili değil")

    def _real_record(self) -> IMedicalRecord:
        if self._real is None:
            self._real = self._record_loader()
        return self._real
