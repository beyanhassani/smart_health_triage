"""Kompozisyon kökü (composition root): somut sınıfların tek bir yerde birleştirildiği yer."""
from __future__ import annotations

from datetime import datetime
from typing import Callable

from .ai import (HashingEmbeddingProvider, InMemoryVectorStore, KnowledgeBase, OfflineTemplateLLM,
                 RagTriageEngine, default_documents)
from .interfaces import SeverityScoringStrategy
from .patterns.facade import HealthSystemFacade
from .patterns.observer import AppointmentSubject
from .patterns.strategy import WeightedAverageSeverityStrategy
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


def create_rag_system(clock: Callable[[], datetime] = datetime.now,
                      strategy: SeverityScoringStrategy | None = None
                      ) -> tuple[HealthSystemFacade, InMemoryNotificationService, RagTriageEngine]:
    """RAG tabanlı triage ile tam sistem. Her şey çevrimdışı (sahte LLM + yerel embedding) çalışır."""
    embedder = HashingEmbeddingProvider()
    store = InMemoryVectorStore()
    knowledge = KnowledgeBase(default_documents())
    knowledge.index(embedder, store)

    engine = RagTriageEngine(
        embedder=embedder, store=store, knowledge=knowledge,
        strategy=strategy or WeightedAverageSeverityStrategy(),
        safety_net=KeywordTriageEngine(),          # kritik semptom güvenlik ağı
        llm=OfflineTemplateLLM(),
    )
    notifier = InMemoryNotificationService()
    subject = AppointmentSubject()
    facade = HealthSystemFacade(triage=engine, appointments=AppointmentService(subject),
                                notifier=notifier, subject=subject, clock=clock)
    return facade, notifier, engine
