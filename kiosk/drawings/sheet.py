"""A3 drawing sheets on matplotlib, laid out in paper millimetres.

A Sheet is one A3 landscape page with border and title block. A View maps
model metres onto the paper at a scale (1:N) so drawing code works in real
coordinates and dimensions print real millimetres.
"""
import datetime
import math

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

from .. import config as C  # noqa: E402

W, H = 420.0, 297.0
MARGIN = 10.0
PT = 72 / 25.4                     # points per millimetre
LW = {"cut": 0.50, "thick": 0.35, "med": 0.25, "thin": 0.18, "dim": 0.13, "hair": 0.09}
INK = "#1a1a1a"
GREY = "#7a7a7a"

FILL = {  # section / elevation fills
    "steel": ("#a9b0b4", "////"),
    "pir": ("#f3e2a0", "xxx"),
    "wool": ("#efe3c2", "..."),
    "wood": ("#c08a5c", None),
    "alu": ("#3a3836", None),
    "panel": ("#5a6065", None),
    "glass": ("#cfe8ef", None),
    "ply": ("#e2c798", "---"),
    "white": ("#f4f3ef", None),
    "concrete": ("#d8d4cc", ".."),
    "ac": ("#e9eef0", None),
    "cut": ("#ffffff", "\\\\\\\\"),
}

PROJECT = "MHC Mola · Kiosk"
SUBTITLE = f"{C.LENGTH:.1f} × {C.WIDTH:.1f} × {C.HEIGHT:.1f} m · prefabrik kahve kioskusu"


def _setup_fonts():
    for name in ("Jost-Regular.ttf", "Jost-Medium.ttf", "Fraunces-SemiBold.ttf"):
        path = C.ASSETS / "fonts" / name
        if path.exists():
            font_manager.fontManager.addfont(str(path))
    have = {f.name for f in font_manager.fontManager.ttflist}
    plt.rcParams["font.family"] = "Jost" if "Jost" in have else "DejaVu Sans"
    plt.rcParams["hatch.linewidth"] = 0.25
    plt.rcParams["pdf.fonttype"] = 42


_setup_fonts()
SERIF = any(f.name == "Fraunces" for f in font_manager.fontManager.ttflist)


def mm(v):
    """Metres -> rounded millimetre string."""
    return f"{round(v * 1000):d}"


