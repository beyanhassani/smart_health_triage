"""Çevrimdışı sahte LLM (LLMClient Protocol gerçeklemesi): internet/API anahtarı gerektirmez."""
from __future__ import annotations

from ..interfaces import LLMClient


class OfflineTemplateLLM(LLMClient):
    """İstemdeki '- ' ile başlayan eşleşme satırlarını kısa bir gerekçeye dönüştürür."""

    def generate(self, prompt: str) -> str:
        lines = [l[2:].strip() for l in prompt.splitlines() if l.startswith("- ")]
        return "Çevrimdışı özet: " + "; ".join(lines) if lines else "Çevrimdışı özet: eşleşme yok."
