"""Bellek içi vektör deposu (VectorStore Protocol gerçeklemesi)."""
from __future__ import annotations

from typing import Sequence

from ..interfaces import VectorStore
from .similarity import cosine_similarity


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._items: dict[str, tuple[str, list[float]]] = {}

    def add(self, doc_id: str, text: str, vector: Sequence[float]) -> None:
        self._items[doc_id] = (text, list(vector))

    def search(self, vector: Sequence[float], top_k: int = 3) -> list[tuple[str, float]]:
        scored = [(doc_id, cosine_similarity(vector, stored))
                  for doc_id, (_, stored) in self._items.items()]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._items)
