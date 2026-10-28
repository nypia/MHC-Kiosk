"""Four logo directions for MHC Mola, to choose from.

    python -m kiosk.brand_concepts   # -> kiosk/art/logo/konsept/*.svg|png + a comparison sheet

A Yol      modern lowercase "mola" over a gently curving road
B Rozet    vintage round seal, coffee bean whose crease is a road
C El yazısı warm script "Mola" with steam rising from the o
D Kemer    arch (the kiosk's rounded corners) framing a steaming cup, serif caps
"""
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from matplotlib.textpath import TextPath  # noqa: E402
from shapely import affinity  # noqa: E402
from shapely.geometry import LineString, Point, Polygon  # noqa: E402
from shapely.ops import unary_union  # noqa: E402

from . import config as C  # noqa: E402

F = C.ASSETS / "fonts"
FONT = {k: FontProperties(fname=str(F / v)) for k, v in {
    "josefin": "JosefinSans-SemiBold.ttf", "cormorant": "CormorantGaramond-SemiBold.ttf",
    "pacifico": "Pacifico-Regular.ttf", "montserrat": "Montserrat-Medium.ttf",
    "dmserif": "DMSerifDisplay-Regular.ttf", "jost": "Jost-Medium.ttf"}.items()}
OUT = C.ROOT / "kiosk" / "art" / "logo" / "konsept"
INK, CREAM, WALNUT, PAPER = "#1f1d1c", "#efe2c4", "#c08a5c", "#f4efe6"


# ---------------------------------------------------------------- geometry helpers
def glyph(ch, font, size):
    """One glyph as a shapely geometry (nonzero fill) and its advance width."""
    prop = FONT[font]
    adv = (TextPath((0, 0), ch + "|", size=size, prop=prop).get_extents().x1
           - TextPath((0, 0), "|", size=size, prop=prop).get_extents().width)
    if ch == " ":
        return None, 0.30 * size
    polys = [Polygon(p) for p in TextPath((0, 0), ch, size=size, prop=prop).to_polygons() if len(p) > 2]
    signed = [(p.buffer(0), p.exterior.is_ccw) for p in polys]
    solid = max(signed, key=lambda g: g[0].area)[1]
    geom = unary_union([g for g, c in signed if c == solid])
    holes = [g for g, c in signed if c != solid]
    if holes:
        geom = geom.difference(unary_union(holes))
    return geom, adv


def text(s, font, size, tracking=0.0, kern=None):
    """Text as one geometry starting at x=0 on the baseline; returns (geom, width)."""
    parts, x = [], 0.0
    for i, ch in enumerate(s):
        g, adv = glyph(ch, font, size)
        if g is not None:
            parts.append(affinity.translate(g, x, 0))
        x += adv + tracking * size + (kern or {}).get(i, 0.0) * size
    return unary_union(parts), x - tracking * size


def place(g, cx=None, cy=None, x0=None, y0=None):
    b = g.bounds
    dx = (cx - (b[0] + b[2]) / 2) if cx is not None else (x0 - b[0] if x0 is not None else 0)
    dy = (cy - (b[1] + b[3]) / 2) if cy is not None else (y0 - b[1] if y0 is not None else 0)
    return affinity.translate(g, dx, dy)


def stroke(pts, w, cap=1):
    return LineString(pts).buffer(w / 2, cap_style=cap, join_style=1, quad_segs=12)


def ring(cx, cy, r, w):
    return Point(cx, cy).buffer(r + w / 2, quad_segs=48).difference(Point(cx, cy).buffer(r - w / 2, quad_segs=48))


