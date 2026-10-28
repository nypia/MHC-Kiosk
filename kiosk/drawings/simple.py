"""Workshop set: three plain A3 sheets with big, explicit measurements.

For the fabricator on the shop floor: what to build and how big, without the
engineering detail of the full set (sheets.py). Same geometry source.
"""
import math

from .. import config as C
from .. import layout as L
from .. import outline as O
from . import geo as G
from . import views as V
from .sheet import GREY, mm
from .sheets import _frame_rows, chassis_plan, frame_elevation

FZ0, FZ1 = C.FASCIA_Z
SIMPLE = []
BIG = 3.2      # body text on these sheets (mm)


def sheet(no, title, scale=""):
    def deco(fn):
        SIMPLE.append((no, title, scale, fn))
        return fn
    return deco


def _list(sh, x, y, title, lines, size=BIG, gap=1.6):
    sh.text(x, y, title, size=size + 0.8, weight="medium", va="top")
    return sh.paragraph(x, y - (size + 0.8) * 1.9, lines, size=size, gap=gap)


# ============================================================================ 1
@sheet("1/3", "GENEL ÖLÇÜLER", "1:30 · 1:40")
def g1(sh):
    f = sh.view(128, 160, 30)
    f.ts = 1.35
    V.elevation(f, "front")
    f.caption(-C.A, -0.62, "ÖNDEN GÖRÜNÜŞ (cam tarafı)", size=3.6)
    r = sh.view(318, 160, 30)
    r.ts = 1.35
    V.elevation(r, "right")
    r.caption(-C.B, -0.62, "YANDAN GÖRÜNÜŞ (kapı tarafı)", size=3.6)
    p = sh.view(100, 84, 40)
    p.ts = 1.2
    V.plan(p, cut_mark=False)
    p.caption(-C.A, -C.B - 0.80, "ÜSTTEN (plan)", size=3.6)

    win_w, win_h = C.WIN_X[1] - C.WIN_X[0], C.WIN_HEAD - C.WIN_SILL
    rows = [
        ["Dış ölçü", f"{mm(C.LENGTH)} × {mm(C.WIDTH)}"],
        ["Yükseklik", mm(C.HEIGHT)],
        ["Köşeler yuvarlak", f"R{mm(C.CORNER_R)}"],
        ["Ön cam (tam ortada)", f"{mm(win_w)} × {mm(win_h)}"],
        ["Cam alt kenarı", f"+{mm(C.WIN_SILL)}"],
        ["Kapı (sağ yan)", f"{mm(C.DOOR_Y[1] - C.DOOR_Y[0])} × {mm(C.DOOR_HEAD - C.SKIRT_H)}"],
        ["Üst siyah bant", f"{mm(FZ1 - FZ0)} yüksek"],
        ["Alt siyah süpürgelik", f"{mm(C.SKIRT_H)} yüksek"],
        ["İç tavan", f"+{mm(C.CEILING_Z)}"],
        ["Klima boşluğu", f"+{mm(C.CEILING_Z)} … +{mm(C.RING_Z[0])}"],
    ]
    sh.text(190, 132, "ÖNEMLİ ÖLÇÜLER (mm)", size=4.0, weight="medium", va="top")
    sh.table(190, 125, [("", 62, "l"), ("", 50, "r")], rows, size=BIG, row_h=6.2, header=False)
    _list(sh, 312, 132, "YAPIM SIRASI", [
        "1. Demir şasi (sayfa 2)",
        "2. Sandviç panel giydir",
        "3. Cam ve kapı boşluğunu kes",
        "4. Siyah karkas + ahşap çıta",
        "5. Üst banda alükobond",
        "6. Cam, kapı, tavan, klima",
    ], gap=1.75)
    sh.text(312, 50, "Ölçüler milimetredir (mm).\nKotlar (+) şasinin altından ölçülür.", size=2.6,
            color=GREY, va="bottom")