class Sheet:
    def __init__(self, no, title, scale="", total=None):
        self.no, self.title, self.scale = no, title, scale
        self.fig = plt.figure(figsize=(W / 25.4, H / 25.4))
        self.ax = self.fig.add_axes((0, 0, 1, 1))
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.total = total
        self._frame()

    # ---------------------------------------------------------------- primitives (paper mm)
    def line(self, pts, lw="thin", color=INK, ls="-", z=3):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=LW.get(lw, lw) * PT, ls=ls, solid_capstyle="butt", zorder=z)

    def poly(self, pts, fill=None, lw="thin", edge=INK, z=2, closed=True, alpha=1.0):
        face, hatch = FILL.get(fill, (fill, None)) if isinstance(fill, str) else (fill, None)
        self.ax.add_patch(Polygon(pts, closed=closed, facecolor=face or "none", edgecolor="none", zorder=z,
                                  alpha=alpha))
        if hatch:
            self.ax.add_patch(Polygon(pts, closed=closed, facecolor="none", edgecolor="#5c5c5c", hatch=hatch,
                                      lw=0, zorder=z))
        if lw:
            self.ax.add_patch(Polygon(pts, closed=closed, facecolor="none", edgecolor=edge,
                                      lw=LW.get(lw, lw) * PT, zorder=z + 0.5))

    def rect(self, x0, y0, x1, y1, **kw):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], **kw)

    def circle(self, x, y, r, fill=None, lw="thin", z=3, ls="-"):
        face = FILL.get(fill, (fill, None))[0] if fill else "none"
        self.ax.add_patch(Circle((x, y), r, facecolor=face, edgecolor=INK, lw=LW.get(lw, lw) * PT, zorder=z,
                                 ls=ls))

    def text(self, x, y, s, size=2.6, weight="normal", ha="left", va="baseline", color=INK, rot=0, z=6, bg=None,
             serif=False):
        kw = {"fontfamily": "Fraunces"} if serif and SERIF else {}
        t = self.ax.text(x, y, s, fontsize=size * PT, fontweight=weight, ha=ha, va=va, color=color, rotation=rot,
                         zorder=z, rotation_mode="anchor", linespacing=1.35, **kw)
        if bg:
            t.set_bbox(dict(facecolor=bg, edgecolor="none", pad=0.6))
        return t

    def paragraph(self, x, y, lines, size=2.6, gap=1.55, **kw):
        """Lines top-down from y; returns the y below the last line."""
        for ln in lines:
            if ln:
                bold = ln.startswith("**")
                self.text(x, y, ln.strip("*"), size=size, weight="medium" if bold else "normal", va="top", **kw)
            y -= size * gap
        return y

    def image(self, path, x, y, w, h=None):
        img = plt.imread(str(path))
        ih, iw = img.shape[:2]
        h = h or w * ih / iw
        self.ax.imshow(img, extent=(x, x + w, y, y + h), zorder=1, interpolation="lanczos")
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(0, H)
        return h

    def table(self, x, y, cols, rows, size=2.3, row_h=4.6, header=True):
        """cols: [(title, width_mm, align)]; rows: lists of cells. Top-left at (x, y). Returns bottom y."""
        total = sum(c[1] for c in cols)
        yy = y
        for r, row in enumerate(([[c[0] for c in cols]] if header else []) + rows):
            is_head = header and r == 0
            if is_head:
                self.rect(x, yy - row_h, x + total, yy, fill="#e6e3dc", lw=0)
            xx = x
            for (title, w, align), cell in zip(cols, row):
                tx = {"l": xx + 1.2, "r": xx + w - 1.2, "c": xx + w / 2}[align]
                self.text(tx, yy - row_h / 2, str(cell), size=size, ha={"l": "left", "r": "right", "c": "center"}[align],
                          va="center", weight="medium" if is_head else "normal")
                xx += w
            yy -= row_h
            self.line([(x, yy), (x + total, yy)], lw="hair", color=GREY)
        self.line([(x, y), (x + total, y), (x + total, yy), (x, yy), (x, y)], lw="thin")
        xx = x
        for _, w, _ in cols[:-1]:
            xx += w
            self.line([(xx, y), (xx, yy)], lw="hair", color=GREY)
        return yy

    def note_box(self, x, y, w, title, lines, size=2.4):
        self.text(x, y, title, size=2.8, weight="medium", va="top")
        return self.paragraph(x, y - 4.6, lines, size=size)

    # ---------------------------------------------------------------- frame + title block
    def _frame(self):
        m = MARGIN
        self.rect(m, m, W - m, H - m, lw="thick")
        bw, bh = 176.0, 30.0
        x0, y0 = W - m - bw, m
        self.rect(x0, y0, W - m, y0 + bh, fill="#ffffff", lw="thick", z=5)
        cx = x0
        self.text(cx + 3, y0 + bh - 5.5, PROJECT, size=4.0, weight="medium", z=7)
        self.text(cx + 3, y0 + bh - 10, SUBTITLE, size=2.3, color=GREY, z=7)
        self.text(cx + 3, y0 + 9.5, self.title, size=3.6, weight="medium", z=7)
        self.text(cx + 3, y0 + 3.6, "Tüm ölçüler mm'dir. Ölçüler sahada kontrol edilmeden imalata başlanmaz.",
                  size=1.9, color=GREY, z=7)
        rx = W - m - 34
        self.line([(rx, y0), (rx, y0 + bh)], lw="thin", z=6)
        for k, (lab, val) in enumerate((("PAFTA", self.no), ("ÖLÇEK", self.scale or "—"),
                                        ("TARİH", datetime.date.today().strftime("%d.%m.%Y")))):
            yy = y0 + bh - 2 - k * 9.6
            self.text(rx + 2.5, yy - 1.6, lab, size=1.7, color=GREY, va="top", z=7)
            self.text(rx + 2.5, yy - 4.6, val, size=3.2 if k == 0 else 2.6, weight="medium", va="top", z=7)
            if k:
                self.line([(rx, yy + 0.2), (W - m, yy + 0.2)], lw="hair", z=6)

    def save(self, pdf, png=None):
        pdf.savefig(self.fig)
        if png:
            self.fig.savefig(png, dpi=110)
        plt.close(self.fig)

    def view(self, ox, oy, scale, title=None, title_dy=-7):
        v = View(self, ox, oy, scale)
        if title:
            v.title, v.title_dy = title, title_dy
        return v


