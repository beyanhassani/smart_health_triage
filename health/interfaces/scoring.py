"""Strategy rolü: ciddiyet skoru hesaplama algoritmasının soyutlaması."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

from ..domain import RetrievedDocument


# Kalıp: Strategy | Rol: Strategy
class SeverityScoringStrategy(ABC):
    @abstractmethod
    def score(self, matches: Sequence[RetrievedDocument]) -> float:
        """Eşleşen dokümanlardan 0..100 arası ciddiyet skoru üretir."""
