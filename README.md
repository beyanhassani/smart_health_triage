# Smart AI Health & Triage Assistant

Modüler sağlık asistanı: şikâyet -> RAG tabanlı triage -> randevu -> bildirim.
Python 3.11, `abc.ABC` ve `typing.Protocol` ile arayüzler, SOLID prensipleri.

## Dizin Yapısı
- `health/domain/`      enum'lar ve değiştirilemez (immutable) veri modelleri (davranış yok)
- `health/interfaces/`  sistemin tüm soyutlamaları (ABC / Protocol)
- `health/patterns/`    GoF kalıplarının somut gerçeklemeleri (adım adım eklenir)
- `health/services/`    alt sistem servisleri (bildirim vb.)
- `health/ai/`          RAG motoru: embedding, vektör deposu, ciddiyet skoru
- `tests/`              unittest testleri (`python -m unittest discover`)

## Kural: ABC mi Protocol mü?
- `ABC`      -> ortak davranışı olan roller (Creator, Subject, Observer, Product)
- `Protocol` -> dış veya değiştirilebilir bağımlılıklar (LLM, embedding, vektör deposu, alt sistemler)

## İlerleme
- [x] Adım 1: yapı, arayüzler, domain modelleri
- [x] Adım 2: Factory Method (3 Creator + 3 Product)
- [x] Adım 3: Proxy (RBAC + tembel yükleme + denetim kaydı)
- [x] Adım 4: Observer (Subject + Patient/Doctor observer + durum geçiş kuralları)
- [x] Adım 5: Facade (HealthSystemFacade + AppointmentService + KeywordTriageEngine + rol etiketleri)
- [x] Adım 6: RAG motoru (embedding + vektör deposu + Strategy ile ciddiyet skoru + çevrimdışı LLM)

## Çalıştırma
Demo: `python demo.py`

```
python -m unittest discover -v
```
RAG sistemi tamamen çevrimdışı çalışır (yerel embedding + sahte LLM); API anahtarı gerekmez.
Bilgi tabanı dokümanları eğitim amaçlı sentetik örneklerdir ve tıbbi tavsiye değildir.
