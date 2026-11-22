# Smart AI Health & Triage Assistant

EBLG443 Tasarım Kalıpları dönem projesi – Beyan Hassani (20212013122)

## Proje ne yapıyor?

Hasta şikâyetini yazıyor; sistem bunu değerlendirip hangi poliklinik ve hangi tür randevunun (acil, genel, online) gerektiğine karar veriyor. Randevunun durumu değişince hasta ve doktora bildirim gidiyor. Tıbbi kayıtlara yalnızca yetkisi olan roller erişebiliyor.

Sistem tanı koymuyor, sadece yönlendiriyor.

## Çalıştırma

```bash
python -m unittest discover -v    # testler (64 test)
python demo.py                    # örnek senaryo
```

Python 3.11 ve üstü yeterli. Ek kütüphane gerekmiyor, internet de gerekmiyor.
Ayrıntılar: [KURULUM.md](KURULUM.md) ve [TEST.md](TEST.md).

## Kullandığım tasarım kalıpları

| Kalıp | Ne için kullandım | Ana sınıflar | Nerede |
|---|---|---|---|
| Factory Method | Acil, genel ve online randevular farklı davranıyor (öncelik, süre, zaman). Üretimi Creator sınıflarına bıraktım. | `AppointmentCreator`, `Emergency/General/OnlineAppointmentCreator`, `Appointment` | `health/interfaces/appointment.py`, `health/patterns/factory/` |
| Proxy | Tıbbi kayda erişimi rol kontrolüyle koruyor, erişimleri kaydediyor, gerçek kaydı ancak gerektiğinde yüklüyor. | `IMedicalRecord`, `MedicalRecordProxy`, `RealMedicalRecord` | `health/patterns/proxy/` |
| Facade | Triage, randevu oluşturma, kayıt ve bildirim adımlarını tek bir metotta topluyor. | `HealthSystemFacade` | `health/patterns/facade/facade.py` |
| Observer | Randevu durumu değişince hasta ve doktor haberdar oluyor. | `AppointmentSubject`, `PatientObserver`, `DoctorObserver` | `health/patterns/observer/` |
| Strategy | Ciddiyet skorunun nasıl hesaplanacağını değiştirebilmek için. | `SeverityScoringStrategy` ve üç somut strateji | `health/interfaces/scoring.py`, `health/patterns/strategy/` |

Kodda her kalıp rolünün üstünde şöyle bir yorum var:

```python
# Kalıp: Factory Method | Rol: ConcreteCreator
```

Hepsini görmek için: `grep -rn "# Kalıp:" health`

## Yapay zekâ kısmı

Şikâyet metni vektöre çevriliyor, bilgi tabanındaki en benzer dokümanlar kosinüs benzerliğiyle bulunuyor ve ciddiyet skoru Strategy ile hesaplanıyor.

- Göğüs ağrısı gibi kritik belirtiler RAG'e sorulmadan doğrudan acile yönlendiriliyor.
- Karar kodla veriliyor. LLM yalnızca açıklama metni yazıyor; internetsiz çalışan sahte bir LLM kullandım.
- Bilgi tabanı örnek veridir, tıbbi tavsiye değildir.
- Kullandığım embedding yöntemi basit; kelimelerin anlamını anlamıyor, sadece harf ve kelime benzerliğine bakıyor.

## Klasörler

- `health/domain/` – veri modelleri ve enum'lar
- `health/interfaces/` – soyut sınıflar ve Protocol'ler
- `health/patterns/` – kalıpların gerçeklemeleri
- `health/services/` – triage, randevu ve bildirim servisleri
- `health/ai/` – RAG kısmı (embedding, vektör deposu, bilgi tabanı)
- `health/app.py` – parçaların birleştirildiği yer
- `tests/` – testler
- `demo.py` – örnek senaryo

## Kaynaklar ve yapay zekâ kullanımı

- Harici kütüphane kullanmadım, sadece Python standart kütüphanesi var.
- Projeyi geliştirirken yapay zekâ kod asistanı (Claude, Anthropic) kullandım. Bunu raporumda da belirttim.
- Kaynaklar: Head First Design Patterns (2. Sürüm), Gamma ve ark., Design Patterns (1994).