# ============================================================================ 2
@sheet("2/3", "DEMİR ŞASİ", "1:30 · 1:40")
def g2(sh):
    v = sh.view(112, 214, 30)
    v.ts = 1.3
    chassis_plan(v, label_size=2.6)
    v.caption(-C.A, -C.B - 1.10, "ŞASİ ÜSTTEN (taban çerçeve + kirişler + dikmeler)", size=3.6)
    for face, ox, oy, title in (("front", 84, 52, "ÖN ÇERÇEVE"), ("right", 196, 52, "YAN ÇERÇEVE (kapı)")):
        e = sh.view(ox, oy, 50)
        e.ts = 1.3
        half = frame_elevation(e, face, size=1.9)
        e.caption(-half, -0.52, title, size=3.4)

    rows = {r[0]: r for r in _frame_rows()}

    def n_x(*keys):
        return " + ".join(f"{rows[k][4]} × {mm(rows[k][3])}" for k in keys)
    table = [
        ["120×120×4 kutu", "Taban çerçeve", n_x("T1", "T2") + f" + 4 köşe yayı R{mm(O.R - 0.11)}"],
        ["100×50×3 kutu", "Taban kirişi (her 1000)", n_x("T4")],
        ["60×60×3 kutu", "Dikme", n_x("D")],
        ["60×60×3 kutu", "Üst çerçeve", n_x("Ü1", "Ü2") + f" + 4 köşe yayı R{mm(O.R - 0.14)}"],
        ["60×100×3 kutu", "Cam altı / cam üstü / kapı üstü", n_x("L1", "L2", "L3")],
        ["40×20×2 kutu", "Köşe kaburgası (bükülü)", n_x("K") + f"  (R{mm(O.R - 0.12)})"],
        ["60×40×2 kutu", "Çatı kirişi", n_x("A")],
        ["40×40×2 kutu", "Asma tavan taşıyıcı", n_x("M1")],
    ]
    sh.text(246, 283, "DEMİR LİSTESİ", size=4.0, weight="medium", va="top")
    y = sh.table(246, 276, [("Profil", 38, "l"), ("Nerede", 50, "l"), ("Boy × adet (mm)", 76, "l")], table,
                 size=2.7, row_h=6.0)
    _list(sh, 246, y - 6, "DİKKAT", [
        "• Köşe dikmeleri radüsün başladığı yerde.",
        "• Köşegen farkı en fazla 3 mm.",
        "• Taban çerçevesi ve üst çerçeve köşelerde",
        "   hadde ile bükülür (yarıçap yukarıda).",
        "• Köşelere 4 adet ayarlı ayak + kaldırma kulağı.",
        "• Tüm demir: galvaniz veya astar + antrasit boya.",
        "• Profiller öneridir; mühendis kontrol etmeli.",
    ], size=2.9)


# ============================================================================ 3
def _wall_section(d):
    """Horizontal cut through a straight wall (outside at the top)."""
    for k in range(-2, 3):
        u = k * C.SLAT_PITCH
        d.rect(u - C.SLAT_W / 2, -C.SLAT_D[1], u + C.SLAT_W / 2, 0, fill="wood", lw="thin")
    d.rect(-0.2, -C.BATTEN_D[1], 0.2, -C.BATTEN_D[0], fill="#2b2b2b", lw="thin")
    d.rect(-0.2, -C.PANEL_D[1], 0.2, -C.PANEL_D[0], fill="pir", lw="thin")
    d.rect(-0.03, -0.17, 0.03, -0.11, fill="steel", lw="thin")
    d.rect(-0.027, -0.167, 0.027, -0.113, fill="#ffffff", lw="hair")
    d.chain_v([0, -C.SLAT_D[1], -C.BATTEN_D[1], -C.PANEL_D[1], -0.17], -0.2, -6)
    d.chain_h([-C.SLAT_W / 2, C.SLAT_W / 2, C.SLAT_PITCH - C.SLAT_W / 2], 0, 5)
    xr = d.p(0.2, 0)[0] + 8
    d.leaders([(0.12, -0.014, "Ahşap çıta 40×28"), (0.15, -0.039, "Siyah karkas (Ω)"),
               (0.17, -0.08, "Sandviç panel 60 mm"), (0.02, -0.14, "Dikme 60×60")], xr, dy=6, gap=6.5)
    d.text(-0.2, 0.012, "DIŞARISI", size=2.6, color=GREY)
    d.text(-0.2, -0.205, "İÇERİSİ", size=2.6, color=GREY, va="top")


def _facade_strip(e):
    """Vertical strip of the facade: what goes where, bottom to top."""
    w = 0.40
    e.rect(0, 0, w, C.SKIRT_H, fill="alu", lw="thin")
    for k in range(5):
        u = 0.04 + k * C.SLAT_PITCH
        e.rect(u, C.SKIRT_H + 0.005, u + C.SLAT_W, FZ0, fill="wood", lw="hair")
    e.rect(0, FZ0, w, FZ1, fill="alu", lw="thin")
    for zr in L.RAIL_Z:
        e.rect(-0.06, zr, 0.0, zr + L.RAIL_H, fill="#2b2b2b", lw=0)
    e.chain_v([0, C.SKIRT_H, FZ0, FZ1], w, 7)
    e.chain_v([0, *L.RAIL_Z], -0.06, -7, size=2.0)
    xr = e.p(w, 0)[0] + 22
    e.leaders([(w / 2, (FZ0 + FZ1) / 2, "Siyah alükobond bant"), (0.2, 1.3, "Ahşap çıta"),
               (w / 2, C.SKIRT_H / 2, "Siyah alükobond süpürgelik"),
               (-0.03, 1.32, "Karkas kotları")], xr, gap=8)


