"""Çevrimdışı embedding: hashing trick + karakter 3-gramları.

Gerçek bir embedding modeli EmbeddingProvider Protocol'üne uyarak bunun yerine
takılabilir. 3-gramlar Türkçe ek farklarına (ağrı / ağrısı) dayanıklılık sağlar.
Python'un hash() fonksiyonu çalıştırmaya göre değiştiği için crc32 kullanılır
(sonuçlar deterministik olsun).
"""
from __future__ import annotations

import math
import re
import zlib

from ..interfaces import EmbeddingProvider

_TOKEN = re.compile(r"[a-zçğıöşü0-9]+")
_STOPWORDS = frozenset({"ve", "ile", "bir", "bu", "çok", "var", "oldu", "oluyor", "gibi",
                        "da", "de", "ama", "için", "ben", "bende", "beni", "çıkıyor"})


class HashingEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 512) -> None:
        if dimension <= 0:
            raise ValueError("dimension pozitif olmalıdır")
        self._dim = dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self._dim
        for word in _TOKEN.findall(text.casefold()):
            if len(word) < 2 or word in _STOPWORDS:
                continue
            self._add(vector, f"w:{word}", 1.0)
            padded = f"<{word}>"
            for i in range(len(padded) - 2):
                self._add(vector, f"c:{padded[i:i + 3]}", 0.5)
        norm = math.sqrt(sum(v * v for v in vector))
        return [v / norm for v in vector] if norm else vector

    def _add(self, vector: list[float], feature: str, weight: float) -> None:
        vector[zlib.crc32(feature.encode("utf-8")) % self._dim] += weight
