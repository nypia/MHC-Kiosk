"""The fabrication drawing set, one function per A3 sheet."""
import math

from .. import config as C
from .. import layout as L
from .. import outline as O
from . import geo as G
from . import views as V
from .sheet import GREY, Sheet, mm

ART = C.ROOT / "kiosk" / "art"
STEPS = ART / "steps"
FZ0, FZ1 = C.FASCIA_Z
DECK_TOP = C.CEILING_Z + C.DECK_T

GENERAL_NOTES = [
    "1. Tüm ölçüler mm'dir. Kotlar şasi alt yüzüne (±0) göredir; bitmiş iç döşeme +160.",
    "2. Çelik profiller öneridir. Statik hesap, kaynak ve bağlantı detayları yetkili mühendis onayıyla kesinleşir.",
    "3. Tüm çelik imalat sıcak daldırma galvaniz veya epoksi astar + RAL 7016 boya ile korunur.",
    "4. Köşeler R450 mm (dış çıta yüzü). Düz yüzler sandviç panel, köşeler kavisli köşe modülüdür (KM).",
    "5. Parça numaraları: D dikme · P panel · KM köşe modülü · K Alucobond kaset · Ç çıta.",
    "6. Panel ve kaset ölçüleri imalattan önce kurulmuş şasi üzerinde yerinde ölçülerek teyit edilir.",
    "7. Montaj sırası 03 numaralı paftadadır. Asma kat ve klima, çatı paneli kapanmadan yerleştirilir.",
    "8. Elektrik, su ve gider tesisatı bu setin kapsamı dışındadır; yalnızca geçiş yerleri gösterilmiştir.",
    "9. Logo (MHC Mola): ön ve sol bantta krem kanal harf, sol yanda çift taraflı Ø720 daire çıkma "
    "tabela (pafta 11).",
]

MATERIALS = [
    ("Sandviç panel (duvar)", "60 mm PIR, dış RAL 7016 antrasit, iç RAL 9010 beyaz"),
    ("Sandviç panel (çatı)", "60 mm PIR trapez, RAL 7016, %1,5 eğim"),
    ("Köşe modülü", "0,8 mm galvaniz bükme sac RAL 7016 + 50 mm taşyünü + iç sac RAL 9010"),
    ("Cephe çıtası", "40×28 mm termo ahşap (ceviz tonu) veya ahşap görünümlü alüminyum"),
    ("Karkas", "45×22 mm siyah alüminyum omega"),
    ("Alucobond", "4 mm kompozit, mat siyah (#1F1D1C), PVDF boya"),
    ("Doğrama", "siyah RAL 9005 alüminyum, 6 mm temperli cam"),
    ("Logo / tabela", "krem kanal harf (arkadan LED) + Ø720 çift taraflı daire çıkma tabela"),
]

SHEETS = []


def sheet(no, title, scale=""):
    def deco(fn):
        SHEETS.append((no, title, scale, fn))
        return fn
    return deco


# ============================================================================ 00
@sheet("00", "Kapak ve genel notlar")
def s00(sh):
    img = ART / "cover.png"
    if img.exists():
        sh.image(img, 16, 120, 220)
    sh.text(16, 274, "MHC Mola · Kiosk", size=9, weight="medium")
    sh.text(16, 264, "Üretim paftaları: şasi · sandviç panel · köşe modülü · çıta · Alucobond · cam · asma kat",
            size=3.2, color=GREY)
    y = sh.note_box(248, 276, 150, "Genel notlar", [])
    y = sh.paragraph(248, y + 1, [ln for n in GENERAL_NOTES for ln in _wrap(n, 78)], size=2.35)
    sh.text(248, y - 3, "Pafta listesi", size=2.8, weight="medium", va="top")
    rows = [[no, title, scale] for no, title, scale, _ in SHEETS]
    sh.table(248, y - 8, [("No", 12, "c"), ("Pafta", 118, "l"), ("Ölçek", 26, "c")], rows, size=2.2, row_h=4.2)
    sh.text(16, 112, "Malzeme ve renkler", size=2.8, weight="medium", va="top")
    sh.table(16, 106, [("Eleman", 52, "l"), ("Tarif", 168, "l")], [list(m) for m in MATERIALS], size=2.2, row_h=4.4)
    sh.text(16, 64, "Ana ölçüler", size=2.8, weight="medium", va="top")
    sh.table(16, 58, [("", 70, "l"), ("", 40, "r")], [
        ["Dış ölçü (çıta yüzü)", f"{mm(C.LENGTH)} × {mm(C.WIDTH)}"],
        ["Saçak dahil", f"{mm(C.LENGTH - 2 * L.FASCIA_D[0])} × {mm(C.WIDTH - 2 * L.FASCIA_D[0])}"],
        ["Toplam yükseklik", mm(C.HEIGHT)],
        ["Köşe yarıçapı", f"R{mm(C.CORNER_R)}"],
        ["Net iç yükseklik", mm(C.CEILING_Z - C.FLOOR_H)],
        ["Teknik asma kat (klima)", f"+{mm(C.CEILING_Z)} … +{mm(C.RING_Z[0])}"],
        ["Pencere boşluğu", f"{mm(C.WIN_X[1] - C.WIN_X[0])} × {mm(C.WIN_HEAD - C.WIN_SILL)}"],
        ["Kapı boşluğu (net)", f"{mm(C.DOOR_Y[1] - C.DOOR_Y[0])} × {mm(C.DOOR_HEAD - C.FLOOR_H)}"],
    ], size=2.2, row_h=4.2, header=False)


def _wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = "   " + w
        else:
            cur = (cur + " " + w).strip() if cur else w
    lines.append(cur)
    return lines


# ============================================================================ 01
@sheet("01", "Genel görünüşler ve plan", "1:40")
def s01(sh):
    p = sh.view(92, 222, 40)
    V.plan(p)
    p.caption(-C.A, -C.B - 0.85, "PLAN (+1,50 kesiti)")
    f = sh.view(292, 180, 40)
    V.elevation(f, "front")
    f.caption(-C.A, -0.75, G.FACE_TITLE["front"])
    b = sh.view(92, 70, 40)
    V.elevation(b, "back")
    b.caption(-C.A, -0.75, G.FACE_TITLE["back"])
    r = sh.view(232, 70, 40)
    V.elevation(r, "right")
    r.caption(-C.B, -0.75, G.FACE_TITLE["right"])
    lf = sh.view(342, 70, 40)
    V.elevation(lf, "left")
    lf.caption(-C.B, -0.75, G.FACE_TITLE["left"])


