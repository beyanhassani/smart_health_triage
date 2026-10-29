import unittest
from datetime import datetime

from health.ai import (HashingEmbeddingProvider, InMemoryVectorStore, KnowledgeBase,
                       OfflineTemplateLLM, RagTriageEngine, cosine_similarity, default_documents)
from health.app import create_rag_system
from health.domain import (AppointmentType, Clinic, Complaint, KnowledgeDocument, Patient,
                           RetrievedDocument)
from health.interfaces import SeverityScoringStrategy
from health.patterns.strategy import (ConservativeSeverityStrategy, TopMatchSeverityStrategy,
                                      WeightedAverageSeverityStrategy)
from health.services import KeywordTriageEngine

CLOCK = lambda: datetime(2026, 10, 28, 10, 0)


def doc(i, sev, clinic=Clinic.INTERNAL_MEDICINE):
    return KnowledgeDocument(i, "x", clinic, sev)


class SimilarityTests(unittest.TestCase):
    def test_cosine_basic(self):
        self.assertAlmostEqual(cosine_similarity([1, 0], [1, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)
        self.assertEqual(cosine_similarity([0, 0], [1, 1]), 0.0)

    def test_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            cosine_similarity([1], [1, 2])


class EmbeddingAndStoreTests(unittest.TestCase):
    def setUp(self):
        self.emb = HashingEmbeddingProvider()

    def test_deterministic_and_normalized(self):
        a, b = self.emb.embed("kalp çarpıntısı"), self.emb.embed("kalp çarpıntısı")
        self.assertEqual(a, b)
        self.assertEqual(len(a), 512)
        self.assertAlmostEqual(sum(x * x for x in a), 1.0, places=6)

    def test_similar_texts_closer_than_unrelated(self):
        q = self.emb.embed("kalbim çok hızlı çarpıyor")
        near = cosine_similarity(q, self.emb.embed("kalp çarpıntısı hızlı kalp atışı"))
        far = cosine_similarity(q, self.emb.embed("ciltte kaşıntı kızarıklık"))
        self.assertGreater(near, far)

    def test_store_returns_best_first_and_respects_top_k(self):
        store = InMemoryVectorStore()
        for i, t in [("a", "diz ağrısı"), ("b", "cilt kaşıntı"), ("c", "diz şişlik")]:
            store.add(i, t, self.emb.embed(t))
        res = store.search(self.emb.embed("dizim ağrıyor"), top_k=2)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0][0], "a")
        self.assertGreaterEqual(res[0][1], res[1][1])


class StrategyTests(unittest.TestCase):
    MATCHES = [RetrievedDocument(doc("a", 40), 0.8), RetrievedDocument(doc("b", 90), 0.2)]

    def test_same_input_different_policies(self):
        top = TopMatchSeverityStrategy().score(self.MATCHES)
        avg = WeightedAverageSeverityStrategy().score(self.MATCHES)
        cons = ConservativeSeverityStrategy().score(self.MATCHES)
        self.assertEqual(top, 40)
        self.assertAlmostEqual(avg, 50.0)          # (0.8*40 + 0.2*90) / 1.0
        self.assertEqual(cons, 90)

    def test_empty_matches_score_zero(self):
        for s in (TopMatchSeverityStrategy(), WeightedAverageSeverityStrategy(), ConservativeSeverityStrategy()):
            self.assertEqual(s.score([]), 0.0)

    def test_strategies_share_the_interface(self):
        for s in (TopMatchSeverityStrategy(), WeightedAverageSeverityStrategy(), ConservativeSeverityStrategy()):
            self.assertIsInstance(s, SeverityScoringStrategy)

    def test_interface_is_abstract(self):
        with self.assertRaises(TypeError):
            SeverityScoringStrategy()


class ConstantStrategy(SeverityScoringStrategy):
    def __init__(self, value):
        self.value = value

    def score(self, matches):
        return self.value


class SpyStore(InMemoryVectorStore):
    calls = 0

    def search(self, vector, top_k=3):
        SpyStore.calls += 1
        return super().search(vector, top_k)


def build_engine(strategy=None, llm=None, store=None):
    emb = HashingEmbeddingProvider()
    store = store or InMemoryVectorStore()
    kb = KnowledgeBase(default_documents())
    kb.index(emb, store)
    return RagTriageEngine(emb, store, kb, strategy or WeightedAverageSeverityStrategy(),
                           KeywordTriageEngine(), llm)


def assess(engine, text):
    return engine.assess(Complaint("p1", text))


