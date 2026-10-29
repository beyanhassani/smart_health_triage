"""Demo: sistemin uçtan uca çalıştırılması.  Kullanım:  python demo.py

Çevrimdışı çalışır (yerel embedding + sahte LLM).
"""
from datetime import datetime

from health.app import create_rag_system
from health.domain import (AccessDeniedError, Clinic, Complaint, InvalidStatusTransitionError,
                           MedicalRecordData, Patient, Role, User)
from health.patterns.strategy import ConservativeSeverityStrategy


def baslik(metin: str) -> None:
    print(f"\n=== {metin} ===")


def yeni_bildirimler(notifier, onceki: int) -> int:
    for n in notifier.sent[onceki:]:
        print(f"   [bildirim -> {n.recipient}] {n.message}")
    return len(notifier.sent)


def main() -> None:
    saat = lambda: datetime(2026, 10, 28, 10, 0)            # çarşamba 10:00 (deterministik demo)
    facade, notifier, engine = create_rag_system(saat)
    ali = Patient("p1", "Ali", 30, "ali@mail.com")
    facade.register_doctor("dr_kalp", Clinic.CARDIOLOGY)
    facade.register_doctor("dr_acil", Clinic.EMERGENCY)

    baslik("1) Triage (RAG + güvenlik ağı) -> randevu türü (Factory Method)")
    sikayetler = [
        "Reçetemi yenilemek ve tahlil sonucuma bakmak istiyorum",
        "Kalbim çok hızlı çarpıyor ve başım dönüyor",
        "Ani başlayan şiddetli baş ağrısı ve konuşma bozukluğu",
        "Şiddetli göğüs ağrısı ve nefes darlığı var",
    ]
    for s in sikayetler:
        r = engine.assess(Complaint(ali.patient_id, s))
        print(f"- {s}\n    klinik={r.clinic.value} tür={r.appointment_type.value} "
              f"skor={r.severity_score} kaynak={list(r.sources)}")

    baslik("2) Facade ile randevu + Observer ile bildirim")
    onceki = 0
    randevu = facade.request_appointment(ali, "Kalbim çok hızlı çarpıyor ve başım dönüyor")
    print("   randevu:", randevu.describe())
    onceki = yeni_bildirimler(notifier, onceki)
    facade.confirm_appointment(randevu.appointment_id, "Lütfen 10 dk erken geliniz")
    onceki = yeni_bildirimler(notifier, onceki)

    baslik("3) Geçersiz durum geçişi reddedilir")
    facade.cancel_appointment(randevu.appointment_id, "mazeret")
    yeni_bildirimler(notifier, onceki)
    try:
        facade.confirm_appointment(randevu.appointment_id)
    except InvalidStatusTransitionError as e:
        print("   HATA (beklenen):", e)

    baslik("4) Proxy: rol tabanlı erişim (RBAC) ve tembel yükleme")
    facade.add_medical_record(MedicalRecordData("p1", ("astım",), ("ventolin",), "ilk not"))
    for kullanici, ad in [(User("d1", Role.DOCTOR), "doktor"), (User("p1", Role.PATIENT), "hasta (kendi kaydı)"),
                          (User("p2", Role.PATIENT), "başka hasta"), (User("a1", Role.ADMIN), "yönetici")]:
        try:
            veri = facade.read_medical_record(kullanici, "p1")
            print(f"   {ad}: İZİN VERİLDİ -> {veri.diagnoses}")
        except AccessDeniedError as e:
            print(f"   {ad}: REDDEDİLDİ -> {e}")

    baslik("5) Strategy: aynı şikâyet, farklı ciddiyet politikası")
    sikayet = "Kolum kırıldı şiddetli ağrı"
    r1 = engine.assess(Complaint("p1", sikayet))
    engine.set_strategy(ConservativeSeverityStrategy())       # çalışma zamanında değişim
    r2 = engine.assess(Complaint("p1", sikayet))
    print(f"   WeightedAverage : skor={r1.severity_score} -> {r1.appointment_type.value} ({r1.clinic.value})")
    print(f"   Conservative    : skor={r2.severity_score} -> {r2.appointment_type.value} ({r2.clinic.value})")


if __name__ == "__main__":
    main()
