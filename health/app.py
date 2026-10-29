"""Kompozisyon kökü (composition root): somut sınıfların tek bir yerde birleştirildiği yer."""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from .patterns.facade import HealthSystemFacade
from .patterns.observer import AppointmentSubject
from .services import AppointmentService, InMemoryNotificationService, KeywordTriageEngine


def create_default_system(clock: Callable[[], datetime] = datetime.now
                          ) -> tuple[HealthSystemFacade, InMemoryNotificationService]:
    notifier = InMemoryNotificationService()
    subject = AppointmentSubject()
    facade = HealthSystemFacade(
        triage=KeywordTriageEngine(),
        appointments=AppointmentService(subject),
        notifier=notifier,
        subject=subject,
        clock=clock,
    )
    return facade, notifier
