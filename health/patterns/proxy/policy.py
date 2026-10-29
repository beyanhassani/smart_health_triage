"""RBAC kuralları: hangi rol hangi işlemi yapabilir."""
from __future__ import annotations

from ...domain import Permission, Role, User

# Rol -> izinler. ADMIN bilerek boştur: sistem yöneticisi tıbbi veriyi görmez.
_ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.DOCTOR: frozenset({Permission.READ, Permission.WRITE}),
    Role.NURSE: frozenset({Permission.READ}),
    Role.PATIENT: frozenset({Permission.READ}),   # yalnızca kendi kaydı
    Role.ADMIN: frozenset(),
}


class AccessPolicy:
    def is_allowed(self, user: User, permission: Permission, record_owner_id: str) -> bool:
        if permission not in _ROLE_PERMISSIONS[user.role]:
            return False
        if user.role is Role.PATIENT:
            return user.user_id == record_owner_id   # hasta başkasının kaydını göremez
        return True