# ============================================================================ 02
def section_aa(v, x=0.40):
    """Cross-section through the screen bay and the ducted AC (YZ plane at x)."""
    fy, by = -C.B, C.B
    pd0, pd1 = C.PANEL_D
    # pad + ground
    v.rect(-C.B - 0.2, -C.PAD_H, C.B + 0.2, 0, fill="concrete", lw="thin")
    for side in (-1, 1):
        y_out = side * C.B
        inward = -side

        def Y(d):
            return y_out + inward * d
        # base frame 120x120x4
        v.rect(Y(0.05), 0, Y(0.17), C.FRAME_BASE_H, fill="steel", lw="thin")
        v.rect(Y(0.054), 0.004, Y(0.166), C.FRAME_BASE_H - 0.004, fill="#ffffff", lw="hair")
        # skirt
        v.rect(Y(-0.006), 0, Y(0.0), C.SKIRT_H, fill="alu", lw="thin")
        # ring beam 60x60
        v.rect(Y(0.11), C.RING_Z[0], Y(0.17), C.RING_Z[1], fill="steel", lw="thin")
        # fascia cassette (C-shape)
        f0, f1 = L.FASCIA_D
        v.rect(Y(f0), FZ0, Y(f0 + 0.004), FZ1, fill="alu", lw="thin")
        for zz in (FZ0, FZ1 - 0.004):
            v.rect(Y(f0), zz, Y(f1), zz + 0.004, fill="alu", lw=0)
        v.rect(Y(0.03), FZ0, Y(0.05), FZ1, fill="#555555", lw="hair")
        v.rect(Y(-0.022), FZ1 - 0.015, Y(0.07), FZ1 + 0.004, fill="alu", lw="thin")
    # back wall (full height)
    def Yb(d):
        return by - d
    v.rect(Yb(pd0), C.FRAME_BASE_H, Yb(pd1), C.PANEL_TOP, fill="pir", lw="thin")
    for zr in L.RAIL_Z:
        v.rect(Yb(C.BATTEN_D[0]), zr, Yb(C.BATTEN_D[1]), zr + L.RAIL_H, fill="#2b2b2b", lw=0)
    v.rect(Yb(0.0), C.SKIRT_H + 0.005, Yb(C.SLAT_D[1]), FZ0, fill="wood", lw="thin")
    # front wall around the window
    def Yf(d):
        return fy + d
    v.rect(Yf(pd0), C.FRAME_BASE_H, Yf(pd1), C.WIN_SILL, fill="pir", lw="thin")
    v.rect(Yf(pd0), C.WIN_HEAD, Yf(pd1), C.PANEL_TOP, fill="pir", lw="thin")
    v.rect(Yf(0.0), C.SKIRT_H + 0.005, Yf(C.SLAT_D[1]), C.WIN_SILL, fill="wood", lw="thin")
    v.rect(Yf(0.0), C.WIN_HEAD, Yf(C.SLAT_D[1]), FZ0, fill="wood", lw="thin")
    for zr in (0.30, 2.30):
        v.rect(Yf(C.BATTEN_D[0]), zr, Yf(C.BATTEN_D[1]), zr + L.RAIL_H, fill="#2b2b2b", lw=0)
    v.rect(Yf(0.11), C.WIN_SILL - 0.10, Yf(0.17), C.WIN_SILL, fill="steel", lw="thin")
    v.rect(Yf(0.11), C.WIN_HEAD, Yf(0.17), C.WIN_HEAD + 0.10, fill="steel", lw="thin")
    # window: liners, frame, glass
    lz = L.WIN_LINER
    v.rect(Yf(-0.018), C.WIN_SILL, Yf(C.INNER), C.WIN_SILL + lz, fill="alu", lw="thin")
    v.rect(Yf(-0.018), C.WIN_HEAD - lz, Yf(C.INNER), C.WIN_HEAD, fill="alu", lw="thin")
    pw = L.WIN_PROFILE
    for zz in (C.WIN_SILL + lz, C.WIN_HEAD - lz - pw):
        v.rect(Yf(0.06), zz, Yf(0.11), zz + pw, fill="#202020", lw=0)
    v.rect(Yf(0.081), C.WIN_SILL + lz + pw - 0.01, Yf(0.089), C.WIN_HEAD - lz - pw + 0.01, fill="glass", lw="hair")
    # menu screen + rods
    _, _, (sx, sz, sw, shh) = L.window()
    v.rect(Yf(C.INNER + 0.015), sz - shh / 2, Yf(C.INNER + 0.055), sz + shh / 2, fill="#26282a", lw="thin")
    v.line([(Yf(C.INNER + 0.035), sz + shh / 2), (Yf(C.INNER + 0.035), C.CEILING_Z)], lw="thin")
    # canopy + bar shelf
    v.rect(Yf(-L.CANOPY["depth"] + 0.01), C.WIN_HEAD + 0.035, Yf(0.01), C.WIN_HEAD + 0.065, fill="alu", lw="thin")
    v.rect(Yf(-L.BAR_SHELF["depth"]), C.WIN_SILL - L.BAR_SHELF["t"], Yf(0.0), C.WIN_SILL, fill="#d8b48a", lw="thin")
    v.line([(Yf(-0.01), C.WIN_SILL - 0.26), (Yf(-0.22), C.WIN_SILL - L.BAR_SHELF["t"])], lw="thick")
    # floor build-up
    v.rect(-C.B + 0.17, C.FRAME_BASE_H, C.B - 0.17, C.FRAME_BASE_H + 0.030, fill="ply", lw="thin")
    v.rect(-C.B + 0.11, C.FRAME_BASE_H + 0.030, C.B - 0.11, C.FLOOR_H, fill="#b9a58a", lw="thin")
    v.rect(-C.B + 0.17, 0.02, C.B - 0.17, C.FRAME_BASE_H, fill=None, lw="hair")   # joist behind
    # roof + purlins
    v.rect(-C.B + 0.05, C.PANEL_TOP, C.B - 0.05, C.ROOF_Z, fill="pir", lw="thin")
    for py in L.PURLINS_Y:
        v.rect(py - 0.02, C.RING_Z[0], py + 0.02, C.RING_Z[1], fill="steel", lw="thin")
    # service deck
    D = L.DECK
    d0 = C.CEILING_Z
    v.rect(-C.B + D["inset"], d0, C.B - D["inset"], d0 + D["board"], fill="white", lw="thin")
    v.rect(-C.B + D["inset"], d0 + D["board"], C.B - D["inset"], d0 + D["board"] + D["grid"], fill=None, lw="hair")
    v.rect(-C.B + D["inset"], d0 + D["board"] + D["grid"], C.B - D["inset"], DECK_TOP, fill="ply", lw="thin")
    for hy in D["hangers_y"]:
        v.line([(hy, DECK_TOP), (hy, C.RING_Z[0])], lw="med")
    ux, uy = D["unit"]
    aw, ad, ah = C.AC_INDOOR
    v.rect(uy - ad / 2, DECK_TOP, uy + ad / 2, DECK_TOP + ah, fill="ac", lw="thick")
    v.text(uy, DECK_TOP + ah / 2, "KLİMA İÇ ÜNİTE", size=1.8, ha="center", va="center")
    v.rect(uy - ad / 2 - 1.20, DECK_TOP + 0.01, uy - ad / 2, DECK_TOP + 0.16, fill="#dfe3e5", lw="thin")
    sx_, sy_, sw_, sd_ = D["supply"]
    v.rect(sy_ - sd_ / 2, d0 - 0.004, sy_ + sd_ / 2, DECK_TOP + 0.06, fill="#dfe3e5", lw="thin")
    rx_, ry_, rw_, rd_ = D["ret"]
    v.rect(ry_ - rd_ / 2, d0 - 0.004, ry_ + rd_ / 2, DECK_TOP + 0.12, fill="#dfe3e5", lw="thin")


@sheet("02", "Kesit A-A ve duvar detayları", "1:20 · 1:5 · 1:10")
def s02(sh):
    v = sh.view(128, 62, 20)
    section_aa(v)
    v.caption(-C.B - 0.2, -0.32, "KESİT A-A (ekran gözü ve klima ekseninden, x = +400)")
    lv = [0, C.FRAME_BASE_H, C.FLOOR_H, C.WIN_SILL, C.WIN_HEAD, FZ0, C.CEILING_Z, DECK_TOP, C.RING_Z[0],
          C.PANEL_TOP, C.ROOF_Z, FZ1]
    v.chain_v(lv, -C.B - 0.05, -9, size=1.8)
    v.dim_v(0, FZ1, -C.B - 0.05, -19)
    v.dim_v(C.FLOOR_H, C.CEILING_Z, 1.28, 0, text=f"{mm(C.CEILING_Z - C.FLOOR_H)} net iç yükseklik", ext=False)
    v.dim_v(DECK_TOP, C.RING_Z[0], -1.26, 0, text=f"{mm(C.RING_Z[0] - DECK_TOP)} plenum", ext=False)
    v.dim_h(-C.B, C.B, 0, -14)
    for z, lab in ((0, "±0 şasi altı"), (C.FLOOR_H, "+160 bitmiş döşeme"), (C.CEILING_Z, "+2500 asma tavan"),
                   (FZ1, "+3000 parapet")):
        v.level(C.B + 0.30, z, lab)
    # labels on the outside of the back wall (right)
    xr = v.p(C.B, 0)[0] + 24
    right = [
        (C.B - 0.014, 1.75, "Çıta 40×28 @80"),
        (C.B - 0.04, 1.32, "Karkas Ω 45×22 (+300 / +1300 / +2300)"),
        (C.B - 0.08, 0.9, "Sandviç panel 60 mm PIR"),
        (C.B - 0.11, 0.06, "Taban çerçeve 120×120×4"),
        (C.B - 0.14, C.RING_Z[0] + 0.03, "Üst çerçeve 60×60×3"),
        (C.B - 0.016, 2.75, "Alucobond kaset 4 mm"),
    ]
    v.leaders(right, xr, dy=3)
    # labels inside the section (left part of the interior)
    xl = v.p(-0.9, 0)[0]
    inside = [
        (-C.B + 0.085, 1.85, "6 mm temperli cam"),
        (-C.B + C.INNER + 0.035, 1.55, "55\" menü ekranı"),
        (-C.B - 0.02, C.WIN_HEAD + 0.05, "Saçak + LED şerit"),
        (-C.B - 0.15, C.WIN_SILL - 0.02, "Dış bar rafı 300"),
        (-C.B + 0.14, C.WIN_SILL - 0.05, "Denizlik kirişi 60×100"),
        (-C.B + 0.14, C.WIN_HEAD + 0.05, "Lento 60×100"),
        (L.DECK["supply"][1], C.CEILING_Z, "Lineer üfleme menfezi"),
        (0.2, C.FLOOR_H - 0.01, "2×15 kontrplak + 10 kaplama"),
    ]
    v.leaders(inside, xl, dy=-4, gap=4.4)
    top = [
        (0.0, C.ROOF_Z - 0.01, "Çatı paneli 60 mm, %1,5 eğim"),
        (L.PURLINS_Y[1], C.RING_Z[0] + 0.02, "Aşık 60×40"),
        (L.DECK["unit"][1], DECK_TOP + 0.15, "Kanallı klima iç ünitesi (h ≤ 200)"),
        (L.DECK["hangers_y"][1], 2.70, "M10 askı"),
        (0.9, DECK_TOP - 0.01, "Asma kat: 6 beyaz panel + 40×40 ızgara + 18 kontrplak"),
    ]
    v.leaders(top, xr, dy=30, gap=4.4)

    # detail 1: horizontal wall section (straight wall at a post), 1:5
    d = sh.view(318, 258, 5)
    for k in range(-2, 3):
        u = k * C.SLAT_PITCH
        d.rect(u - C.SLAT_W / 2, -C.SLAT_D[1], u + C.SLAT_W / 2, 0, fill="wood", lw="thin")
    d.rect(-0.2, -C.BATTEN_D[1], 0.2, -C.BATTEN_D[0], fill="#2b2b2b", lw="thin")
    d.rect(-0.2, -C.PANEL_D[1], 0.2, -C.PANEL_D[0], fill="pir", lw="thin")
    d.rect(-0.03, -0.17, 0.03, -0.11, fill="steel", lw="thin")
    d.rect(-0.027, -0.167, 0.027, -0.113, fill="#ffffff", lw="hair")
    d.chain_v([0, -C.SLAT_D[1], -C.BATTEN_D[1], -C.PANEL_D[1], -0.17], -0.2, -5, size=1.8)
    d.chain_h([-C.SLAT_W / 2, C.SLAT_W / 2, C.SLAT_PITCH - C.SLAT_W / 2, C.SLAT_PITCH + C.SLAT_W / 2], 0, 5, size=1.8)
    xr = d.p(0.2, 0)[0] + 6
    for u, vv, t, y in ((0.12, -0.014, "Çıta, A2 paslanmaz vida ile karkasa", 262),
                        (0.15, -0.039, "Ω karkas, panele 2 vida / 600", 256),
                        (0.17, -0.08, "Sandviç panel 60 mm", 250),
                        (0.02, -0.14, "Dikme 60×60×3", 244)):
        d.leader_to(u, vv, t, xr, y, size=1.9)
    d.text(-0.2, 0.012, "DIŞ", size=1.8, color=GREY)
    d.caption(-0.2, -0.20, "DETAY 1 · Düz duvar yatay kesiti (+1300)", size=2.6)

    # detail 2: fascia / parapet vertical section, 1:10
    e = sh.view(318, 92 - 225, 10)
    f0, f1 = L.FASCIA_D
    e.rect(f0, FZ0, f0 + 0.004, FZ1, fill="alu", lw="thin")
    for zz in (FZ0, FZ1 - 0.004):
        e.rect(f0, zz, f1, zz + 0.004, fill="alu", lw=0)
    e.rect(0.03, FZ0, 0.05, FZ1, fill="#555555", lw="thin")
    e.rect(-0.022, FZ1 - 0.015, 0.07, FZ1 + 0.004, fill="alu", lw="thin")
    e.rect(C.PANEL_D[0], 2.25, C.PANEL_D[1], C.PANEL_TOP, fill="pir", lw="thin")
    e.rect(0.11, C.RING_Z[0], 0.17, C.RING_Z[1], fill="steel", lw="thin")
    e.rect(0.05, C.PANEL_TOP, 0.40, C.ROOF_Z, fill="pir", lw="thin")
    e.line([(0.05, C.ROOF_Z), (0.05, FZ1 - 0.015)], lw="thick")
    e.rect(0.0, 2.25, C.SLAT_D[1], FZ0, fill="wood", lw="thin")
    e.rect(C.BATTEN_D[0], 2.30, C.BATTEN_D[1], 2.30 + L.RAIL_H, fill="#2b2b2b", lw=0)
    for zz in (FZ0 + 0.06, FZ1 - 0.10):
        e.rect(-0.01, zz, 0.03, zz + 0.004, fill="#888888", lw="hair")
    e.chain_v([FZ0, FZ1], f0, -6, size=1.8)
    e.dim_h(f0, 0.0, FZ0, -6, size=1.8)
    xr = e.p(0.40, 0)[0] + 6
    e.leaders([(0.02, FZ1 - 0.005, "Parapet kapağı, damlalıklı"),
                (0.05, C.ROOF_Z + 0.02, "Su yalıtımı parapete 150 mm kıvrılır"),
                (0.14, C.RING_Z[0] + 0.03, "Üst çerçeve 60×60×3"),
                (f0, 2.70, "Alucobond kaset 4 mm, 30 mm kıvrık dönüş"),
                (0.01, FZ0 + 0.062, "Al askı köşebendi 40×40 + kaset pimi"),
                (0.014, 2.33, "Çıta üst ucu, karkas +2300")], xr, dy=4, size=1.9)
    e.caption(-0.05, 2.20, "DETAY 2 · Saçak ve parapet düşey kesiti", size=2.6)


