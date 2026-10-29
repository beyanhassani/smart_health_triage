"""Yapay zekâ bağımlılıkları Protocol olarak tanımlanır (Dependency Inversion).

Sistem yalnızca bu soyutlamalara bağlıdır. Böylece demo, sahte (fake) bir
gerçekleme ile internetsiz çalışabilir; gerçek LLM veya vektör veritabanı
sonradan değiştirilerek takılabilir.
"""
from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable


@runtime_checkable
class LLMClient(Protocol):
    def generate(self, prompt: str) -> str: ...


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


@runtime_checkable
class VectorStore(Protocol):
    def add(self, doc_id: str, text: str, vector: Sequence[float]) -> None: ...

    def search(self, vector: Sequence[float], top_k: int = 3) -> list[tuple[str, float]]:
        """(doc_id, cosine_similarity) çiftlerini en iyiden başlayarak döndürür."""
        ...
