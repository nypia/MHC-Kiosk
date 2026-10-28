# MHC Kahve Kiosku: gerçekçi model ve yapım animasyonu

5,0 × 3,0 × 3,0 m'lik MHC Kahve kioskunun Blender'da Python ile prosedürel olarak kurulan, Cycles ile fotogerçekçi render alınan modeli ve 45 saniyelik yapım animasyonu.

## Animasyon akışı (24 fps, 1080 kare)

| Süre | Aşama |
|---|---|
| 0–3 sn | Boş meydan, beton platform dökülür |
| 3–8 | Çelik şasi: taban çerçevesi, kirişler, döşeme plakası, dikmeler, lentolar, üst çerçeve |
| 8–14 | Sandviç paneller (RAL 7016 dış / RAL 9010 iç, PIR çekirdek) tek tek gelir, çatı paneli oturur |
| 14–17 | Pencere ve kapı boşlukları kesilir, parçalar dışarı devrilir |
| 17–23 | Süpürgelik, siyah karkas çıtaları, ardından ~190 ceviz çıta köşeden köşeye çakılır |
| 23–27 | Üst banda Alucobond kasetler çevrelenir, parapet kapağı, logo diskleri ve tabela takılır |
| 27–31 | Doğramalar, menü ekranı, camlar, kapı, bar rafları; ekran titreyerek açılır, LED yanar |
| 31–33 | Çatı modülü vinçle kalkar |
| 33–40 | Zemin, dolaplar, tezgâhlar, raflar; espresso, değirmen, tost ve çay makinesi, evye, buzdolabı, küçük detaylar |
| 40–45 | Çatı geri oturur, iç ışıklar yanar, akşamüstü tonu, teras kurulur, servis kapağı açılır, final açısı |

## Kendi bilgisayarınızda render (önerilen: GPU'lu makine)

Gereken: **Blender 4.2 veya üstü** (5.x test edildi) ve internet (dokular ilk seferde iner).

```bash
git clone <repo> && cd mhc-kiosk
python fetch_assets.py --final            # 4K doku + 8K HDRI → assets/ (yaklaşık 250 MB)
blender -b -P build.py                    # sahneyi kurar, kiosk.blend'i yeniden yazar
blender -b kiosk.blend -P render.py -- --final    # 1920×1080 animasyon → out/final/kiosk_build.mp4
blender -b kiosk.blend -P render.py -- --final --stills   # 3840×2160 C01–C04 → out/final/stills/
```

- Windows'ta `blender` komutu yerine tam yolu yazın, örneğin `"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe"`. `python` yoksa `fetch_assets.py` betiğini Blender'ın kendi Python'u ile de çalıştırabilirsiniz: `blender -b -P fetch_assets.py -- --final`.
- GPU otomatik seçilir (OptiX → CUDA → HIP → Metal → oneAPI). Bulunamazsa CPU kullanılır.
- Kareler `out/final/frames/0001.png …` olarak tek tek yazılır. Render yarıda kesilirse aynı komut kaldığı yerden devam eder.
- Sistemde `ffmpeg` varsa MP4 onunla kodlanır, yoksa Blender'ın kendi sequencer'ı kullanılır.
- Hızlı kontrol için: `-- --preview --step 4` (960×540, 24 örnek, her 4. kare).
- Kaba süre tahmini: RTX 3070 sınıfı bir kartta 1080p/160 örnekle kare başına 15–40 sn, yani tüm animasyon 5–10 saat.

`kiosk.blend` Blender'da doğrudan açılabilir. Ancak doku yolları `assets/` klasörüne göreli olduğundan önce `fetch_assets.py` çalıştırılmalıdır.

## Üretim paftaları (usta için)

`docs/uretim/MHC_Kiosk_Uretim_Paftalari.pdf`: A3, 12 pafta. PNG önizlemeler `docs/uretim/png/` klasöründe.

| No | Pafta |
|---|---|
| 00 | Kapak, genel notlar, malzeme ve ana ölçüler |
| 01 | Plan ve 4 görünüş (1:40) |
| 02 | Kesit A-A, duvar ve saçak detayları |
| 03 | Montaj sırası (8 adım, 3D görselli) |
| 04 | Çelik şasi planı, çerçeve görünüşleri, kesim listesi |
| 05 | Yuvarlak köşe detayı: köşe modülü KM, R değerleri |
| 06 | Sandviç panel ve köşe modülü açınımı + panel listesi |
| 07 | Çıta ve karkas açınımı, çıta kesim listesi, vida adedi |
| 08 | Alucobond kaset açınımı (K01–K16), açınım ölçüleri, diğer kaplamalar |
| 09 | Pencere, servis kapağı, ekran yeri, kapı |
| 10 | Teknik asma kat (+2500) ve gizli kanallı klima yerleşimi |
| 11 | Çatı planı, logo ve tabela alanları, toplam metraj |

Bütün ölçüler 3D modelle aynı kaynaktan (`kiosk/config.py` + `kiosk/layout.py`) hesaplanır. Ölçü değişince paftaları yeniden üretmek için:

```bash
pip install matplotlib
python make_drawings.py            # tüm set → docs/uretim/
python render_steps.py             # (bpy) 03 numaralı paftadaki montaj görsellerini yeniler
```

Logo ve tabela grafikleri kesin değildir; paftalarda yalnızca montaj alanları vardır.

## Kod yapısı

```
kiosk/config.py      ölçüler, palet (MHC Kahve tasarım sistemi token'ları), zaman çizelgesi
kiosk/outline.py     yuvarlatılmış dikdörtgen çevre geometrisi (s = çevre boyunca yay uzunluğu,
                     d = dış yüzden içe derinlik), Blender'sız
kiosk/layout.py      parça yerleşimi ve numaraları (D, P, KM, K, Ç), pencere, asma kat; Blender'sız
kiosk/util.py        Blender mesh üreticileri, keyframe yardımcıları
kiosk/drawings/      A3 üretim paftaları (matplotlib)
kiosk/materials.py   PBR malzemeler (Poly Haven dokuları, ölçülmüş renk kalibrasyonu)
kiosk/site.py        meydan, beton platform, HDRI + güneş, teras
kiosk/shell.py       şasi, paneller, boşluklar, çıtalar, Alucobond, cam, ekran, kapı, tabela
kiosk/interior.py    zemin, tavan ve ışıklar, dolaplar, tezgâhlar, ekipman
kiosk/finale.py      çatı kaldırma/dönüş, ışıklar, akşamüstü, servis kapağı
kiosk/cameras.py     animasyon kamerası + C01–C04 sabit kameralar
kiosk/menu_art.py    menü ekranı görseli (kiosk/art/menu.png; değişince: python -m kiosk.menu_art)
build.py / render.py giriş noktaları
```

Ölçü veya süre değişiklikleri `kiosk/config.py` üzerinden yapılır. `build.py` her çalıştığında sahneyi sıfırdan kurar ve dış zarfı (5,036 × 3,036 × 3,000 m, saçak 18 mm taşıntılı) doğrular.

## Kaynaklar ve lisanslar

- HDRI `buikslotermeerplein` ile dokular `wood_table_001`, `oak_veneer_01`, `laminate_floor_02`, `concrete_floor_02` ve `concrete_pavement`: [Poly Haven](https://polyhaven.com), CC0.
- Fontlar Fraunces ve Jost: Google Fonts, SIL OFL.