# ============================================================================ 03
STEP_TEXT = [
    ("01_sasi", "1 · Şasi", ["Taban çerçeve 120×120×4 (köşeler hadde bükümlü) ve 5 ara",
                            f"kiriş kaynatılır. {len(L.posts())} dikme (D01–D{len(L.posts()):02d}), lento, denizlik,",
                            "köşe kaburgaları ve üst çerçeve kurulur. Köşegen farkı ≤ 3 mm."]),
    ("02_panel", "2 · Sandviç panel + çatı", [f"Düz yüzlere 60 mm paneller (P01–P{sum(1 for p in L.panels() if not p['curved']):02d}), köşelere kavisli",
                                             "köşe modülleri (KM1–KM4). Çatı paneli %1,5 eğimle",
                                             "kapanır (önce 7. adımdaki asma kat iskeleti asılır)."]),
    ("03_bosluk", "3 · Boşluklar", [f"Pencere {mm(C.WIN_X[1] - C.WIN_X[0])}×{mm(C.WIN_HEAD - C.WIN_SILL)} ve kapı {mm(C.DOOR_Y[1] - C.DOOR_Y[0])}×{mm(C.DOOR_HEAD - C.SKIRT_H)} boşlukları",
                                    "lento/denizlik hizasından kesilir; kesik panel",
                                    "kenarları söve kaplamasıyla kapanır (pafta 09)."]),
    ("04_cita", "4 · Karkas ve çıta", ["Süpürgelik, siyah Ω karkas (+300 / +1300 / +2300),",
                                       f"ardından {len(L.slats()[0])} adet 40×28 çıta, ~80 mm aksla, ön-sol",
                                       "köşeden başlayarak vidalanır (pafta 07)."]),
    ("05_alucobond", "5 · Alucobond saçak", ["Saçak bandına 16 kaset (K01–K16) askı profillerine",
                                             "asılır, derz 8 mm, parapet kapağı takılır (pafta 08).",
                                             "Kanal harf logo ve daire tabela takılır (pafta 11)."]),
    ("06_cam_kapi", "6 · Cam, ekran, kapı", ["Siyah doğrama, 6 mm temperli camlar, sürgülü servis",
                                            "kapağı, 55\" menü ekranı, kapı, pencere saçağı (LED)",
                                            "ve bar rafları monte edilir (pafta 09)."]),
    ("07_asma_kat", "7 · Teknik asma kat + klima", ["+2500'de asma kat ızgarası M10 askılarla aşıklara",
                                                     "asılır; kontrplak, kanallı klima iç ünitesi,",
                                                     "menfezler, bakım kapağı (pafta 10)."]),
    ("08_final", "8 · Teslim", ["Tesisat, iç mobilya ve ekipman yerleşimi sonrası",
                                "son kontroller: su testi (çatı), LED ve ekran,",
                                "kapı/servis kapağı ayarları."]),
]


@sheet("03", "Montaj sırası")
def s03(sh):
    cw, gap = 93.0, 4.0
    for i, (img, title, lines) in enumerate(STEP_TEXT):
        col, row = i % 4, i // 4
        x = 17 + col * (cw + gap)
        ytop = 282 - row * 118
        path = STEPS / f"{img}.png"
        h = cw * 2 / 3
        if path.exists():
            sh.image(path, x, ytop - h, cw, h)
        else:
            sh.rect(x, ytop - h, x + cw, ytop, fill="#eeeeee", lw="thin")
        sh.rect(x, ytop - h, x + cw, ytop, fill=None, lw="thin")
        sh.text(x, ytop - h - 5, title, size=3.0, weight="medium")
        sh.paragraph(x, ytop - h - 7.5, lines, size=2.2, gap=1.5)


# ============================================================================ 04
def _frame_rows():
    st = 2 * O.HX
    sd = 2 * O.HY
    arc = lambda d: math.pi / 2 * (O.R - d)  # noqa: E731
    posts = L.posts()

    def between(role):
        a, b = sorted(L.loop_pos(sv) for _, sv, r in posts if r == role)
        return b - a - 0.06
    win_l = between("pencere sövesi")
    door_l = between("kapı sövesi")
    rows = [
        ("T1", "Taban çerçeve, ön/arka düz", "120×120×4", st, 2),
        ("T2", "Taban çerçeve, yan düz", "120×120×4", sd, 2),
        ("T3", f"Taban çerçeve köşe yayı R{mm(O.R - 0.11)} eksen", "120×120×4", arc(0.11), 4),
        ("T4", "Taban ara kiriş", "100×50×3", 2 * (C.B - 0.17), len(L.JOIST_X)),
        ("D", f"Dikme D01–D{len(posts):02d}", "60×60×3", C.RING_Z[0] - C.FRAME_BASE_H, len(posts)),
        ("L1", "Pencere lentosu", "60×100×3", win_l, 1),
        ("L2", "Pencere denizlik kirişi", "60×100×3", win_l, 1),
        ("L3", "Kapı lentosu", "60×100×3", door_l, 1),
        ("K", f"Köşe kaburgası R{mm(O.R - 0.12)} eksen (+1300, +2300)", "40×20×2", arc(0.12), 4 * len(L.RIB_Z)),
        ("Ü1", "Üst çerçeve, ön/arka düz", "60×60×3", st, 2),
        ("Ü2", "Üst çerçeve, yan düz", "60×60×3", sd, 2),
        ("Ü3", f"Üst çerçeve köşe yayı R{mm(O.R - 0.14)} eksen", "60×60×3", arc(0.14), 4),
        ("A", "Çatı aşığı (y = −700 / 0 / +700)", "60×40×2", 2 * (C.A - 0.17), len(L.PURLINS_Y)),
        ("M1", "Asma kat taşıyıcı", "40×40×2", 2 * (C.B - 0.17), len(L.DECK["carriers_x"])),
        ("M2", "Asma kat çevre köşebendi", "L40×40×4", G.perimeter(0.17), 1),
        ("M3", "Asma kat askısı", "M10 dişli + L40", C.RING_Z[0] - DECK_TOP,
         len(L.DECK["carriers_x"]) * len(L.DECK["hangers_y"])),
    ]
    return rows


def chassis_plan(v, label_size=2.0):
    """Base frame, joists, posts (numbered), lifting feet, with dimensions."""
    v.poly(G.band(0, O.TOTAL, 0.05, 0.17), fill="steel", lw="thin")
    v.poly(G.ring(0.05), fill=None, lw="thin")
    v.poly(G.ring(0.17), fill=None, lw="thin")
    for x in L.JOIST_X:
        v.rect(x - 0.025, -(C.B - 0.17), x + 0.025, C.B - 0.17, fill="steel", lw="thin")
    for pid, s, role in L.posts():
        x, y = O.at(s, 0.14)
        tx, ty = O.tangent2(s)
        nx, ny = -ty, tx
        c = [(x + tx * a + nx * b, y + ty * a + ny * b) for a, b in ((-.03, -.03), (.03, -.03), (.03, .03), (-.03, .03))]
        v.poly(c, fill="#2b2b2b", lw="thin", z=4)
        lx, ly = O.at(s, 0.30)
        v.text(lx, ly, pid, size=label_size, ha="center", va="center", weight="medium")
    for cx, cy in ((O.HX, O.HY), (-O.HX, O.HY), (-O.HX, -O.HY), (O.HX, -O.HY)):
        v.circle(cx + math.copysign(O.R - 0.11, cx) * 0.707, cy + math.copysign(O.R - 0.11, cy) * 0.707, 0.04,
                 fill="#ffffff", lw="thin", z=5)
    v.dim_h(-C.A + 0.05, C.A - 0.05, -C.B, -22)
    v.chain_h([-C.A + 0.05] + list(L.JOIST_X) + [C.A - 0.05], -C.B, -14)
    v.dim_v(-C.B + 0.05, C.B - 0.05, C.A, 20)
    v.chain_v([-C.B + 0.05, -(C.B - 0.17), C.B - 0.17, C.B - 0.05], C.A, 11)
    front_posts = sorted(O.at(s, 0.14)[0] for _, s, _ in L.posts() if abs(O.at(s, 0.14)[1] + C.B - 0.14) < 1e-3)
    v.chain_h([-C.A + 0.05] + front_posts + [C.A - 0.05], -C.B, -7, size=1.8)
    back_posts = sorted(O.at(s, 0.14)[0] for _, s, _ in L.posts() if abs(O.at(s, 0.14)[1] - (C.B - 0.14)) < 1e-3)
    v.chain_h([-C.A + 0.05] + back_posts + [C.A - 0.05], C.B, 7, size=1.8)
    v.radius(O.HX, O.HY, O.R - 0.11, math.radians(45), f"R{mm(O.R - 0.11)} eksen")
    v.radius(-O.HX, -O.HY, O.R - 0.05, math.radians(225), f"R{mm(O.R - 0.05)} dış")


