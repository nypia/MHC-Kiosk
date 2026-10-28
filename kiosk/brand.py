"""MHC Mola logo (concept B, Rozet): a round seal with a coffee bean whose crease is a road.

Outputs to kiosk/art/logo/:
    rozet_*.svg|png   the seal (blade sign, avatar, stamp)
    yatay_*.svg|png   horizontal lockup: seal + MHC MOLA / YOL ÜSTÜ (fascia, menu)
    logo_seffaf.png   transparent horizontal lockup for the menu screen
    logo_geometry.json  outlines for Blender (logo3d.py) and the drawings

    python -m kiosk.brand
"""
import json

from shapely import affinity
from shapely.ops import unary_union

from . import brand_concepts as B
from . import config as C

NAME = "MHC Mola"
OUT = C.ROOT / "kiosk" / "art" / "logo"
COLORS = {"ink": B.INK, "cream": B.CREAM, "walnut": B.WALNUT}


def seal():
    return B.concept_b()


def lockup():
    """Seal on the left, MHC MOLA with YOL ÜSTÜ underneath on the right."""
    parts = seal()
    x0, y0, x1, y1 = B.bounds(parts)
    d = y1 - y0
    name, _ = B.text("MHC MOLA", "montserrat", 0.27 * d / 0.70, tracking=0.30)
    sub, _ = B.text("YOL ÜSTÜ", "montserrat", 0.085 * d / 0.70, tracking=0.80)
    left = x1 + 0.17 * d
    name = B.place(name, x0=left, y0=(y0 + y1) / 2 - 0.02 * d)
    sub = B.place(sub, x0=left + 0.01 * d, y0=(y0 + y1) / 2 - 0.20 * d)
    rule = B.stroke([(left + 0.01 * d, (y0 + y1) / 2 - 0.075 * d),
                     (name.bounds[2], (y0 + y1) / 2 - 0.075 * d)], 0.012 * d)
    return parts + [(unary_union([name, rule]), "fg"), (sub, "accent")]


def _shapes(geom, sx, sy, k):
    def ring(coords):
        return [[round((x - sx) * k, 5), round((y - sy) * k, 5)] for x, y in coords]
    return [{"outer": ring(g.exterior.coords), "holes": [ring(h.coords) for h in g.interiors]}
            for g in getattr(geom, "geoms", [geom]) if not g.is_empty]


def export_geometry(path):
    """wordmark = horizontal lockup, height 1, centred; badge = seal, diameter 1, centred."""
    lk = lockup()
    x0, y0, x1, y1 = B.bounds(lk)
    k = 1 / (y1 - y0)
    sl = seal()
    s0, t0, s1, t1 = B.bounds(sl)
    data = {
        "wordmark": {"aspect": (x1 - x0) / (y1 - y0),
                     "parts": [{"key": key, "shapes": _shapes(g, (x0 + x1) / 2, (y0 + y1) / 2, k)} for g, key in lk]},
        "badge": {"parts": [{"key": key, "shapes": _shapes(g, (s0 + s1) / 2, (t0 + t1) / 2, 1 / (s1 - s0))}
                            for g, key in sl]},
        "colors": COLORS,
    }
    path.write_text(json.dumps(data))
    return data["wordmark"]["aspect"]


def _png(parts, path, fg, accent, bg=None, px=1600, pad=12):
    import matplotlib.pyplot as plt
    x0, y0, x1, y1 = B.bounds(parts)
    x0, y0, x1, y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
    fig = plt.figure(figsize=(px / 200, px / 200 * (y1 - y0) / (x1 - x0)), dpi=200)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.patch.set_facecolor(bg or (0, 0, 0, 0))
    B.draw(ax, parts, fg, accent)
    fig.savefig(path, transparent=bg is None)
    plt.close(fig)


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in ("logo_koyu", "logo_acik", "logo_tek_renk", "rozet", "isaret"):
        for ext in ("svg", "png"):
            (OUT / f"{old}.{ext}").unlink(missing_ok=True)
    variants = [("koyu", B.CREAM, B.WALNUT, B.INK), ("acik", B.INK, B.WALNUT, B.PAPER),
                ("tek_renk", B.CREAM, B.CREAM, None)]
    for name, parts in (("rozet", seal()), ("yatay", lockup())):
        for v, fg, accent, bg in variants:
            B.svg(parts, OUT / f"{name}_{v}.svg", fg, accent, bg)
            _png(parts, OUT / f"{name}_{v}.png", fg, accent, bg)
    _png(lockup(), OUT / "logo_seffaf.png", B.CREAM, B.WALNUT, None, px=1400, pad=4)
    aspect = export_geometry(OUT / "logo_geometry.json")
    print(f"logo written to {OUT} (lockup aspect {aspect:.3f})")


if __name__ == "__main__":
    build()
