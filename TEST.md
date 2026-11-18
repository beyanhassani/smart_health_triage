# Test Dokümanı

Testler Python standart kütüphanesindeki `unittest` ile yazılmıştır; ek paket gerekmez.
Toplam: **64 test**, hepsi geçmektedir.

## 1. Testleri çalıştırma

| Amaç | Komut |
|---|---|
| Tüm testler | `python -m unittest discover -v` |
| Tek dosya | `python -m unittest tests.test_proxy -v` |
| Tek test | `python -m unittest tests.test_proxy.ProxyTests.test_nurse_can_read_but_not_write -v` |
| pytest ile (isteğe bağlı, kuruluysa) | `pytest -v` |

Beklenen çıktı: `Ran 64 tests ... OK`.

## 2. Test envanteri

| Dosya | Test sayısı | Neyi doğrular | İlgili kalıp |
|---|---|---|---|
| `tests/test_step1.py` | 6 | Veri modellerinin doğrulaması ve değiştirilemezliği; soyut sınıfların doğrudan örneklenememesi; Protocol'ün yapısal tipleme ile çalışması | Temel (domain / arayüzler) |
| `tests/test_factory.py` | 7 | Her Creator kendi ürününü üretir; önceliklerin sıralaması; acilin anında planlanması; genel randevunun hafta sonunu atlaması; online randevunun benzersiz bağlantısı; `creator_for` seçimi; istemcinin yalnızca soyutlamaya bağlı olması | Factory Method |
| `tests/test_proxy.py` | 9 | Rol matrisi (doktor, hemşire, hasta, yönetici); hastanın yalnızca kendi kaydını okuması; **reddedilen istekte gerçek kaydın hiç yüklenmemesi**; gerçek kaydın bir kez ve tembel yüklenmesi; denetim kaydının izinli ve reddedilen denemeleri tutması; Proxy ile gerçek kaydın aynı arayüzü paylaşması | Proxy |
| `tests/test_observer.py` | 10 | Onayda hasta ve doktorun bildirilmesi; tamamlanınca yalnızca hastanın bildirilmesi; başka hasta ve başka klinik olaylarının süzülmesi; `detach`; `attach`'in tekrarsızlığı; geçersiz durum geçişinin reddedilmesi ve bildirim gönderilmemesi; **bozuk bir gözlemcinin diğerlerini engellememesi** | Observer |
| `tests/test_facade.py` | 12 | Kural tabanlı triage (kritik semptom önceliği, klinik yönlendirme, online, varsayılan); Facade ile uçtan uca acil akışı; doğru doktorun bilgilendirilmesi; iptal/tamamlama kuralları; bilinmeyen randevu; hasta gözlemcisinin bir kez eklenmesi; tıbbi kaydın Proxy/RBAC üzerinden okunması; boş şikâyetin reddi | Facade |
| `tests/test_rag.py` | 19 | Kosinüs benzerliği; embedding'in deterministik ve normalize olması; vektör deposunun sıralaması; üç Strategy'nin aynı girdiden farklı skor üretmesi; motorun skor hesabını Strategy'ye devretmesi ve çalışma zamanında değişim; **kritik semptomda RAG'in hiç çağrılmaması**; eşleşme yoksa güvenlik ağına dönüş; LLM'in karar vermeyip yalnızca gerekçe yazması; LLM hatasında triage'ın bozulmaması; RAG'li sistemle uçtan uca akış | Strategy, RAG |
| `tests/test_pattern_tags.py` | 1 | Her kalıp rolünün kodda `# Kalıp: <ad> \| Rol: <rol>` yorumuyla işaretlenmiş olması (ders şartı) | Tüm kalıplar |

## 3. Kullanılan test teknikleri

- **Saat enjeksiyonu:** Creator'lar ve Facade, saat bilgisini dışarıdan alır; böylece "Cuma akşamı → Pazartesi 09:00" gibi zamana bağlı davranışlar deterministik test edilir.
- **Casus nesne (spy):** `SpyStore`, vektör deposuna kaç kez arama yapıldığını sayar; güvenlik ağının RAG'i atladığı bu şekilde kanıtlanır.
- **Sahte bağımlılıklar:** Çevrimdışı sahte LLM ve yerel embedding ile testler ağa bağlı değildir.
- **Alt testler (`subTest`):** Birden çok girdi için tek test içinde ayrı raporlama yapılır.
- **Sayaçlı yükleyici:** Proxy testlerinde gerçek kaydın kaç kez yüklendiği sayılır.

## 4. Kalıp – test izlenebilirliği

Her kalıbın tasarım kararı en az bir testle bağlanmıştır:

| Kalıp | Tasarım kararı | Doğrulayan test |
|---|---|---|
| Factory Method | Türler yalnızca etiketle değil davranışla da farklıdır | `test_priority_order_emergency_first`, `test_general_skips_weekend`, `test_online_has_unique_meeting_link` |
| Proxy | Yetkisiz istek gerçek kaydı yüklemez | `test_denied_request_never_loads_real_record` |
| Facade | Tek metot tüm zinciri çalıştırır | `test_emergency_flow_end_to_end` |
| Observer | Bir gözlemcinin hatası diğerlerini etkilemez | `test_failing_observer_does_not_block_others` |
| Strategy | Aynı girdiden farklı politika, farklı sonuç | `test_same_input_different_policies`, `test_policy_changes_outcome_for_same_complaint` |

## 5. Yeni test ekleme

1. `tests/` altında `test_*.py` dosyası oluşturun (veya mevcut dosyaya ekleyin).
2. `unittest.TestCase` alt sınıfı yazın; test metotlarının adı `test_` ile başlamalıdır.
3. Zamana bağlı kod için saat enjekte edin; dış servisler için sahte gerçeklemeler kullanın.
4. `python -m unittest discover -v` ile tümünün geçtiğini doğrulayın.

## 6. Sınırlamalar

- Kod kapsama (coverage) oranı ölçülmemiştir.
- Bildirim, vektör deposu ve LLM bellek içi/sahte gerçeklemelerle test edilir; gerçek e-posta, vektör veritabanı veya LLM entegrasyon testi yoktur.
- Bilgi tabanı eğitim amaçlı sentetik örneklerden oluşur; triage sonuçları tıbbi tavsiye değildir.