def frame_elevation(e, face, size=1.8):
    """Steel frame of one face as seen from outside: base frame, posts, ribs, beams, ring."""
    half = G.HALF[face] - 0.05
    e.rect(-half, 0, half, C.FRAME_BASE_H, fill="steel", lw="thin")
    e.rect(-half, C.RING_Z[0], half, C.RING_Z[1], fill="steel", lw="thin")
    us = []
    for _, s, _ in L.posts():
        if G.visible(face, s) or G.facing(face, s) > 0.6:
            u = G.project(face, *O.at(s, 0.14))
            if abs(u) <= half + 1e-6:
                e.rect(u - 0.03, C.FRAME_BASE_H, u + 0.03, C.RING_Z[0], fill="steel", lw="thin")
                us.append(u)
    for zr in L.RIB_Z:
        for sgn in (-1, 1):
            e.rect(sgn * (G.HALF[face] - O.R), zr - 0.02, sgn * half, zr + 0.02, fill="steel", lw="hair")
    for name, u0, u1, z0, z1 in G.opening_on(face):
        if name == "pencere":
            e.rect(u0, z0 - 0.10, u1, z0, fill="steel", lw="thin")
        e.rect(u0, z1, u1, z1 + 0.10, fill="steel", lw="thin")
        e.rect(u0, max(z0, C.FRAME_BASE_H), u1, z1, fill=None, lw="hair")
    e.chain_v([0, C.FRAME_BASE_H] + sorted({max(z, C.FRAME_BASE_H) for _, _, _, z0, z1 in G.opening_on(face)
                                            for z in (z0, z1)})
              + [C.RING_Z[0], C.RING_Z[1]], -half, -6, size=size)
    e.chain_h([-half] + sorted(us) + [half], 0, -6, size=size)
    return half


@sheet("04", "Çelik şasi ve taşıyıcı sistem", "1:30 · 1:50")
def s04(sh):
    v = sh.view(118, 214, 30)
    chassis_plan(v)
    v.caption(-C.A, -C.B - 1.05, "ŞASİ PLANI (taban çerçeve, kirişler, dikmeler)")
    x0, y0 = v.p(-C.A, -C.B - 1.05)
    sh.text(x0, y0 - 7.5, "Beyaz daire: köşelerde ayarlı ayak M24 + kaldırma kulağı (4 adet). Köşe dikmeleri "
                          "yay teğet noktalarındadır.", size=2.0, color=GREY, va="top")

    rows = _frame_rows()
    tot = {}
    cells = []
    for pos, name, prof, length, n in rows:
        cells.append([pos, name, prof, mm(length), n, f"{length * n:.2f}"])
        tot[prof] = tot.get(prof, 0) + length * n
    y = sh.table(246, 283, [("Poz", 10, "c"), ("Eleman", 70, "l"), ("Profil", 30, "l"), ("Boy", 15, "r"),
                            ("Adet", 11, "r"), ("Top. m", 15, "r")], cells, size=2.0, row_h=4.1)
    sh.text(246, y - 4, "Profil toplamları (fire hariç)", size=2.5, weight="medium", va="top")
    sh.table(246, y - 8, [("Profil", 50, "l"), ("Toplam m", 25, "r")],
             [[k, f"{v_:.1f}"] for k, v_ in tot.items()], size=2.0, row_h=4.0)

    # frame elevations, 1:50
    for face, ox, oy in (("front", 80, 62), ("right", 196, 62)):
        e = sh.view(ox, oy, 50)
        half = frame_elevation(e, face)
        e.caption(-half, -0.32, f"ÇERÇEVE · {G.FACE_TITLE[face].split(' (')[0]}", size=2.6)


# ============================================================================ 05
@sheet("05", "Yuvarlak köşe detayı (köşe modülü KM)", "1:5 · 1:20")
def s05(sh):
    a, b = L.ARCS[2]                       # back-left corner; all four are identical
    cx, cy = -O.HX, O.HY
    v = sh.view(0, 0, 5)
    v.ox, v.oy = 150 - cx * v.k + 0.0, 150 - cy * v.k
    s0, s1 = a - 0.32, b + 0.32
    # straight sandwich panels either side of the corner module
    for p0, p1 in ((s0, a - 0.002), (b + 0.002, s1)):
        v.poly(G.band(p0, p1, C.PANEL_D[0], C.PANEL_D[1]), fill="pir", lw="thin")
        v.poly(G.band(p0, p1, C.PANEL_D[0], C.PANEL_D[0] + 0.0006), fill="#2b2b2b", lw=0)
        v.poly(G.band(p0, p1, C.PANEL_D[1] - 0.0006, C.PANEL_D[1]), fill="#2b2b2b", lw=0)
    # corner module: bent sheets + mineral wool
    v.poly(G.band(a, b, 0.0508, 0.1092, 0.005), fill="wool", lw="thin")
    v.poly(G.band(a, b, 0.050, 0.0508, 0.005), fill="#2b2b2b", lw=0)
    v.poly(G.band(a, b, 0.1092, 0.110, 0.005), fill="#2b2b2b", lw=0)
    # rib, battens, slats
    v.poly(G.band(a, b, 0.11, 0.13, 0.005), fill="steel", lw="thin")
    v.poly(G.band(s0, s1, C.BATTEN_D[0], C.BATTEN_D[1], 0.005), fill="#2b2b2b", lw="thin")
    for _, s, segs in L.slats()[0]:
        if L.loop_pos(s0) <= L.loop_pos(s) <= L.loop_pos(s0) + (s1 - s0):
            x, y = O.at(s, 0)
            tx, ty = O.tangent2(s)
            nx, ny = O.normal2(s)
            w = C.SLAT_W / 2
            pts = [(x - tx * w, y - ty * w), (x + tx * w, y + ty * w),
                   (x + tx * w - nx * C.SLAT_D[1], y + ty * w - ny * C.SLAT_D[1]),
                   (x - tx * w - nx * C.SLAT_D[1], y - ty * w - ny * C.SLAT_D[1])]
            v.poly(pts, fill="wood", lw="thin")
    # tangent posts
    for s in (a, b):
        x, y = O.at(s, 0.14)
        tx, ty = O.tangent2(s)
        nx, ny = -ty, tx
        for half, fill in ((0.03, "steel"), (0.027, "#ffffff")):
            c = [(x + tx * p + nx * q, y + ty * p + ny * q) for p, q in ((-half, -half), (half, -half), (half, half),
                                                                       (-half, half))]
            v.poly(c, fill=fill, lw="thin" if fill == "steel" else "hair", z=4)
        v.line([O.at(s, -0.06), O.at(s, 0.20)], lw="hair", ls=(0, (8, 2, 2, 2)))
    v.text(*O.at(a, -0.075), "teğet", size=1.9, color=GREY, ha="center")
    v.text(*O.at(b, -0.075), "teğet", size=1.9, color=GREY, ha="center")
    # radii
    for d, ang, lab in ((0.0, 112, "çıta dışı"), (C.SLAT_D[1], 124, "karkas"), (0.05, 136, "dış sac"),
                        (0.11, 148, "iç sac"), (0.13, 160, "kaburga içi")):
        v.radius(cx, cy, O.R - d, math.radians(ang), f"R{mm(O.R - d)} {lab}", size=1.9)
    v.circle(cx, cy, 0.004, fill="#1a1a1a", lw=0)
    v.leaders([
        (*O.at(a - 0.2, 0.08), "Sandviç panel 60 mm (" + next(p["id"] for p in L.panels()
                                                               if abs(p["s1"] + L.PANEL_GAP - a) < 1e-6) + ", arka)"),
        (*O.at((a + b) / 2 - 0.12, 0.08), "KM: 0,8 mm galvaniz bükme sac + 50 mm taşyünü + iç sac"),
        (*O.at((a + b) / 2 + 0.15, 0.12), "Kaburga 40×20×2 hadde bükümlü (+1300, +2300)"),
        (*O.at(a, 0.15), "Teğet dikme 60×60×3"),
    ], v.p(cx + 0.40, 0)[0], dy=14, size=2.0)
    v.leaders([
        (*O.at(b + 0.2, 0.014), "Çıta 40×28, köşede radyal"),
        (*O.at(b + 0.25, 0.039), "Ω karkas, köşede bükümlü"),
        (*O.at(b, 0.05), "Birleşim: panel ucu dikmeye vidalı + lamba + mastik"),
    ], v.p(cx - 0.20, 0)[0], dy=8, gap=6, size=2.0)
    v.caption(cx - 0.45, cy - 0.40, "KÖŞE PLAN KESİTİ +1300 (arka-sol köşe, 4 köşe aynı)")
    arc_len = O.CQ
    notes = [
        "**Köşe modülü (KM) imalatı",
        f"• Yay: dış sac R{mm(O.R - 0.05)} · iç sac R{mm(O.R - 0.11)} · 90°",
        f"• Dış sac açınımı ≈ {mm(math.pi / 2 * (O.R - 0.05))} + 2×50 bindirme, h = {mm(C.PANEL_TOP - C.FRAME_BASE_H)}",
        f"• İç sac açınımı ≈ {mm(math.pi / 2 * (O.R - 0.11))} + 2×50 bindirme",
        "• Sac: 0,8 mm galvaniz, dış RAL 7016 / iç RAL 9010, silindir bükümlü",
        "• Dolgu: 50 mm taşyünü (yoğunluk ≥ 100 kg/m³), boşluk kalmayacak",
        "• Saclar kaburgalara ve teğet dikmelere 4,8 mm matkap uçlu vida @200",
        "• Panel–KM birleşimi: dikme üzerinde, iç ve dış köşe lambası + mastik",
        "",
        "**Çıta ve karkas köşede",
        f"• Çıta aksı yay üzerinde de ~{mm(L.slats()[1])} mm, çıtalar radyal",
        f"• Ω karkas R{mm(O.R - C.BATTEN_D[0])} hadde bükümlü veya 100 mm parçalı",
        f"• Köşedeki görünen yay boyu (çıta dışı) {mm(arc_len)}",
    ]
    sh.paragraph(262, 280, notes, size=2.3)
    # corner elevation (unrolled), 1:20
    e = sh.view(290, 74, 20)
    w = O.CQ
    e.rect(0, 0, w, C.FRAME_BASE_H, fill="steel", lw="thin")
    e.rect(0, C.RING_Z[0], w, C.RING_Z[1], fill="steel", lw="thin")
    for zr in L.RIB_Z:
        e.rect(0, zr - 0.02, w, zr + 0.02, fill="steel", lw="thin")
    for u in (0, w):
        e.rect(u - 0.03, C.FRAME_BASE_H, u + 0.03, C.RING_Z[0], fill="#2b2b2b", lw="thin")
    e.rect(0.03, C.FRAME_BASE_H, w - 0.03, C.RING_Z[0], fill=None, lw="hair")
    e.chain_v([0, C.FRAME_BASE_H] + [z for zr in L.RIB_Z for z in (zr - 0.02, zr + 0.02)] + list(C.RING_Z), 0, -6,
              size=1.7)
    e.dim_h(0, w, 0, -6, text=f"{mm(w)} yay")
    e.caption(-0.05, -0.22, "KÖŞE İSKELETİ (açılmış)", size=2.6)


