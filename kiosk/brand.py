"""MHC Mola logo: generated as vector paths from the brand fonts.

The O of MOLA is the mark: a cup seen from above (ring) holding a pause
sign (two bars) -- a coffee break on the road. Outputs SVG + PNG lockups to
kiosk/art/logo/:

    python -m kiosk.brand
"""
import math

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import PathPatch  # noqa: E402
from matplotlib.path import Path  # noqa: E402
from matplotlib.textpath import TextPath  # noqa: E402

from . import config as C  # noqa: E402

NAME = "MHC Mola"
FONTS = C.ASSETS / "fonts"
SERIF = FontProperties(fname=str(FONTS / "Fraunces-SemiBold.ttf"))
SANS = FontProperties(fname=str(FONTS / "Jost-Medium.ttf"))
OUT = C.ROOT / "kiosk" / "art" / "logo"

COLORS = {
    "ink": "#1f1d1c",      # alucobond-black
    "cream": "#efe2c4",
    "walnut": "#c08a5c",   # oak-counter: the pause bars
}


# ---------------------------------------------------------------- geometry
def _text(s, prop, size, x=0.0, y=0.0, tracking=0.0):
    """Text as a list of (Path) glyphs laid out with extra tracking (em fraction)."""
    paths, cx = [], x
    for ch in s:
        if ch == " ":
            cx += 0.30 * size + tracking * size
            continue
        tp = TextPath((0, 0), ch, size=size, prop=prop)
        adv = TextPath((0, 0), ch + "|", size=size, prop=prop).get_extents().x1 - \
            TextPath((0, 0), "|", size=size, prop=prop).get_extents().width
        v = tp.vertices.copy()
        v[:, 0] += cx
        v[:, 1] += y
        paths.append(Path(v, np.array(tp.codes)))
        cx += adv + tracking * size
    return paths, cx - tracking * size - x


def _bounds(paths):
    xs = [p.get_extents() for p in paths]
    return min(e.x0 for e in xs), min(e.y0 for e in xs), max(e.x1 for e in xs), max(e.y1 for e in xs)


def _circle(cx, cy, r, ccw=True, n=96):
    pts = [(cx + r * math.cos(t), cy + r * math.sin(t))
           for t in [2 * math.pi * k / n * (1 if ccw else -1) for k in range(n)]]
    return pts


def _poly_path(rings):
    verts, codes = [], []
    for ring in rings:
        verts += ring + [ring[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(ring) - 1) + [Path.CLOSEPOLY]
    return Path(np.array(verts), np.array(codes, dtype=Path.code_type))


def _rounded_rect(x0, y0, x1, y1, r, n=8):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            t = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def mark(cx, cy, d):
    """The O-mark: ring + pause bars, outer diameter d. Returns (ring Path, bars Path)."""
    r = d / 2
    stroke = 0.155 * d
    ring = _poly_path([_circle(cx, cy, r, True), _circle(cx, cy, r - stroke, False)])
    bh, bw, gap = 0.40 * d, 0.095 * d, 0.085 * d
    bars = _poly_path([_rounded_rect(cx - gap / 2 - bw, cy - bh / 2, cx - gap / 2, cy + bh / 2, bw / 2),
                       _rounded_rect(cx + gap / 2, cy - bh / 2, cx + gap / 2 + bw, cy + bh / 2, bw / 2)])
    return ring, bars


def wordmark(cap=100.0, mhc=True):
    """Stacked lockup: small spaced MHC over M(mark)LA. Returns [(Path, colour key)] and bbox."""
    size = cap / 0.70
    m, w_m = _text("M", SERIF, size)
    x = w_m + 0.06 * cap
    d = cap * 1.06
    ring, bars = mark(x + d / 2, cap / 2, d)
    x += d + 0.06 * cap
    la, w_la = _text("LA", SERIF, size, x=x, tracking=0.02)
    parts = [(p, "fg") for p in m + la] + [(ring, "fg"), (bars, "accent")]
    if mhc:
        total = x + w_la
        hs = cap * 0.30 / 0.70
        top, w_top = _text("MHC", SANS, hs, tracking=0.55)
        dx = (total - w_top) / 2
        y = cap + 0.30 * cap
        for p in top:
            v = p.vertices.copy()
            v[:, 0] += dx
            v[:, 1] += y
            parts.append((Path(v, np.array(p.codes)), "fg"))
    return parts


def badge(d=100.0):
    """Round badge for the blade sign / avatar: disk, mark, MHC MOLA underneath."""
    parts = [(_poly_path([_circle(0, 0, d / 2)]), "bg")]
    ring, bars = mark(0, 0.08 * d, 0.46 * d)
    parts += [(ring, "fg"), (bars, "accent")]
    t, w = _text("MHC MOLA", SANS, 0.062 * d / 0.70, tracking=0.24)
    for p in t:
        v = p.vertices.copy()
        v[:, 0] -= w / 2
        v[:, 1] -= 0.27 * d
        parts.append((Path(v, np.array(p.codes)), "fg"))
    return parts


# ---------------------------------------------------------------- output
def _svg(parts, pal, pad, path):
    bb = _bounds([p for p, _ in parts])
    x0, y0, x1, y1 = bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad
    w, h = x1 - x0, y1 - y0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.2f} {h:.2f}" width="{w:.0f}" '
           f'height="{h:.0f}" role="img" aria-label="{NAME}">']
    if pal.get("page"):
        out.append(f'<rect width="100%" height="100%" fill="{pal["page"]}"/>')
    for p, key in parts:
        d = []
        cmd = {Path.MOVETO: "M", Path.LINETO: "L", Path.CURVE3: "Q", Path.CURVE4: "C"}
        for verts, code in p.iter_segments(simplify=False, curves=True):
            if code == Path.CLOSEPOLY:
                d.append("Z")
                continue
            pts = verts.reshape(-1, 2)
            d.append(cmd[code] + " ".join(f"{vx - x0:.2f} {y1 - vy:.2f}" for vx, vy in pts))
        out.append(f'<path fill="{pal[key]}" fill-rule="nonzero" d="{" ".join(d)}"/>')
    out.append("</svg>")
    path.write_text("\n".join(out))


