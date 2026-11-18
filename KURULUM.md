# Kurulum ve Çalıştırma Kılavuzu

Smart AI Health & Triage Assistant – EBLG443 Tasarım Kalıpları dönem projesi.

## 1. Gereksinimler

| Gereksinim | Ayrıntı |
|---|---|
| Python | 3.11 veya üzeri (geliştirme ortamında 3.12 ile denenmiştir) |
| Git | Depoyu klonlamak için |
| Harici kütüphane | **Yok.** Yalnızca Python standart kütüphanesi kullanılır |
| İnternet / API anahtarı | **Gerekmez.** Sistem çevrimdışı çalışır (yerel embedding + sahte LLM) |

## 2. Kurulum

```bash
git clone https://github.com/beyanhassani/smart_health_triage.git
cd smart_health_triage
```

Sanal ortam isteğe bağlıdır (kurulacak paket olmadığı için gerekli değildir):

```bash
python -m venv .venv
# Linux / macOS:  source .venv/bin/activate
# Windows (cmd):  .venv\Scripts\activate
```

## 3. Testleri çalıştırma

```bash
python -m unittest discover -v
```

Beklenen son satırlar:

```
Ran 64 tests in 0.0xxs

OK
```

Ayrıntılar için bkz. [TEST.md](TEST.md).

## 4. Demoyu çalıştırma

```bash
python demo.py
```

Demo beş bölümden oluşur:

1. Dört şikâyetin triage sonucu (RAG + kritik semptom güvenlik ağı) ve randevu türü (Factory Method)
2. Facade ile randevu oluşturma, onaylama ve bildirimler (Observer)
3. Geçersiz durum geçişinin reddedilmesi
4. Tıbbi kayda rol tabanlı erişim ve tembel yükleme (Proxy)
5. Aynı şikâyet için farklı ciddiyet politikası (Strategy)

## 5. Kodda kullanım örneği

```python
from health.app import create_rag_system
from health.domain import Patient

facade, notifier, engine = create_rag_system()
hasta = Patient("p1", "Ali", 30, "ali@mail.com")

randevu = facade.request_appointment(hasta, "Kalbim çok hızlı çarpıyor ve başım dönüyor")
print(randevu.describe())

facade.confirm_appointment(randevu.appointment_id, "Lütfen 10 dk erken geliniz")
for bildirim in notifier.sent:
    print(bildirim.recipient, "->", bildirim.message)
```

## 6. Sık karşılaşılan sorunlar

| Sorun | Çözüm |
|---|---|
| `python` komutu bulunamıyor | Linux/macOS'ta `python3`, Windows'ta `py` deneyin |
| Windows konsolunda Türkçe karakterler bozuk görünüyor | cmd: `set PYTHONUTF8=1` · PowerShell: `$env:PYTHONUTF8=1`, sonra komutu tekrar çalıştırın |
| `ModuleNotFoundError: No module named 'health'` | Komutları deponun kök dizininden (`health/` klasörünün bulunduğu yer) çalıştırın |
| Beklenmedik sözdizimi / tip hataları | Python sürümünüz eski olabilir; `python --version` ile kontrol edin (3.11+ önerilir) |

## 7. Dizin yapısı

```
health/domain/      enum'lar, değiştirilemez veri modelleri, hata tipleri
health/interfaces/  tüm soyutlamalar (ABC / Protocol)
health/patterns/    factory, proxy, observer, facade, strategy gerçeklemeleri
health/services/    alt sistem servisleri (triage, randevu, bildirim)
health/ai/          RAG motoru (embedding, vektör deposu, bilgi tabanı, sahte LLM)
health/app.py       composition root (somut sınıfların birleştirildiği yer)
tests/              unittest testleri
demo.py             uçtan uca gösterim
```