def bezier(p0, p1, p2, p3, n=48):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return list(map(tuple, (1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3))


def dashed(pts, dash, gap, w):
    """Rounded dashes along a polyline."""
    line = LineString(pts)
    out, s = [], gap / 2
    while s + dash <= line.length:
        seg = [line.interpolate(s + k * dash / 6) for k in range(7)]
        out.append(stroke([(p.x, p.y) for p in seg], w))
        s += dash + gap
    return unary_union(out)


def arc_text(s, font, size, r, mid_deg, top=True, tracking=0.0):
    """Text along a circle centred on the origin; top reads clockwise, bottom anticlockwise."""
    glyphs = [glyph(ch, font, size) for ch in s]
    advs = [a + tracking * size for _, a in glyphs]
    total = sum(advs) - tracking * size
    span = total / r
    theta = math.radians(mid_deg) + (span / 2 if top else -span / 2)
    out = []
    for (g, adv), step in zip(glyphs, advs):
        mid = theta - (adv / 2) / r if top else theta + (adv / 2) / r
        if g is not None:
            gb = g.bounds
            g0 = affinity.translate(g, -adv / 2, 0)
            if top:
                rot = math.degrees(mid) - 90
                pos = (r * math.cos(mid), r * math.sin(mid))
            else:
                rot = math.degrees(mid) + 90
                pos = ((r) * math.cos(mid), (r) * math.sin(mid))
                g0 = affinity.translate(g0, 0, -size * 0.70)
            g1 = affinity.rotate(g0, rot, origin=(0, 0))
            out.append(affinity.translate(g1, *pos))
        theta = theta - step / r if top else theta + step / r
    return unary_union(out)


# ---------------------------------------------------------------- the four concepts
def concept_a():
    """Yol: lowercase geometric 'mola' over a gently curving two-lane road."""
    word, w = text("mola", "josefin", 160, tracking=0.02)
    word = place(word, x0=0, y0=0)
    b = word.bounds
    xs = np.linspace(b[0] - 8, b[2] + 8, 80)
    mid = [(x, -34 + 7 * math.sin((x - b[0]) / (b[2] - b[0]) * math.pi * 2)) for x in xs]
    edges = unary_union([stroke([(x, y + 13) for x, y in mid], 3.2), stroke([(x, y - 13) for x, y in mid], 3.2)])
    dashes = dashed(mid, 16, 11, 4.0)
    mhc, _ = text("MHC", "montserrat", 26, tracking=0.9)
    mhc = place(mhc, x0=b[0] + 4, y0=b[3] + 16)
    return [(unary_union([word, edges, mhc]), "fg"), (dashes, "accent")]


def concept_b():
    """Rozet: round seal; a coffee bean whose crease is a road."""
    R = 100
    outer = ring(0, 0, R, 4.5)
    inner = ring(0, 0, R - 34, 1.6)
    top = arc_text("MHC MOLA", "montserrat", 19, R - 26, 90, top=True, tracking=0.32)
    bottom = arc_text("YOL ÜSTÜ", "montserrat", 13, R - 15.5, 270, top=False, tracking=0.45)
    dots = unary_union([Point(-(R - 17), 0).buffer(2.6), Point(R - 17, 0).buffer(2.6)])
    bean = affinity.rotate(affinity.scale(Point(0, 0).buffer(30, quad_segs=48), 0.78, 1.08), -28, origin=(0, 0))
    crease = bezier((-6, -36), (14, -12), (-14, 12), (6, 36))
    crease = [affinity.rotate(Point(x, y), -28, origin=(0, 0)).coords[0] for x, y in crease]
    bean = bean.difference(stroke(crease, 9.5))
    road = dashed(crease, 5, 4, 2.2)
    return [(unary_union([outer, inner, top, bottom, dots, bean]), "fg"), (road, "accent")]


def concept_c():
    """El yazısı: script 'Mola', steam curling up from the o, small MHC underneath."""
    word, w = text("Mola", "pacifico", 150)
    word = place(word, x0=0, y0=0)
    b = word.bounds
    # centre the steam on the o: its glyph starts after the M's advance
    _, adv_m = glyph("M", "pacifico", 150)
    o_geom, _ = glyph("o", "pacifico", 150)
    ob = affinity.translate(o_geom, adv_m + (b[0] - text("Mola", "pacifico", 150)[0].bounds[0]), 0).bounds
    ox = (ob[0] + ob[2]) / 2
    oy = ob[3] - 34
    steam = []
    for k, dx in enumerate((-12, 8)):
        x0, y0 = ox + dx, oy + 34
        pts = bezier((x0, y0), (x0 - 14, y0 + 18), (x0 + 16, y0 + 30), (x0 + 2, y0 + 52 + 6 * k))
        steam.append(stroke(pts, 5.0))
    mhc, mw = text("MHC", "montserrat", 22, tracking=1.0)
    mhc = place(mhc, x0=b[2] - mw - 8, y0=b[1] - 30)
    line = stroke([(b[0] + 30, b[1] - 22), (b[2] - mw - 22, b[1] - 22)], 2.2)
    return [(unary_union([word, mhc, line]), "fg"), (unary_union(steam), "accent")]


def concept_d():
    """Kemer: arch framing a steaming cup, MHC MOLA in serif capitals below."""
    w, h, r = 108, 150, 54
    arch_pts = [(-w / 2, 0)] + [(r * math.cos(t), h - r + r * math.sin(t))
                                for t in np.linspace(math.pi, 0, 60)] + [(w / 2, 0)]
    arch = stroke(arch_pts, 4.2, cap=2)
    base = stroke([(-w / 2 - 10, 0), (w / 2 + 10, 0)], 4.2, cap=2)
    # cup: rounded trapezoid body + handle + saucer
    body = Polygon([(-24, 52), (24, 52), (19, 22), (-19, 22)]).buffer(4, join_style=1)
    handle = ring(29, 40, 8.5, 4.2).difference(Polygon([(18, 20), (28, 20), (28, 60), (18, 60)]))
    saucer = stroke([(-34, 14), (34, 14)], 4.0)
    steam = unary_union([stroke(bezier((x, 66), (x - 9, 78), (x + 9, 88), (x, 102)), 3.6) for x in (-12, 0, 12)])
    name, nw = text("MHC MOLA", "cormorant", 34, tracking=0.28)
    name = place(name, cx=0, y0=-46)
    return [(unary_union([arch, base, body, handle, saucer, name]), "fg"), (steam, "accent")]


CONCEPTS = [
    ("A", "Yol", "Modern, sade: küçük harf 'mola' ve altında kıvrılan iki şeritli yol.", concept_a),
    ("B", "Rozet", "Vintage mühür: çizgisi yol olan kahve çekirdeği, çevresinde MHC MOLA · YOL ÜSTÜ.", concept_b),
    ("C", "El yazısı", "Sıcak, kafe havası: akıcı 'Mola', o harfinden yükselen buhar, altında MHC.", concept_c),
    ("D", "Kemer", "Zarif: kioskun yuvarlak hatlarını anan kemer içinde tüten fincan, serif MHC MOLA.", concept_d),
]


# ---------------------------------------------------------------- output
def _path(geom):
    verts, codes = [], []
    for g in getattr(geom, "geoms", [geom]):
        if g.is_empty:
            continue
        for r_ in [g.exterior] + list(g.interiors):
            c = list(r_.coords)
            verts += c
            codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
    return Path(np.array(verts), np.array(codes, dtype=Path.code_type))


def draw(ax, parts, fg, accent, dx=0, dy=0, k=1.0):
    for geom, key in parts:
        g = affinity.translate(affinity.scale(geom, k, k, origin=(0, 0)), dx, dy)
        ax.add_patch(PathPatch(_path(g), facecolor=accent if key == "accent" else fg, edgecolor="none", lw=0))


def bounds(parts):
    return unary_union([g for g, _ in parts]).bounds


def svg(parts, path, fg, accent, bg=None, pad=12):
    x0, y0, x1, y1 = bounds(parts)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {x1 - x0:.1f} {y1 - y0:.1f}">']
    if bg:
        out.append(f'<rect width="100%" height="100%" fill="{bg}"/>')
    for geom, key in parts:
        d = []
        for g in getattr(geom, "geoms", [geom]):
            for r_ in [g.exterior] + list(g.interiors):
                c = list(r_.coords)
                d.append("M" + " L".join(f"{x - x0:.2f} {y1 - y:.2f}" for x, y in c) + "Z")
        out.append(f'<path fill="{accent if key == "accent" else fg}" d="{" ".join(d)}"/>')
    out.append("</svg>")
    path.write_text("\n".join(out))


def sheet(path):
    """Comparison sheet: each concept on dark and on light, plus a mock-up on the kiosk band."""
    fig = plt.figure(figsize=(16, 18), dpi=110)
    fig.patch.set_facecolor("#e9e4da")
    for i, (code, name, desc, fn) in enumerate(CONCEPTS):
        parts = fn()
        x0, y0, x1, y1 = bounds(parts)
        bw, bh = x1 - x0, y1 - y0
        for j, (bg, fg) in enumerate(((INK, CREAM), (PAPER, INK))):
            ax = fig.add_axes((0.04 + j * 0.31, 0.77 - i * 0.24, 0.29, 0.19))
            ax.set_facecolor(bg)
            k = min(0.62 / bw, 0.62 / bh * (0.19 * 18) / (0.29 * 16))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, (0.19 * 18) / (0.29 * 16))
            draw(ax, parts, fg, WALNUT, dx=0.5 - k * (x0 + x1) / 2,
                 dy=(0.19 * 18) / (0.29 * 16) / 2 - k * (y0 + y1) / 2, k=k)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
        # mock-up: on a black fascia band above slats
        ax = fig.add_axes((0.66, 0.77 - i * 0.24, 0.30, 0.19))
        ratio = (0.19 * 18) / (0.30 * 16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, ratio)
        ax.add_patch(plt.Rectangle((0, ratio * 0.42), 1, ratio * 0.58, color=INK))
        for s in np.arange(0.01, 1, 0.022):
            ax.add_patch(plt.Rectangle((s, 0), 0.011, ratio * 0.42, color="#8a5a3a"))
        ax.add_patch(plt.Rectangle((0, 0), 1, ratio * 0.42, color="#2b2826", zorder=0))
        k = min(0.5 / bw, ratio * 0.44 / bh)
        draw(ax, parts, CREAM, WALNUT, dx=0.5 - k * (x0 + x1) / 2, dy=ratio * 0.71 - k * (y0 + y1) / 2, k=k)
        ax.set_xticks([])
        ax.set_yticks([])
        fig.text(0.04, 0.965 - i * 0.24, f"{code} · {name}", fontsize=20, fontproperties=FONT["jost"],
                 color=INK)
        fig.text(0.04 + 0.12, 0.965 - i * 0.24, desc, fontsize=12, fontproperties=FONT["jost"], color="#5c5650",
                 va="baseline")
    fig.savefig(path, facecolor=fig.get_facecolor())
    plt.close(fig)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for code, name, _, fn in CONCEPTS:
        parts = fn()
        svg(parts, OUT / f"{code}_{name.replace(' ', '_')}_koyu.svg", CREAM, WALNUT, INK)
        svg(parts, OUT / f"{code}_{name.replace(' ', '_')}_acik.svg", INK, WALNUT, PAPER)
    sheet(OUT / "konseptler.png")
    print(OUT / "konseptler.png")


if __name__ == "__main__":
    build()