class View:
    """Model metres -> paper mm at 1:scale, origin (ox, oy) on paper = model (0, 0)."""

    def __init__(self, sheet, ox, oy, scale):
        self.s, self.ox, self.oy, self.scale = sheet, ox, oy, scale
        self.k = 1000.0 / scale
        self.ts = 1.0          # text scale for dimensions / labels (bigger on the workshop sheets)

    def p(self, u, v):
        return self.ox + u * self.k, self.oy + v * self.k

    def pts(self, seq):
        return [self.p(u, v) for u, v in seq]

    # drawing in model units
    def line(self, seq, **kw):
        self.s.line(self.pts(seq), **kw)

    def poly(self, seq, **kw):
        self.s.poly(self.pts(seq), **kw)

    def rect(self, u0, v0, u1, v1, **kw):
        self.poly([(u0, v0), (u1, v0), (u1, v1), (u0, v1)], **kw)

    def circle(self, u, v, r, **kw):
        x, y = self.p(u, v)
        self.s.circle(x, y, r * self.k, **kw)

    def text(self, u, v, s, **kw):
        x, y = self.p(u, v)
        return self.s.text(x, y, s, **kw)

    def caption(self, u, v, title, scale=True, size=3.0):
        x, y = self.p(u, v)
        self.s.text(x, y, title, size=size, weight="medium", va="top")
        if scale:
            t = self.s.text(x, y - size * 1.5, f"Ölçek 1:{self.scale}", size=2.0, color=GREY, va="top")
        self.s.line([(x, y + 1.2), (x + 60, y + 1.2)], lw="thin")

    # ---------------------------------------------------------------- dimensions
    def _tick(self, x, y):
        d = 1.1
        self.s.line([(x - d, y - d), (x + d, y + d)], lw="thin")

    def dim_h(self, u0, u1, v, off, text=None, size=2.2, ext=True):
        """Horizontal dimension between u0..u1 measured at model height v, drawn `off` mm away."""
        size *= self.ts
        (x0, y0), (x1, _) = self.p(u0, v), self.p(u1, v)
        yl = y0 + off
        if ext:
            sgn = 1 if off > 0 else -1
            for x in (x0, x1):
                self.s.line([(x, y0 + sgn * 1.0), (x, yl + sgn * 1.5)], lw="dim", color=GREY)
        self.s.line([(x0 - 1.5, yl), (x1 + 1.5, yl)], lw="dim")
        self._tick(x0, yl)
        self._tick(x1, yl)
        label = text if text is not None else mm(abs(u1 - u0))
        small = abs(x1 - x0) < len(label) * size * 0.62
        ty = yl + 0.7 if not small else yl - 0.9      # a label that doesn't fit goes under the line
        self.s.text((x0 + x1) / 2, ty, label, size=size, ha="center", va="bottom" if not small else "top",
                    bg="white" if small else None)

    def dim_v(self, v0, v1, u, off, text=None, size=2.2, ext=True):
        size *= self.ts
        (x0, y0), (_, y1) = self.p(u, v0), self.p(u, v1)
        xl = x0 + off
        if ext:
            sgn = 1 if off > 0 else -1
            for y in (y0, y1):
                self.s.line([(x0 + sgn * 1.0, y), (xl + sgn * 1.5, y)], lw="dim", color=GREY)
        self.s.line([(xl, y0 - 1.5), (xl, y1 + 1.5)], lw="dim")
        self._tick(xl, y0)
        self._tick(xl, y1)
        label = text if text is not None else mm(abs(v1 - v0))
        small = abs(y1 - y0) < len(label) * size * 0.62
        tx = xl - 0.7 if not small else xl + 0.9      # a label that doesn't fit goes beside the line
        self.s.text(tx, (y0 + y1) / 2, label, size=size, ha="center", va="bottom" if not small else "top", rot=90,
                    bg="white" if small else None)

    def chain_h(self, us, v, off, **kw):
        us = sorted(us)
        for a, b in zip(us, us[1:]):
            if b - a > 1e-4:
                self.dim_h(a, b, v, off, **kw)

    def chain_v(self, vs, u, off, **kw):
        vs = sorted(vs)
        for a, b in zip(vs, vs[1:]):
            if b - a > 1e-4:
                self.dim_v(a, b, u, off, **kw)

    def level(self, u, v, label, side=1, size=2.1):
        """Height mark: small triangle + text, e.g. '+2500'."""
        x, y = self.p(u, v)
        t = 1.4
        self.s.poly([(x, y), (x - t, y + t * 1.4), (x + t, y + t * 1.4)], fill="#ffffff", lw="thin", z=7)
        self.s.line([(x - 3 * side, y), (x + 9 * side, y)], lw="dim")
        self.s.text(x + 2 * side, y + 0.6, label, size=size, ha="left" if side > 0 else "right", va="bottom")

    def leader(self, u, v, text, dx, dy, size=2.2, ha=None):
        """Arrow-less leader: dot on the part, elbow line to a label offset (dx, dy) mm."""
        x, y = self.p(u, v)
        self.s.circle(x, y, 0.45, fill="#1a1a1a", lw=0, z=8)
        xe, ye = x + dx, y + dy
        hx = xe + (6 if dx >= 0 else -6)
        self.s.line([(x, y), (xe, ye), (hx, ye)], lw="dim", z=8)
        self.s.text(hx + (0.8 if dx >= 0 else -0.8), ye, text, size=size, ha=ha or ("left" if dx >= 0 else "right"),
                    va="center", z=8, bg="white")

    def leader_to(self, u, v, text, x, y, size=2.0):
        """Leader from a part to a label at absolute paper position (x, y); text grows away from the part."""
        size *= self.ts
        px, py = self.p(u, v)
        self.s.circle(px, py, 0.45, fill="#1a1a1a", lw=0, z=8)
        right = x >= px
        hx = x + (3 if right else -3)
        self.s.line([(px, py), (x, y), (hx, y)], lw="dim", z=8)
        self.s.text(hx + (0.8 if right else -0.8), y, text, size=size, ha="left" if right else "right", va="center",
                    z=8, bg="white")

    def leaders(self, items, x, dy=0.0, gap=4.0, size=2.0):
        """Several leaders into one label column at paper x, spaced at least `gap` mm apart."""
        placed = sorted(((self.p(u, v)[1] + dy, u, v, t) for u, v, t in items), reverse=True)
        last = None
        for y, u, v, t in placed:
            if last is not None and y > last - gap:
                y = last - gap
            self.leader_to(u, v, t, x, y, size=size)
            last = y

    def radius(self, cu, cv, r, ang, text, size=2.2):
        x0, y0 = self.p(cu, cv)
        x1, y1 = self.p(cu + r * math.cos(ang), cv + r * math.sin(ang))
        self.s.line([(x0, y0), (x1, y1)], lw="dim")
        a = math.atan2(y1 - y0, x1 - x0)
        for da in (2.6, -2.6):
            self.s.line([(x1, y1), (x1 - 1.8 * math.cos(a + da * 0.1), y1 - 1.8 * math.sin(a + da * 0.1))], lw="dim")
        self.s.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.5, text, size=size, ha="center", va="bottom",
                    rot=math.degrees(a) if abs(math.degrees(a)) <= 90 else math.degrees(a) - 180, bg="white")