# ============================================================================ 06
@sheet("06", "Sandviç panel ve köşe modülü açınımı", "1:40")
def s06(sh):
    v = sh.view(22, 176, 40)
    V.developed(v, z0=0, z1=C.PANEL_TOP)
    rows, area = [], 0.0
    edges = []
    for pn in L.panels():
        u0 = L.loop_pos(pn["s0"])
        u1 = u0 + (pn["s1"] - pn["s0"])
        edges += [u0, u1]
        for z0, z1, cut in pn["spans"]:
            if cut:
                v.rect(u0, z0, u1, z1, fill="cut", lw="hair")
                v.text((u0 + u1) / 2, (z0 + z1) / 2, "kesilir", size=1.8, ha="center", va="center", color=GREY,
                       bg="white")
            else:
                v.rect(u0, z0, u1, z1, fill="wool" if pn["curved"] else "#c4c9cc", lw="thin")
        v.text((u0 + u1) / 2, C.PANEL_TOP - 0.28, pn["id"], size=2.6, weight="medium", ha="center", va="center")
        width = L.length_at(pn["s0"], pn["s1"], C.PANEL_D[0])
        v.dim_h(u0, u1, 0, -6, text=mm(width), size=1.8)
        pieces = [(z0, z1) for z0, z1, cut in pn["spans"] if not cut]
        for z0, z1 in pieces:
            area += width * (z1 - z0)
        kind = "kavisli KM" if pn["curved"] else "düz panel"
        size_txt = " + ".join(f"{mm(width)}×{mm(z1 - z0)}" for z0, z1 in pieces)
        note = {"window": "pencere gözü: yatay 2 parça", "door": "kapı üstü parça"}.get(pn["kind"], "")
        if pn["curved"]:
            note = f"iç sac {mm(L.length_at(pn['s0'], pn['s1'], C.PANEL_D[1]))}"
        rows.append([pn["id"], L.FACE_NAMES[pn["face"]], kind, size_txt, note])
    v.dim_h(0, O.TOTAL, 0, -13, text=f"{mm(O.TOTAL)} açınım (çıta dış yüzü); parça ölçüleri panel dış yüzünde")
    v.chain_v([0, C.FRAME_BASE_H, C.WIN_SILL, C.WIN_HEAD, C.PANEL_TOP], 0, -6, size=1.7)
    v.caption(0, -0.75, "DUVAR AÇINIMI · dışarıdan bakış, ön-sol köşeden saat yönü tersine")
    y = sh.table(14, 128, [("No", 12, "c"), ("Cephe", 34, "l"), ("Tip", 22, "l"), ("Ölçü G × Y (mm)", 64, "l"),
                           ("Not", 58, "l")], rows, size=2.0, row_h=4.1)
    sh.text(14, y - 4, f"Toplam panel / modül yüzeyi ≈ {area:.1f} m² (boşluklar hariç)", size=2.4, weight="medium",
            va="top")
    notes = [
        "**Panel notları",
        "• Panel: 60 mm PIR, dış RAL 7016, iç RAL 9010, düz yüzde dikey montaj.",
        "• Genişlikler dış yüze göre net ölçüdür; panel üreticisinden kesimli istenir.",
        "• P02 (pencere gözü): alt 960 ve üst 700 yüksekliğinde iki yatay parça.",
        "   Alternatif: tam panel takılıp boşluk sahada kesilir (pafta 03, adım 3).",
        "• Dikey derzler dikme üzerine gelir; derz içi bütil bant + dış lamba.",
        "• Panel alt ucu taban çerçevesine, üst ucu üst çerçeveye vidalı.",
        "• Köşe modülleri (KM1–KM4) pafta 05'e göre yerinde veya atölyede üretilir.",
        f"• Panel alt kotu +{mm(C.FRAME_BASE_H)}, üst kotu +{mm(C.PANEL_TOP)}.",
    ]
    sh.paragraph(214, 126, notes, size=2.2)


# ============================================================================ 07
@sheet("07", "Çıta ve karkas açınımı", "1:40")
def s07(sh):
    v = sh.view(22, 158, 40)
    V.developed(v, z0=0, z1=C.FASCIA_Z[1])
    v.rect(0, 0, O.TOTAL, C.SKIRT_H, fill="alu", lw="thin")
    v.rect(0, FZ0, O.TOTAL, FZ1, fill="#77736f", lw="thin")
    for zr, a, b in L.rails():
        u0 = L.loop_pos(a)
        v.rect(u0, zr, u0 + (b - a), zr + L.RAIL_H, fill="#2b2b2b", lw=0)
    slats, pitch = L.slats()
    for _, s, segs in slats:
        u = L.loop_pos(s)
        for z0, z1 in segs:
            v.rect(u - C.SLAT_W / 2, z0, u + C.SLAT_W / 2, z1, fill="wood", lw=0)
    for name, s0, s1, z0, z1 in L.openings():
        u0 = L.loop_pos(s0)
        v.rect(u0, z0, u0 + (s1 - s0), z1, fill=None, lw="thin")
        v.text(u0 + (s1 - s0) / 2, (z0 + z1) / 2, name.upper(), size=2.2, ha="center", va="center")
    v.chain_v([0, C.SKIRT_H, *L.RAIL_Z, FZ0, FZ1], 0, -6, size=1.7)
    v.dim_h(0, O.TOTAL, 0, -8, text=f"{mm(O.TOTAL)} açınım")
    v.caption(0, -0.50, "ÇITA AÇINIMI · süpürgelik, karkas, çıtalar, saçak bandı")
    rows = [[f"{k}", n, f"{k * n / 1000:.1f}"] for k, n in G.slat_lengths().items()]
    total = sum(k * n for k, n in G.slat_lengths().items()) / 1000
    y = sh.table(14, 118, [("Boy mm", 22, "r"), ("Adet", 18, "r"), ("Toplam m", 22, "r")], rows, size=2.1, row_h=4.2)
    sh.text(14, y - 4, f"Toplam {sum(G.slat_lengths().values())} parça · {total:.1f} m çıta (fire hariç, +%8 alın)",
            size=2.3, weight="medium", va="top")
    rail_rows = []
    for zr in L.RAIL_Z:
        rs = [(a, b) for z, a, b in L.rails() if z == zr]
        length = sum(L.length_at(a, b, sum(C.BATTEN_D) / 2) for a, b in rs)
        rail_rows.append([f"+{mm(zr)}", len(rs), f"{length:.2f}"])
    screws = 0
    for _, s, segs in slats:
        for z0, z1 in segs:
            screws += 2 * sum(1 for zr in L.RAIL_Z if z0 <= zr <= z1 and
                              any(L.loop_pos(a) <= L.loop_pos(s) <= L.loop_pos(a) + (b - a)
                                  for z, a, b in L.rails() if z == zr))
    y2 = sh.table(100, 118, [("Karkas kotu", 26, "l"), ("Parça", 16, "r"), ("Boy m", 20, "r")], rail_rows, size=2.1,
                  row_h=4.2)
    sh.text(100, y2 - 4, f"Çıta vidası A2 4,5×40: {screws} adet (+%10)", size=2.3, weight="medium", va="top")
    notes = [
        "**Çıta",
        f"• Kesit 40×28 mm, aks {pitch * 1000:.1f} mm, ara boşluk {(pitch - C.SLAT_W) * 1000:.0f} mm.",
        "• Malzeme: termo dişbudak / termo çam (ceviz tonu yağ) veya ahşap",
        "   görünümlü alüminyum. Uç kesitler ve vida delikleri yağlanır.",
        "• Her çıta, kestiği her karkasa 2 vida ile; vida başı çıtaya gömme.",
        f"• Çıta altı +{mm(C.SKIRT_H + 0.005)}, üstü +{mm(FZ0)} (saçak altı); boşluk altı ve üstünde kısa parçalar.",
        "• Dizilim ön-sol köşe teğetinden başlar (Ç001) ve saat yönü tersine ilerler.",
        "",
        "**Karkas",
        "• 45×22 siyah eloksal Ω profil, panele 2 vida / 600 mm.",
        "• Köşelerde hadde bükümlü veya 100 mm'lik kısa parçalarla.",
        "• Boşluk kenarlarında karkas 2 mm geride biter.",
    ]
    sh.paragraph(214, 116, notes, size=2.2)