class RagEngineTests(unittest.TestCase):
    def test_retrieval_routes_to_right_clinic(self):
        cases = {
            "Kalbim çok hızlı çarpıyor ve başım dönüyor": Clinic.CARDIOLOGY,
            "Cildimde kaşıntı ve kızarıklık var": Clinic.DERMATOLOGY,
            "Dizim ağrıyor merdiven çıkarken": Clinic.ORTHOPEDICS,
            "Midem bulanıyor ve ishalim var": Clinic.INTERNAL_MEDICINE,
        }
        engine = build_engine()
        for text, clinic in cases.items():
            with self.subTest(text=text):
                r = assess(engine, text)
                self.assertEqual(r.clinic, clinic)
                self.assertEqual(r.appointment_type, AppointmentType.GENERAL)
                self.assertTrue(r.sources)

    def test_routine_request_goes_online(self):
        r = assess(build_engine(), "Reçetemi yenilemek ve tahlil sonucuma bakmak istiyorum")
        self.assertEqual(r.appointment_type, AppointmentType.ONLINE)

    def test_stroke_like_description_is_emergency_via_rag(self):
        r = assess(build_engine(), "Ani başlayan şiddetli baş ağrısı ve konuşma bozukluğu")
        self.assertEqual(r.appointment_type, AppointmentType.EMERGENCY)
        self.assertEqual(r.clinic, Clinic.EMERGENCY)

    def test_safety_net_bypasses_rag(self):
        SpyStore.calls = 0
        r = assess(build_engine(store=SpyStore()), "Şiddetli göğüs ağrısı var")
        self.assertEqual(r.appointment_type, AppointmentType.EMERGENCY)
        self.assertEqual(SpyStore.calls, 0)

    def test_unknown_complaint_falls_back_to_safety_net(self):
        r = assess(build_engine(), "xyzxyz qwerty")
        self.assertEqual((r.clinic, r.appointment_type), (Clinic.INTERNAL_MEDICINE, AppointmentType.GENERAL))
        self.assertEqual(r.sources, ())

    def test_engine_delegates_scoring_to_strategy(self):
        engine = build_engine(ConstantStrategy(85))
        r = assess(engine, "Dizim ağrıyor merdiven çıkarken")
        self.assertEqual((r.severity_score, r.appointment_type), (85, AppointmentType.EMERGENCY))
        self.assertEqual(r.clinic, Clinic.EMERGENCY)
        engine.set_strategy(ConstantStrategy(10))                  # çalışma zamanında değişim
        r = assess(engine, "Dizim ağrıyor merdiven çıkarken")
        self.assertEqual((r.severity_score, r.appointment_type), (10, AppointmentType.ONLINE))
        engine.set_strategy(ConstantStrategy(50))
        self.assertEqual(assess(engine, "Dizim ağrıyor merdiven çıkarken").appointment_type, AppointmentType.GENERAL)

    def test_policy_changes_outcome_for_same_complaint(self):
        text = "Kolum kırıldı şiddetli ağrı"
        weighted = assess(build_engine(WeightedAverageSeverityStrategy()), text)
        conservative = assess(build_engine(ConservativeSeverityStrategy()), text)
        self.assertEqual(weighted.appointment_type, AppointmentType.GENERAL)
        self.assertEqual(conservative.appointment_type, AppointmentType.EMERGENCY)

    def test_llm_writes_rationale_but_does_not_decide(self):
        with_llm = assess(build_engine(llm=OfflineTemplateLLM()), "Cildimde kaşıntı ve kızarıklık var")
        without = assess(build_engine(), "Cildimde kaşıntı ve kızarıklık var")
        self.assertTrue(with_llm.rationale.startswith("Çevrimdışı özet"))
        self.assertEqual((with_llm.clinic, with_llm.severity_score), (without.clinic, without.severity_score))

    def test_broken_llm_does_not_break_triage(self):
        class Broken:
            def generate(self, prompt):
                raise RuntimeError("API down")
        r = assess(build_engine(llm=Broken()), "Cildimde kaşıntı ve kızarıklık var")
        self.assertEqual(r.clinic, Clinic.DERMATOLOGY)
        self.assertIn("ciddiyet", r.rationale)


class RagSystemTests(unittest.TestCase):
    def test_facade_with_rag_end_to_end(self):
        facade, notifier, engine = create_rag_system(CLOCK)
        ali = Patient("p1", "Ali", 30, email="ali@mail.com")
        a = facade.request_appointment(ali, "Kalbim çok hızlı çarpıyor ve başım dönüyor")
        self.assertEqual((a.clinic_name, a.appointment_type), ("cardiology", AppointmentType.GENERAL))
        b = facade.request_appointment(ali, "Şiddetli göğüs ağrısı")
        self.assertEqual(b.appointment_type, AppointmentType.EMERGENCY)
        self.assertEqual(len(notifier.sent), 2)


if __name__ == "__main__":
    unittest.main()
