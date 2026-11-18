# Smart AI Health & Triage Assistant

EBLG443 Tasarım Kalıpları dönem projesi · Beyan Hassani – 20212013122

Hasta şikâyetini ön değerlendirmeden (triage) geçiren, uygun poliklinik ve randevu türünü
(acil / genel / online) belirleyen, randevu durumunu takip edip bildirim gönderen ve tıbbi
kayıtlara rol tabanlı erişim (RBAC) sağlayan modüler bir sağlık asistanı.
Sistem tanı koymaz; yalnızca yönlendirme yapar.

- Python 3.11+, arayüzler `abc.ABC` ve `typing.Protocol` ile, SOLID prensipleri
- Harici kütüphane yok; internet ve API anahtarı gerekmez
- RAG tabanlı triage (yerel embedding + kosinüs benzerliği), kritik semptomlar için kural tabanlı güvenlik ağı

## Hızlı başlangıç

```bash
python -m unittest discover -v    # 64 test
python demo.py                    # uçtan uca gösterim
```

Ayrıntılar: [KURULUM.md](KURULUM.md) · [TEST.md](TEST.md)

## Kalıp Haritası

| Kalıp | Grup | Çözülen problem | Rol → Sınıf (dosya) |
|---|---|---|---|
| **Factory Method** | Yaratımsal | Triage sonucuna göre davranışı farklı randevu türlerinin üretimi | Product → `Appointment` (`interfaces/appointment.py`)<br>ConcreteProduct → `EmergencyAppointment`, `GeneralAppointment`, `OnlineAppointment` (`patterns/factory/appointments.py`)<br>Creator → `AppointmentCreator` (`interfaces/appointment.py`)<br>ConcreteCreator → `Emergency/General/OnlineAppointmentCreator` (`patterns/factory/creators.py`) |
| **Proxy** | Yapısal | Hassas tıbbi kayda yetkisiz erişimin engellenmesi, denetim kaydı ve tembel yükleme | Subject → `IMedicalRecord` (`interfaces/medical_record.py`)<br>RealSubject → `RealMedicalRecord` (`patterns/proxy/real_record.py`)<br>Proxy → `MedicalRecordProxy` (`patterns/proxy/proxy.py`) |
| **Facade** | Yapısal | Triage, randevu, gözlemci ve bildirim adımlarının tek giriş noktasında sunulması | Facade → `HealthSystemFacade` (`patterns/facade/facade.py`)<br>Subsystem → `KeywordTriageEngine`/`RagTriageEngine`, `AppointmentService`, `InMemoryNotificationService` (`services/`, `ai/`) |
| **Observer** | Davranışsal | Randevu durumu değişince hasta ve doktorun bilgilendirilmesi | Subject → `IAppointmentSubject` / `AppointmentSubject` (`interfaces/observer.py`, `patterns/observer/subject.py`)<br>ConcreteObserver → `PatientObserver`, `DoctorObserver` (`patterns/observer/observers.py`) |
| **Strategy** | Davranışsal | Ciddiyet skoru hesaplama algoritmasının çalışma zamanında değiştirilebilmesi | Strategy → `SeverityScoringStrategy` (`interfaces/scoring.py`)<br>ConcreteStrategy → `TopMatch…`, `WeightedAverage…`, `Conservative…SeverityStrategy` (`patterns/strategy/strategies.py`)<br>Context → `RagTriageEngine` (`ai/rag_triage.py`) |

Kodda her kalıp rolü, kalıbın adını ve rolünü belirten kısa bir yorumla işaretlenmiştir:

```python
# Kalıp: Factory Method | Rol: ConcreteCreator
class EmergencyAppointmentCreator(_ClockedCreator): ...
```

Tüm işaretleri listelemek için: `grep -rn "# Kalıp:" health` (işaretlerin varlığı `tests/test_pattern_tags.py` ile denetlenir).

## Dizin Yapısı

- `health/domain/`      enum'lar ve değiştirilemez (immutable) veri modelleri
- `health/interfaces/`  sistemin tüm soyutlamaları (ABC / Protocol)
- `health/patterns/`    GoF kalıplarının somut gerçeklemeleri
- `health/services/`    alt sistem servisleri (triage, randevu, bildirim)
- `health/ai/`          RAG motoru: embedding, vektör deposu, bilgi tabanı, sahte LLM
- `health/app.py`       composition root
- `tests/`              unittest testleri
- `demo.py`             uçtan uca gösterim

## ABC mi Protocol mü?

- `ABC`: ortak davranışı olan roller (Creator, Product, Subject, Observer, Strategy)
- `Protocol`: dış veya değiştirilebilir bağımlılıklar (LLM, embedding, vektör deposu, alt sistem sözleşmeleri, `IMedicalRecord`)

## Güvenlik ve sınırlar

- Ölümcül belirtiler (ör. göğüs ağrısı) LLM/RAG'e sorulmadan kural tabanlı güvenlik ağıyla acile yönlendirilir.
- Triage kararı deterministiktir; LLM yalnızca gerekçe metnini yazar, karar vermez.
- Bilgi tabanı dokümanları eğitim amaçlı sentetik örneklerdir ve tıbbi tavsiye değildir.
- Gömme (embedding) basit bir harf/kelime tabanlı yöntemdir; anlam benzerliğini yakalamaz.

## Kullanılan kaynaklar ve yapay zekâ

- Harici/açık kaynak kütüphane kullanılmamıştır (yalnızca Python standart kütüphanesi).
- Tasarım ve kod taslakları sırasında yapay zekâ kod asistanı (Claude, Anthropic) kullanılmıştır; ayrıntı proje raporunda belirtilmiştir.
- Kaynaklar: Head First Design Patterns (2. Sürüm); Gamma ve ark., Design Patterns (1994).