# ============================================================================ 08
@sheet("08", "Alucobond kaset, süpürgelik ve kaplamalar", "1:40 · 1:5")
def s08(sh):
    v = sh.view(22, 250 - FZ0 * 25, 40)
    V.developed(v, z0=FZ0, z1=FZ1)
    rows, area = [], 0.0
    edges = []
    for kid, s0, s1, curved in L.cassettes():
        u0 = L.loop_pos(s0)
        u1 = u0 + (s1 - s0)
        edges += [u0, u1]
        v.rect(u0, FZ0, u1, FZ1, fill="alu", lw="thin")
        v.text((u0 + u1) / 2, (FZ0 + FZ1) / 2, kid, size=2.2, weight="medium", ha="center", va="center",
               color="#efe2c4")
        w = L.length_at(s0, s1, L.FASCIA_D[0])
        v.dim_h(u0, u1, FZ0, -5, text=mm(w), size=1.8)
        h = FZ1 - FZ0
        blank = (w + 0.06, h + 0.06)
        area += blank[0] * blank[1]
        rows.append([kid, L.FACE_NAMES[L.face_of((s0 + s1) / 2)], f"R{mm(O.R - L.FASCIA_D[0])} kavisli" if curved
                     else "düz", f"{mm(w)} × {mm(h)}", f"{mm(blank[0])} × {mm(blank[1])}"])
    v.caption(0, FZ0 - 0.45, "SAÇAK KASETLERİ AÇINIMI · görünen yüz ölçüleri, derz 8 mm, ön-sol köşeden")
    y = sh.table(14, 212, [("No", 12, "c"), ("Cephe", 34, "l"), ("Tip", 24, "l"), ("Görünen G × Y", 30, "l"),
                           ("Açınım (kıvrım dahil)", 34, "l")], rows, size=2.0, row_h=4.0)
    sh.text(14, y - 4, f"Kaset levha ihtiyacı ≈ {area:.1f} m² (fire hariç)", size=2.3, weight="medium", va="top")
    # other Alucobond pieces
    win_w = C.WIN_X[1] - C.WIN_X[0]
    win_h = C.WIN_HEAD - C.WIN_SILL
    door_w = C.DOOR_Y[1] - C.DOOR_Y[0]
    door_h = C.DOOR_HEAD - C.SKIRT_H
    reveal = C.INNER + 0.018
    others = [
        ["Süpürgelik h140, çevre", f"{G.perimeter(-0.006):.2f} m", "köşeler kavisli"],
        ["Parapet kapağı, çevre", f"{G.perimeter(0.024):.2f} m", "genişlik 92 + 2 damlalık"],
        ["Pencere sövesi yan ×2", f"{mm(reveal)} × {mm(win_h)}", ""],
        ["Pencere sövesi üst / denizlik", f"{mm(reveal)} / {mm(reveal + 0.03)} × {mm(win_w)}", "denizlik 3° eğimli"],
        ["Kapı sövesi yan ×2 + üst", f"{mm(reveal)} × {mm(door_h)} / {mm(door_w)}", ""],
        ["Kapı kanadı kaplaması ×2 yüz", f"{mm(door_w - 0.05)} × {mm(door_h - 0.04)}", "çelik kasa üzerine"],
        ["Pencere saçağı (LED'li)", f"{mm(win_w + 2 * L.CANOPY['overhang'])} × {mm(L.CANOPY['depth'])}", "alt yüzde LED kanalı"],
        ["Kanal harf logo, ön", f"{mm(L.LOGO['front'][2] * L.LOGO_ASPECT)} × {mm(L.LOGO['front'][2])}",
         "40 derinlik, arkadan LED"],
        ["Kanal harf logo, sol yan", f"{mm(L.LOGO['left'][2] * L.LOGO_ASPECT)} × {mm(L.LOGO['left'][2])}",
         "40 derinlik, arkadan LED"],
        ["Daire çıkma tabela, çift taraflı", f"Ø{mm(2 * L.BLADE['r'])} × {mm(L.BLADE['t'])}", "kenarı ışıklı"],
    ]
    sh.text(160, 216, "Diğer Alucobond parçaları", size=2.6, weight="medium")
    sh.table(160, 212, [("Parça", 62, "l"), ("Ölçü", 52, "l"), ("Not", 38, "l")], others, size=2.0, row_h=4.0)
    # cassette detail 1:5
    e = sh.view(40, 0, 5)
    e.oy = 62 - FZ0 * e.k
    f0, f1 = L.FASCIA_D
    e.rect(f0, FZ0, f0 + 0.004, FZ0 + 0.30, fill="alu", lw="thin")
    e.rect(f0, FZ0, f1, FZ0 + 0.004, fill="alu", lw=0)
    e.rect(0.03, FZ0, 0.05, FZ0 + 0.30, fill="#555555", lw="thin")
    e.rect(C.PANEL_D[0], FZ0 - 0.06, C.PANEL_D[1], FZ0 + 0.30, fill="pir", lw="thin")
    e.rect(0.0, FZ0 - 0.06, C.SLAT_D[1], FZ0, fill="wood", lw="thin")
    e.rect(-0.01, FZ0 + 0.06, 0.03, FZ0 + 0.064, fill="#888888", lw="thin")
    e.dim_h(f0, f1, FZ0, -6, size=1.8)
    e.dim_v(FZ0, FZ0 + 0.004, f0, -5, text="4", size=1.8)
    e.leaders([(f0, FZ0 + 0.2, "Kaset yüzü 4 mm"), (0.01, FZ0 + 0.002, "30 mm kıvrık dönüş (V-freze)"),
               (0.0, FZ0 + 0.062, "Askı pimi + Al köşebent 40×40"), (0.04, FZ0 + 0.25, "Derz fonu, siyah")],
              e.p(0.12, 0)[0], dy=4, size=1.9)
    e.caption(-0.03, FZ0 - 0.10, "KASET ALT KENAR DETAYI", size=2.5)
    notes = [
        "**Kaset imalatı",
        "• 4 mm Alucobond (mat siyah), CNC V-freze + bükme, köşeler perçinli.",
        "• Kavisli kasetler (K01, K06, K09, K14) hadde ile R468 bükülür,",
        "   üst/alt dönüşler bükümden sonra parçalı kıvrılır.",
        "• Kasetler pimli askı sistemiyle asılır; vida görünmez.",
        "• Saçak yüzü çıta yüzünden 18 mm dışarıda.",
    ]
    sh.paragraph(160, 150, notes, size=2.1)