@sheet("3/3", "PANEL · ÇITA · ALÜKOBOND · CAM", "1:5 · 1:20")
def g3(sh):
    d = sh.view(70, 262, 5)
    d.ts = 1.3
    _wall_section(d)
    d.caption(-0.2, -0.27, "DUVAR KESİTİ (düz duvar)", size=3.4)
    e = sh.view(40, 62, 25)
    e.ts = 1.3
    _facade_strip(e)
    e.caption(-0.06, -0.26, "DUVAR DİZİLİMİ (aşağıdan yukarı)", size=3.4)

    # quantities, in plain words
    panels = L.panels()
    by_face = {}
    for p in panels:
        if p["curved"]:
            continue
        w = L.length_at(p["s0"], p["s1"], C.PANEL_D[0])
        for z0, z1, cut in p["spans"]:
            if not cut:
                key = (mm(w), mm(z1 - z0))
                by_face.setdefault(L.FACE_NAMES[p["face"]].split(" (")[0], []).append(key)
    panel_lines = []
    for face, sizes in by_face.items():
        counts = {}
        for k in sizes:
            counts[k] = counts.get(k, 0) + 1
        panel_lines.append(f"• {face}: " + ", ".join(f"{n} × {w}×{h}" for (w, h), n in counts.items()))
    panel_lines.append(f"• 4 köşe: kavisli sac + taşyünü, dış R{mm(O.R - C.PANEL_D[0])}, "
                       f"yükseklik {mm(C.PANEL_TOP - C.FRAME_BASE_H)}")
    y = _list(sh, 150, 283, "SANDVİÇ PANEL 60 mm (dış antrasit, iç beyaz)", panel_lines, size=2.9)
    y = _list(sh, 150, y - 4, "AHŞAP ÇITA 40×28", [
        f"• Aralık 40 mm (her {mm(L.slats()[1])} mm'de bir çıta), köşelerde de aynı.",
        "• " + ", ".join(f"{n} adet {k}" for k, n in G.slat_lengths().items()) + " mm.",
        "• Her çıta, geçtiği her karkasa 2 paslanmaz vida.",
    ], size=2.9)
    cass = L.cassettes()
    flat = [c for c in cass if not c[3]]
    curved = [c for c in cass if c[3]]
    widths = sorted({mm(L.length_at(s0, s1, L.FASCIA_D[0])) for _, s0, s1, _ in flat})
    y = _list(sh, 150, y - 4, "SİYAH ALÜKOBOND (4 mm)", [
        f"• Üst bant: {mm(FZ1 - FZ0)} yüksek, {len(cass)} parça, aralarında 8 mm derz.",
        f"   {len(flat)} düz parça ({' / '.join(widths)} geniş), {len(curved)} köşe parçası "
        f"(kavisli, {mm(L.length_at(curved[0][1], curved[0][2], L.FASCIA_D[0]))}).",
        f"• Bant, çıtanın 18 mm önünde durur.",
        f"• Alt süpürgelik: {mm(C.SKIRT_H)} yüksek, çepeçevre {G.perimeter(-0.006):.1f} m.",
        "• Cam ve kapı kenarları da alükobond ile kaplanır.",
    ], size=2.9)
    _, panes, _ = L.window()
    y = _list(sh, 150, y - 4, "CAM (6 mm temperli, siyah doğrama)", [
        f"• Toplam boşluk {mm(C.WIN_X[1] - C.WIN_X[0])} × {mm(C.WIN_HEAD - C.WIN_SILL)}, ön cephenin tam ortası.",
        "• " + ", ".join(f"{n.split(' (')[0]} {mm(w + 0.02)}×{mm(h + 0.02)}" for n, _, _, w, h, _ in panes) + ".",
        "• Sağ alttaki cam (servis kapağı) yukarı kayar.",
        "• Ortadaki camın arkasına 55\" menü ekranı asılır.",
    ], size=2.9)
    bx, by = L.blade_centre()
    B = L.BLADE
    y = _list(sh, 150, y - 4, "LOGO VE DAİRE TABELA (MHC Mola, arkadan LED)", [
        f"• Ön siyah bantın ortasına MHC Mola logosu, kanal harf: {mm(L.LOGO['front'][2] * L.LOGO_ASPECT)} geniş, "
        f"{mm(L.LOGO['front'][2])} yüksek.",
        f"• Sol yan bantta aynı logo, {mm(L.LOGO['left'][2] * L.LOGO_ASPECT)} × {mm(L.LOGO['left'][2])}.",
        f"• Sol yanda dışarı çıkan daire tabela: Ø{mm(2 * B['r'])}, {mm(B['t'])} kalın, iki yüzü yazılı.",
        f"   Duvardan {mm(B['gap'])} mm dışarıda, ön köşeye {mm(by + C.B)} mm, ortası +{mm(B['z'])}.",
    ], size=2.9)
    _list(sh, 150, y - 4, "TAVAN VE KLİMA", [
        f"• İç tavan +{mm(C.CEILING_Z)}. Üstündeki boşluğa gizli kanallı klima girer.",
        "• Tavanda 60×60 bakım kapağı bırakılır. Dış ünite çatıda.",
    ], size=2.9)
