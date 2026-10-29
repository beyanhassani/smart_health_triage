"""Strategy - Concrete Strategy'ler.

Aynı eşleşmelerden üç farklı ciddiyet politikası üretilir. Algoritma, bağlam
(RagTriageEngine) değiştirilmeden çalışma zamanında seçilebilir.
"""
from __future__ import annotations

from typing import Sequence

from ...domain import RetrievedDocument
from ...interfaces import SeverityScoringStrategy


# Kalıp: Strategy | Rol: ConcreteStrategy
class TopMatchSeverityStrategy(SeverityScoringStrategy):
    """En benzer dokümanın ciddiyeti belirleyicidir."""

    def score(self, matches: Sequence[RetrievedDocument]) -> float:
        if not matches:
            return 0.0
        best = max(matches, key=lambda m: m.similarity)
        return best.document.severity


# Kalıp: Strategy | Rol: ConcreteStrategy
class WeightedAverageSeverityStrategy(SeverityScoringStrategy):
    """Benzerlik ağırlıklı ortalama: tek bir yanlış eşleşmenin etkisini azaltır."""

    def score(self, matches: Sequence[RetrievedDocument]) -> float:
        total = sum(m.similarity for m in matches)
        if total <= 0:
            return 0.0
        return sum(m.similarity * m.document.severity for m in matches) / total


# Kalıp: Strategy | Rol: ConcreteStrategy
class ConservativeSeverityStrategy(SeverityScoringStrategy):
    """Temkinli politika: eşleşen en ciddi durumu varsayar (klinik olarak daha güvenli)."""

    def score(self, matches: Sequence[RetrievedDocument]) -> float:
        return max((m.document.severity for m in matches), default=0.0)