# ============================================================================ 09
@sheet("09", "Pencere, servis kapağı, ekran ve kapı", "1:20")
def s09(sh):
    v = sh.view(120, 150, 20)
    x0, x1 = C.WIN_X
    sill, head = C.WIN_SILL, C.WIN_HEAD
    lz = L.WIN_LINER
    v.rect(x0, sill, x1, head, fill="alu", lw="thin")
    profiles, panes, (sx, sz, sw, shh) = L.window()
    for _, cx, cz, w, h, _ in panes:
        v.rect(cx - w / 2, cz - h / 2, cx + w / 2, cz + h / 2, fill="glass", lw="hair")
    for _, cx, cz, w, h in profiles:
        v.rect(cx - w / 2, cz - h / 2, cx + w / 2, cz + h / 2, fill="#202020", lw=0)
    v.rect(sx - sw / 2, sz - shh / 2, sx + sw / 2, sz + shh / 2, fill=None, lw="thin", z=6)
    v.text(sx, sz, f"55\" ekran {mm(sw)}×{mm(shh)}\n(camın 20 mm arkasında, tavana askılı)", size=2.0,
           ha="center", va="center")
    for name, cx, cz, w, h, _ in panes:
        v.text(cx, cz - h / 2 + 0.06, name, size=1.8, ha="center", color="#20546a")
    v.rect(x0 - L.CANOPY["overhang"], head + 0.035, x1 + L.CANOPY["overhang"], head + 0.065, fill="alu", lw="thin")
    for _, a, b in L.bar_shelves():
        v.rect(a, sill - L.BAR_SHELF["t"], b, sill, fill="#d8b48a", lw="thin")
        for bx in (a + 0.12, b - 0.12):
            v.rect(bx - 0.006, sill - 0.26, bx + 0.006, sill - L.BAR_SHELF["t"], fill="#202020", lw=0)
    us = sorted({x0, x0 + lz, x1 - lz, x1} | {p[1] - p[3] / 2 for p in profiles[4:6]} | {p[1] + p[3] / 2 for p in profiles[4:6]})
    v.chain_h(us, sill - 0.26, -6, size=1.7)
    v.dim_h(x0, x1, sill - 0.26, -13)
    v.chain_v([sill, sill + lz, L.HATCH_TOP, L.HATCH_TOP + 0.04, head - lz, head], x0, -6, size=1.7)
    v.dim_v(sill, head, x0, -13)
    v.dim_v(head + 0.035, head + 0.065, x1 + L.CANOPY["overhang"], 6, text="30")
    v.caption(x0, sill - 0.60, "PENCERE GÖRÜNÜŞÜ (dıştan) · sipariş / ekran / teslim gözleri")
    rows = [[n, f"{mm(w + 0.02)} × {mm(h + 0.02)}", "6 mm temperli" + (" · dikey sürgülü" if "kapağı" in n else "")]
            for n, _, _, w, h, _ in panes]
    sh.table(250, 283, [("Cam", 34, "l"), ("Kesim ölçüsü", 34, "l"), ("Tip", 50, "l")], rows, size=2.0, row_h=4.2)
    prows = [[n, f"{mm(w)} × {mm(h)}"] for n, _, _, w, h in profiles]
    sh.table(250, 255, [("Doğrama profili", 40, "l"), ("Ölçü", 34, "l")], prows, size=2.0, row_h=4.0)
    notes = [
        "**Doğrama",
        f"• Siyah RAL 9005 alüminyum, profil yüzü {mm(L.WIN_PROFILE)} mm, cam payı 10 mm.",
        "• Servis kapağı: alt sağ göz, ray içinde 500 mm yukarı kayar,",
        "   gazlı amortisörle dengeli; kapalıyken kilitli.",
        f"• Denizlik: Alucobond, bar rafı ile aynı kotta +{mm(sill)} (iç tezgâh hizası).",
        "• Bar rafı: 40 mm masif meşe, 300 mm, siyah çelik konsol @ 600.",
        "• Pencere saçağı alt yüzünde 3000 K LED şerit, IP65.",
    ]
    sh.paragraph(250, 210, notes, size=2.1)
    # door, 1:20
    d = sh.view(70, 50, 20)
    dw = C.DOOR_Y[1] - C.DOOR_Y[0]
    dz0, dz1 = C.SKIRT_H, C.DOOR_HEAD
    d.rect(0, dz0, dw, dz1, fill="#ffffff", lw="thin")
    d.rect(0.025, dz0 + 0.02, dw - 0.025, dz1 - 0.02, fill="alu", lw="thin")
    d.line([(dw - 0.12, 0.85 - 0.0), (dw - 0.12, 1.30)], lw="thick", color="#c9cdd0")
    d.line([(-0.3, 0), (dw + 0.3, 0)], lw="thick")
    d.line([(-0.3, C.FLOOR_H), (dw + 0.3, C.FLOOR_H)], lw="hair", ls=(0, (4, 2)))
    d.dim_h(0, dw, 0, -6)
    d.chain_v([0, dz0, C.FLOOR_H, dz1], 0, -6, size=1.7)
    d.dim_v(C.FLOOR_H, dz1, dw, 6, text=f"{mm(dz1 - C.FLOOR_H)} net")
    d.caption(-0.1, -0.30, "KAPI GÖRÜNÜŞÜ (dıştan)", size=2.6)
    sh.paragraph(130, 150, [
        "**Kapı",
        f"• Boşluk {mm(dw)} × {mm(dz1 - dz0)}, net geçiş {mm(dw - 0.05)} × {mm(dz1 - C.FLOOR_H)}.",
        "• Çelik kasa + 40 mm yalıtımlı kanat, iki yüz Alucobond kaplı.",
        "• Dışa açılır, 3 menteşe, kapı kapatıcı, silindirli kilit.",
        "• Paslanmaz çekme kol 450 mm; eşik +160 bitmiş döşeme.",
    ], size=2.1)


# ============================================================================ 10
@sheet("10", "Teknik asma kat ve klima yerleşimi", "1:25 · 1:15")
def s10(sh):
    D = L.DECK
    v = sh.view(130, 214, 25)
    v.poly(G.ring(C.INNER), fill=None, lw="thin")
    v.poly(G.ring(D["inset"]), fill="#f4efe4", lw="thin")
    for x in D["carriers_x"]:
        v.rect(x - 0.02, -(C.B - D["inset"]), x + 0.02, C.B - D["inset"], fill="steel", lw="hair")
        for y in D["hangers_y"]:
            v.circle(x, y, 0.025, fill="#1a1a1a", lw=0, z=5)
    ux, uy = D["unit"]
    aw, ad, ah = C.AC_INDOOR
    v.rect(ux - aw / 2, uy - ad / 2, ux + aw / 2, uy + ad / 2, fill="ac", lw="thick", z=4)
    v.text(ux, uy, "KANALLI İÇ ÜNİTE", size=2.0, ha="center", va="center", weight="medium")
    v.rect(ux + 0.05 - 0.35, uy - ad / 2 - 1.2, ux + 0.05 + 0.35, uy - ad / 2, fill="#dfe3e5", lw="thin", z=3.5)
    sx_, sy_, sw_, sd_ = D["supply"]
    v.rect(sx_ - sw_ / 2, sy_ - sd_ / 2, sx_ + sw_ / 2, sy_ + sd_ / 2, fill="#2b2b2b", lw=0, z=4)
    rx_, ry_, rw_, rd_ = D["ret"]
    v.rect(rx_ - rw_ / 2, ry_ - rd_ / 2, rx_ + rw_ / 2, ry_ + rd_ / 2, fill=None, lw="thick", z=4)
    hx, hy, hs = D["hatch"]
    v.rect(hx - hs / 2, hy - hs / 2, hx + hs / 2, hy + hs / 2, fill=None, lw="thick", z=4)
    v.line([(hx - hs / 2, hy - hs / 2), (hx + hs / 2, hy + hs / 2)], lw="hair")
    v.line([(hx - hs / 2, hy + hs / 2), (hx + hs / 2, hy - hs / 2)], lw="hair")
    px, py, pw_, pd_, _ = D["panel"]
    v.rect(px - pw_ / 2, py - pd_ / 2, px + pw_ / 2, py + pd_ / 2, fill="#cfc9bd", lw="thin", z=4)
    lx, ly = D["lines"]
    v.circle(lx, ly, 0.03, fill="#c77a4a", lw="thin", z=5)
    v.line([(ux + aw / 2 - 0.05, uy + ad / 2), (ux + aw / 2 - 0.05, C.B - C.INNER)], lw="med", color="#3b8db0")
    v.dim_h(-(C.A - D["inset"]), C.A - D["inset"], -(C.B - D["inset"]), -16)
    v.chain_h([-(C.A - D["inset"])] + list(D["carriers_x"]) + [C.A - D["inset"]], -(C.B - D["inset"]), -9, size=1.8)
    v.dim_v(-(C.B - D["inset"]), C.B - D["inset"], C.A - D["inset"], 14)
    v.chain_v([-(C.B - D["inset"]), D["hangers_y"][0], D["hangers_y"][1], C.B - D["inset"]], C.A - D["inset"], 7,
              size=1.8)
    v.leaders([(sx_, sy_, f"Lineer üfleme menfezi {mm(sw_)}×{mm(sd_)}"),
               (ux, uy - ad / 2 - 0.6, "Üfleme kanalı 700×150 galvaniz, yalıtımlı"),
               (hx, hy, f"Bakım kapağı {mm(hs)}×{mm(hs)} (alt yüzden)"),
               (px, py, "Elektrik panosu"),
               (rx_, ry_, f"Emiş menfezi {mm(rw_)}×{mm(rd_)}"),
               (lx, ly, "Bakır hatlar, çatıdaki dış üniteye"),
               (ux + aw / 2 - 0.05, C.B - C.INNER - 0.05, "Yoğuşma hattı ≥%1, arka duvardan dışarı")],
              v.p(C.A + 0.25, 0)[0], dy=0, gap=5, size=2.0)
    v.caption(-(C.A - D["inset"]), -(C.B - D["inset"]) - 0.80, "ASMA KAT PLANI (+2564 üstünden bakış)")
    # partial section 1:10 through the unit
    e = sh.view(0, 0, 15)
    y_a, y_b = -C.B, 0.85
    e.ox = 34 - y_a * e.k
    e.oy = 56 - 2.40 * e.k
    for d0, d1, fill in ((0.0, C.SLAT_D[1], "wood"), (C.PANEL_D[0], C.PANEL_D[1], "pir")):
        e.rect(y_a + d0, 2.40, y_a + d1, C.PANEL_TOP, fill=fill, lw="thin")
    e.rect(y_a + L.FASCIA_D[0], FZ0, y_a + L.FASCIA_D[0] + 0.004, FZ1, fill="alu", lw="thin")
    e.rect(y_a + 0.11, C.RING_Z[0], y_a + 0.17, C.RING_Z[1], fill="steel", lw="thin")
    e.rect(y_a + 0.05, C.PANEL_TOP, y_b, C.ROOF_Z, fill="pir", lw="thin")
    for py_ in L.PURLINS_Y:
        if py_ < y_b:
            e.rect(py_ - 0.02, C.RING_Z[0], py_ + 0.02, C.RING_Z[1], fill="steel", lw="thin")
    d0 = C.CEILING_Z
    e.rect(y_a + D["inset"], d0, y_b, d0 + D["board"], fill="white", lw="thin")
    e.rect(y_a + D["inset"], d0 + D["board"], y_b, d0 + D["board"] + D["grid"], fill=None, lw="hair")
    e.rect(y_a + D["inset"], d0 + D["board"] + D["grid"], y_b, DECK_TOP, fill="ply", lw="thin")
    for hy_ in D["hangers_y"]:
        e.line([(hy_, DECK_TOP), (hy_, C.RING_Z[0])], lw="thick")
    e.rect(uy - ad / 2, DECK_TOP, uy + ad / 2, DECK_TOP + ah, fill="ac", lw="thick")
    e.text(uy, DECK_TOP + ah / 2, "İÇ ÜNİTE", size=2.0, ha="center", va="center")
    e.rect(sy_ + 0.06, DECK_TOP + 0.01, uy - ad / 2, DECK_TOP + 0.16, fill="#dfe3e5", lw="thin")
    e.rect(sy_ - 0.06, d0 - 0.004, sy_ + 0.06, DECK_TOP + 0.06, fill="#dfe3e5", lw="thin")
    e.chain_v([d0, d0 + D["board"], d0 + D["board"] + D["grid"], DECK_TOP, DECK_TOP + ah, C.RING_Z[0],
               C.PANEL_TOP, C.ROOF_Z], y_b, 6, size=1.7)
    e.level(y_a + 0.4, d0, "+2500 asma tavan alt yüzü", side=1)
    e.caption(y_a, 2.36, "KESİT (kısmi) · ünite ve üfleme kanalı", size=2.6)
    notes = [
        "**Asma kat",
        f"• Alt yüz +{mm(C.CEILING_Z)}: 6 mm beyaz kompozit panel (sökülebilir).",
        "• 40×40×2 taşıyıcılar 1000 aks, her biri 2 M10 askı ile aşıklara;",
        "   duvar kenarında L40×40×4 çevre köşebendine oturur.",
        "• Üstte 18 mm kontrplak servis zemini; taşıma ≤ 100 kg/m² (yalnız servis).",
        "",
        "**Klima",
        "• Gizli kanallı (slim ducted) iç ünite, h ≤ 200 mm, 9.000–12.000 BTU/h.",
        "• Üfleme: pencere üstü lineer menfez (müşteri önü + tezgâh).",
        "• Emiş: arka tarafta 600×300 menfez, filtreli.",
        "• Dış ünite çatıda, titreşim takozlu; bakır hatlar izoleli.",
        "• Yoğuşma ≥%1 eğimle arka duvardan süpürgelik altına.",
        "• Bakım kapağı ünite servis tarafına 600 mm yakınlıkta.",
    ]
    sh.paragraph(262, 126, notes, size=2.1)


