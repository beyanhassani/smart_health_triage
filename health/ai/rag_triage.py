"""RAG tabanlı triage motoru (Strategy kalıbında Context).

Akış:
1. Güvenlik ağı: kritik semptom varsa LLM/RAG'a hiç sorulmadan acile yönlendirilir.
2. Retrieval: şikâyet embed edilir, vektör deposunda en benzer dokümanlar bulunur.
3. Ciddiyet skoru: hesaplama, enjekte edilen Strategy'ye bırakılır.
4. Karar deterministiktir; LLM yalnızca gerekçe metnini yazar, karar vermez.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from ..domain import (AppointmentType, Clinic, Complaint, RetrievedDocument, TriageResult)
from ..interfaces import (EmbeddingProvider, ITriageEngine, LLMClient, SeverityScoringStrategy,
                          VectorStore)
from .knowledge_base import KnowledgeBase

EMERGENCY_THRESHOLD = 80.0
ONLINE_THRESHOLD = 20.0


# Kalıp: Strategy | Rol: Context (aynı zamanda Facade alt sistemi: TriageEngine)
class RagTriageEngine(ITriageEngine):
    def __init__(self, embedder: EmbeddingProvider, store: VectorStore, knowledge: KnowledgeBase,
                 strategy: SeverityScoringStrategy, safety_net: ITriageEngine,
                 llm: LLMClient | None = None, top_k: int = 3,
                 min_similarity: float = 0.15, relative_cutoff: float = 0.7) -> None:
        self._embedder = embedder
        self._store = store
        self._knowledge = knowledge
        self._strategy = strategy
        self._safety_net = safety_net
        self._llm = llm
        self._top_k = top_k
        self._min_similarity = min_similarity
        self._relative_cutoff = relative_cutoff

    def set_strategy(self, strategy: SeverityScoringStrategy) -> None:
        """Çalışma zamanında algoritma değişimi."""
        self._strategy = strategy

    def assess(self, complaint: Complaint) -> TriageResult:
        guard = self._safety_net.assess(complaint)
        if guard.appointment_type is AppointmentType.EMERGENCY:
            return guard                                   # güvenlik ağı: RAG'a sorulmaz

        matches = self._retrieve(complaint.text)
        if not matches:
            return guard                                   # bilgi tabanında eşleşme yok

        severity = round(self._strategy.score(matches), 1)
        appointment_type = self._appointment_type(severity)
        clinic = (Clinic.EMERGENCY if appointment_type is AppointmentType.EMERGENCY
                  else self._vote_clinic(matches))
        return TriageResult(
            severity_score=severity,
            clinic=clinic,
            appointment_type=appointment_type,
            rationale=self._explain(matches, severity),
            sources=tuple(m.document.doc_id for m in matches),
        )

    # --- iç yardımcılar -------------------------------------------------
    def _retrieve(self, text: str) -> list[RetrievedDocument]:
        pairs = self._store.search(self._embedder.embed(text), self._top_k)
        pairs = [(doc_id, sim) for doc_id, sim in pairs if sim >= self._min_similarity]
        if not pairs:
            return []
        # Göreli eşik: en iyi eşleşmenin çok altında kalan (gürültü) dokümanlar elenir.
        cutoff = self._relative_cutoff * pairs[0][1]
        return [RetrievedDocument(self._knowledge.get(doc_id), sim)
                for doc_id, sim in pairs if sim >= cutoff]

    @staticmethod
    def _appointment_type(severity: float) -> AppointmentType:
        if severity >= EMERGENCY_THRESHOLD:
            return AppointmentType.EMERGENCY
        if severity <= ONLINE_THRESHOLD:
            return AppointmentType.ONLINE
        return AppointmentType.GENERAL

    @staticmethod
    def _vote_clinic(matches: Sequence[RetrievedDocument]) -> Clinic:
        votes: dict[Clinic, float] = defaultdict(float)
        for m in matches:
            votes[m.document.clinic] += m.similarity       # benzerlik ağırlıklı oy
        return max(votes, key=votes.get)

    def _explain(self, matches: Sequence[RetrievedDocument], severity: float) -> str:
        fallback = (f"ciddiyet {severity}; en yakın eşleşmeler: "
                    + ", ".join(m.document.doc_id for m in matches))
        if self._llm is None:
            return fallback
        lines = "\n".join(f"- {m.document.text} (benzerlik {m.similarity:.2f})" for m in matches)
        prompt = f"Aşağıdaki eşleşmelere dayanarak kısa bir gerekçe yaz.\nEşleşmeler:\n{lines}"
        try:
            return self._llm.generate(prompt)
        except Exception:                                  # LLM hatası triage kararını etkilemesin
            return fallback
