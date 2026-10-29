"""Bildirim alt sistemi (Facade'ın arkasındaki servislerden biri; GoF kalıbı değildir).

Gerçek e-posta/SMS yerine gönderilenleri bellekte tutar; demo ve testler için yeterlidir.
Gerçek bir sağlayıcı INotificationService Protocol'üne uyarak değiştirilebilir.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..interfaces import INotificationService


@dataclass(frozen=True)
class Notification:
    recipient: str
    message: str


# Kalıp: Facade | Rol: Subsystem (NotificationService)
class InMemoryNotificationService(INotificationService):
    def __init__(self) -> None:
        self._sent: list[Notification] = []

    def send(self, recipient: str, message: str) -> None:
        self._sent.append(Notification(recipient, message))

    @property
    def sent(self) -> tuple[Notification, ...]:
        return tuple(self._sent)