# ============================================================================ 11
@sheet("11", "Çatı, logo, daire tabela ve toplam metraj", "1:50 · 1:20 · 1:10")
def s11(sh):
    v = sh.view(80, 220, 50)
    v.poly(G.ring(L.FASCIA_D[0]), fill="alu", lw="thin")
    v.poly(G.ring(0.07), fill="#b9bdc0", lw="thin")
    for k in range(-2, 3):
        v.line([(k * 1.0 - 0.6, -1.0), (k * 1.0 - 0.6 + 0.0, 1.0)], lw="hair", color="#8a8a8a")
    ao = L.AC_OUTDOOR
    v.rect(ao["x"] - ao["w"] / 2, ao["y"] - ao["d"] / 2, ao["x"] + ao["w"] / 2, ao["y"] + ao["d"] / 2, fill="#eeeeee",
           lw="thick", z=4)
    v.text(ao["x"], ao["y"], "DIŞ ÜNİTE", size=1.8, ha="center", va="center")
    drain = (C.A - 0.30, C.B - 0.30)
    v.circle(*drain, 0.05, fill="#ffffff", lw="thick", z=5)
    for start in ((-1.8, -0.9), (-0.4, -0.9), (1.0, -0.9), (-1.8, 0.5)):
        v.line([start, (drain[0] - 0.15, drain[1] - 0.08)], lw="thin", color="#3b8db0")
    v.text(-0.3, -0.2, "%1,5 eğim", size=2.4, ha="center", color="#3b8db0", weight="medium")
    v.leaders([(*drain, "Gizli süzgeç Ø75 + iniş borusu (köşe içi)"),
               (ao["x"], ao["y"] - ao["d"] / 2, "Dış ünite, titreşim takozlu"),
               (0.0, C.B - 0.04, "Parapet kapağı")], v.p(C.A + 0.3, 0)[0], dy=10, size=2.0)
    v.dim_h(-C.A, C.A, -C.B, -8)
    v.dim_v(-C.B, C.B, -C.A, -8)
    v.caption(-C.A, -C.B - 0.45, "ÇATI PLANI")
    # channel-letter logo (front) and blade sign, 1:20 / 1:10
    g = sh.view(130, 142 - 2.40 * 50, 20)
    xf, zf, hf = L.LOGO["front"]
    wf = hf * L.LOGO_ASPECT
    g.rect(-1.0, FZ0, 1.0, FZ1, fill="alu", lw="thin")
    V.logo(g, "wordmark", 0, zf, hf)
    g.dim_h(-wf / 2, wf / 2, FZ1, 6)
    g.dim_v(zf - hf / 2, zf + hf / 2, 1.0, 6)
    g.chain_v([FZ0, FZ1], -1.0, -6)
    g.caption(-1.0, FZ0 - 0.12, "ÖN BANT LOGOSU · kanal harf, ortada", size=2.6)
    B = L.BLADE
    t = sh.view(60, 0, 10)
    t.oy = 52 + B["r"] * t.k
    t.circle(0, 0, B["r"], fill="#1f1d1c", lw="thin")
    V.logo(t, "badge", 0, 0, 2 * B["r"])
    t.dim_h(-B["r"], B["r"], -B["r"], -5, text=f"Ø{mm(2 * B['r'])}")
    k = sh.view(130, t.oy, 10)
    k.rect(-B["t"] / 2, -B["r"], B["t"] / 2, B["r"], fill="#1f1d1c", lw="thin")
    k.rect(B["t"] / 2 + B["gap"], -B["r"] - 0.1, B["t"] / 2 + B["gap"] + 0.05, B["r"] + 0.1, fill="alu", lw="thin")
    for dz in B["arms"]:
        k.rect(B["t"] / 2, dz - 0.015, B["t"] / 2 + B["gap"] + 0.01, dz + 0.015, fill="#202020", lw=0)
    k.dim_h(-B["t"] / 2, B["t"] / 2, B["r"], 5)
    k.dim_h(B["t"] / 2, B["t"] / 2 + B["gap"], B["r"], 5)
    k.chain_v([-B["r"], B["arms"][0], B["arms"][1], B["r"]], -B["t"] / 2, -6, size=1.9)
    k.text(B["t"] / 2 + B["gap"] + 0.07, 0, "sol duvar\n(saçak)", size=2.0, va="center")
    t.caption(-B["r"], -B["r"] - 0.12, "DAİRE ÇIKMA TABELA · önden ve yandan", size=2.6)
    bx, by = L.blade_centre()
    hl = L.LOGO["left"][2]
    sh.paragraph(250, 180, [
        "**Logo (MHC Mola) ve tabela",
        f"• Ön bant: kanal harf logo {mm(wf)} × {mm(hf)}, ortada, krem; \"O\" içindeki",
        "   iki çubuk ceviz tonu. Harf derinliği 40, kasetten 15 mm önde, arkadan LED.",
        f"• Sol yan bant: aynı logo {mm(hl * L.LOGO_ASPECT)} × {mm(hl)}.",
        f"• Daire tabela: Ø{mm(2 * B['r'])}, kalınlık {mm(B['t'])}, çift taraflı rozet, kenarı ışıklı;",
        f"   sol duvardan {mm(B['gap'])} mm dışarıda, ön köşeye {mm(by + C.B)} mm, merkez +{mm(B['z'])}.",
        "• Konsol: 2 adet 30×12 siyah lama, saçak arkasındaki dikmeye cıvatalı.",
        "• Logo dosyaları: kiosk/art/logo (SVG / PNG).",
    ], size=2.1)

    # bill of quantities
    panels = L.panels()
    flat_area = sum(L.length_at(p["s0"], p["s1"], C.PANEL_D[0]) * (z1 - z0)
                    for p in panels if not p["curved"] for z0, z1, cut in p["spans"] if not cut)
    km_area = sum(L.length_at(p["s0"], p["s1"], C.PANEL_D[0]) * (C.PANEL_TOP - C.FRAME_BASE_H)
                  for p in panels if p["curved"])
    cass_area = sum((L.length_at(s0, s1, L.FASCIA_D[0]) + 0.06) * (FZ1 - FZ0 + 0.06) for _, s0, s1, _ in L.cassettes())
    slat_m = sum(k * n for k, n in G.slat_lengths().items()) / 1000
    rails_m = sum(L.length_at(a, b, 0.039) for _, a, b in L.rails())
    _, panes, _ = L.window()
    glass = sum((w + 0.02) * (h + 0.02) for _, _, _, w, h, _ in panes)
    steel = {}
    for _, _, prof, length, n in _frame_rows():
        steel[prof] = steel.get(prof, 0) + length * n
    rows = [
        ["Çelik 120×120×4", f"{steel['120×120×4']:.1f}", "m"],
        ["Çelik 100×50×3", f"{steel['100×50×3']:.1f}", "m"],
        ["Çelik 60×60×3", f"{steel['60×60×3']:.1f}", "m"],
        ["Çelik 60×100×3", f"{steel['60×100×3']:.1f}", "m"],
        ["Çelik 40×20×2 (bükümlü)", f"{steel['40×20×2']:.1f}", "m"],
        ["Çelik 60×40×2", f"{steel['60×40×2']:.1f}", "m"],
        ["Çelik 40×40×2 + L40", f"{steel['40×40×2'] + steel['L40×40×4']:.1f}", "m"],
        ["Kontrplak 2×15 mm (döşeme)", f"{G.rounded_area(0.11):.1f}", "m²"],
        ["Sandviç panel 60 mm (duvar)", f"{flat_area:.1f}", "m²"],
        ["Köşe modülü KM (4 adet)", f"{km_area:.1f}", "m²"],
        ["Sandviç panel 60 mm (çatı)", f"{G.rounded_area(0.05):.1f}", "m²"],
        ["Çıta 40×28", f"{slat_m:.0f}", "m"],
        ["Ω karkas 45×22", f"{rails_m:.1f}", "m"],
        ["Alucobond kaset levhası", f"{cass_area:.1f}", "m²"],
        ["Süpürgelik + parapet kapağı", f"{G.perimeter(-0.006) + G.perimeter(0.024):.1f}", "m"],
        ["Temperli cam 6 mm", f"{glass:.2f}", "m²"],
        ["Asma kat kontrplak 18 mm + beyaz panel", f"{G.rounded_area(L.DECK['inset']):.1f}", "m² ×2"],
        ["Kanallı klima (iç + dış ünite)", "1", "takım"],
    ]
    sh.text(250, 283, "Toplam metraj (fire hariç)", size=2.8, weight="medium", va="top")
    sh.table(250, 278, [("Kalem", 100, "l"), ("Miktar", 30, "r"), ("Birim", 20, "l")], rows, size=2.1, row_h=4.3)
