"""Erişim denetim kaydı (audit log): izinli ve reddedilen tüm denemeler tutulur."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ...domain import Permission, Role


@dataclass(frozen=True)
class AccessLogEntry:
    user_id: str
    role: Role
    permission: Permission
    record_owner_id: str
    allowed: bool
    timestamp: datetime = field(default_factory=datetime.now)


class AccessAuditLog:
    def __init__(self) -> None:
        self._entries: list[AccessLogEntry] = []

    def record(self, entry: AccessLogEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> tuple[AccessLogEntry, ...]:
        return tuple(self._entries)

    @property
    def denied(self) -> tuple[AccessLogEntry, ...]:
        return tuple(e for e in self._entries if not e.allowed)