def _png(parts, pal, pad, path, px=1600):
    bb = _bounds([p for p, _ in parts])
    x0, y0, x1, y1 = bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad
    w, h = x1 - x0, y1 - y0
    fig = plt.figure(figsize=(px / 200, px / 200 * h / w), dpi=200)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(pal.get("page") or (0, 0, 0, 0))
    for p, key in parts:
        ax.add_patch(PathPatch(p, facecolor=pal[key], edgecolor="none", lw=0))
    fig.savefig(path, transparent=pal.get("page") is None)
    plt.close(fig)


def _polys(parts, sx, sy, k):
    """Flatten parts to clean polygons (overlapping glyph contours merged, nonzero rule).

    Each part -> {"key", "shapes": [{"outer": ring, "holes": [ring, ...]}]}, shifted by
    (-sx, -sy) and scaled by k.
    """
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    def ring(coords):
        return [[round((x - sx) * k, 5), round((y - sy) * k, 5)] for x, y in coords]

    out = []
    for p, key in parts:
        polys = [Polygon(poly) for poly in p.to_polygons(closed_only=True) if len(poly) > 2]
        # nonzero fill: a contour inside another with opposite winding is a hole
        signed = [(pg.buffer(0), pg.exterior.is_ccw) for pg in polys]
        solid_ccw = max(signed, key=lambda gc: gc[0].area)[1]   # the biggest contour is always solid
        solids = [g for g, ccw in signed if ccw == solid_ccw]
        holes = [g for g, ccw in signed if ccw != solid_ccw]
        shape = unary_union(solids)
        if holes:
            shape = shape.difference(unary_union(holes))
        geoms = getattr(shape, "geoms", [shape])
        out.append({"key": key, "shapes": [{"outer": ring(g.exterior.coords),
                                            "holes": [ring(h.coords) for h in g.interiors]}
                                           for g in geoms if not g.is_empty]})
    return out


def export_geometry(path):
    """Logo outlines as plain JSON for Blender (no matplotlib there) and the drawings.

    wordmark: height 1, centred on (0, 0).  badge: disk diameter 1, centred; no background disk.
    """
    import json
    wm = wordmark()
    x0, y0, x1, y1 = _bounds([p for p, _ in wm])
    k = 1 / (y1 - y0)
    data = {"wordmark": {"aspect": (x1 - x0) / (y1 - y0),
                         "parts": _polys(wm, (x0 + x1) / 2, (y0 + y1) / 2, k)},
            "badge": {"parts": _polys([pp for pp in badge() if pp[1] != "bg"], 0, 0, 1 / 100.0)},
            "colors": COLORS}
    path.write_text(json.dumps(data))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    dark = {"page": COLORS["ink"], "fg": COLORS["cream"], "accent": COLORS["walnut"], "bg": COLORS["ink"]}
    light = {"page": "#f4efe6", "fg": COLORS["ink"], "accent": COLORS["walnut"], "bg": COLORS["ink"]}
    mono = {"page": None, "fg": COLORS["cream"], "accent": COLORS["cream"], "bg": COLORS["ink"]}
    badge_pal = {"page": None, "fg": COLORS["cream"], "accent": COLORS["walnut"], "bg": COLORS["ink"]}
    jobs = [
        ("logo_koyu", wordmark(), dark, 40),
        ("logo_acik", wordmark(), light, 40),
        ("logo_tek_renk", wordmark(), mono, 10),
        ("rozet", badge(), badge_pal, 2),
        ("isaret", list(zip(mark(0, 0, 100), ("fg", "accent"))), dark, 22),
    ]
    for name, parts, pal, pad in jobs:
        _svg(parts, pal, pad, OUT / f"{name}.svg")
        _png(parts, pal, pad, OUT / f"{name}.png")
        print(OUT / f"{name}.svg")
    export_geometry(OUT / "logo_geometry.json")
    clear = {"page": None, "fg": COLORS["cream"], "accent": COLORS["walnut"], "bg": COLORS["ink"]}
    _png(wordmark(), clear, 6, OUT / "logo_seffaf.png", px=1200)     # for the menu screen


if __name__ == "__main__":
    build()
