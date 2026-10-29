"""RAG bilgi tabanı. Dokümanlar EĞİTİM AMAÇLI sentetik örneklerdir; tıbbi tavsiye değildir."""
from __future__ import annotations

from typing import Iterable

from ..domain import Clinic, KnowledgeDocument
from ..interfaces import EmbeddingProvider, VectorStore


class KnowledgeBase:
    def __init__(self, documents: Iterable[KnowledgeDocument]) -> None:
        self._docs = {d.doc_id: d for d in documents}

    def get(self, doc_id: str) -> KnowledgeDocument:
        return self._docs[doc_id]

    def index(self, embedder: EmbeddingProvider, store: VectorStore) -> None:
        for doc in self._docs.values():
            store.add(doc.doc_id, doc.text, embedder.embed(doc.text))

    def __len__(self) -> int:
        return len(self._docs)


def default_documents() -> tuple[KnowledgeDocument, ...]:
    C = Clinic
    d = KnowledgeDocument
    return (
        d("k01", "göğüs ağrısı sol kola yayılan ter basması nefes darlığı", C.CARDIOLOGY, 95),
        d("k02", "kalp çarpıntısı hızlı kalp atışı hafif baş dönmesi", C.CARDIOLOGY, 55),
        d("k03", "yüksek tansiyon baş ağrısı kulak çınlaması", C.CARDIOLOGY, 45),
        d("n01", "ani şiddetli baş ağrısı konuşma bozukluğu yüzde kayma kol güçsüzlüğü", C.NEUROLOGY, 92),
        d("n02", "tekrarlayan migren ışığa hassasiyet bulantı", C.NEUROLOGY, 40),
        d("n03", "ellerde uyuşma karıncalanma", C.NEUROLOGY, 35),
        d("o01", "diz ağrısı merdiven çıkarken şişlik", C.ORTHOPEDICS, 30),
        d("o02", "bel ağrısı uzun süre oturduktan sonra", C.ORTHOPEDICS, 28),
        d("o03", "düşme sonrası kol kırığı şiddetli ağrı şişlik morarma", C.ORTHOPEDICS, 70),
        d("d01", "ciltte kaşıntı kızarıklık döküntü", C.DERMATOLOGY, 25),
        d("d02", "yüzde sivilce akne cilt bakımı", C.DERMATOLOGY, 15),
        d("i01", "ateş boğaz ağrısı öksürük halsizlik grip belirtileri", C.INTERNAL_MEDICINE, 35),
        d("i02", "mide bulantısı karın ağrısı ishal", C.INTERNAL_MEDICINE, 40),
        d("i03", "rutin kontrol tahlil sonucu rapor reçete yenileme", C.INTERNAL_MEDICINE, 10),
        d("i04", "yorgunluk halsizlik iştahsızlık", C.INTERNAL_MEDICINE, 25),
        d("i05", "şiddetli karın ağrısı kusma yüksek ateş", C.INTERNAL_MEDICINE, 85),
    )
