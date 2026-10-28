"""Reusable drawn views: plan, elevations, cross-section, developed walls."""
import math

from .. import config as C
from .. import layout as L
from .. import outline as O
from . import geo as G
from .sheet import mm

FZ0, FZ1 = C.FASCIA_Z


def plan(v, dims=True, cut_mark=True):
    """Plan cut at +1.50 m: walls, posts, openings, door swing."""
    v.poly(G.ring(L.FASCIA_D[0]), fill=None, lw="thin")                     # fascia line above
    v.poly(G.ring(0.0), fill=None, lw="hair")
    for a, b in L.free_ranges(1.5, 1.5):
        v.poly(G.band(a, b, 0.0, C.SLAT_D[1]), fill="wood", lw="hair")
        v.poly(G.band(a, b, *C.PANEL_D), fill="panel", lw="thin")
    for pid, s, _ in L.posts():
        x, y = O.at(s, 0.14)
        tx, ty = O.tangent2(s)
        nx, ny = -ty, tx
        c = [(x + tx * a + nx * b, y + ty * a + ny * b) for a, b in ((-.03, -.03), (.03, -.03), (.03, .03), (-.03, .03))]
        v.poly(c, fill="steel", lw="thin")
    # window: sill line + glass
    x0, x1 = C.WIN_X
    v.line([(x0, -C.B + 0.085), (x1, -C.B + 0.085)], lw="thin", color="#3b8db0")
    v.line([(x0, -C.B), (x1, -C.B)], lw="hair", ls=(0, (4, 2)))
    for name, a, b in L.bar_shelves():
        v.rect(a, -C.B - L.BAR_SHELF["depth"], b, -C.B, fill=None, lw="hair")
    # door leaf + swing (opens outward)
    y0, y1 = C.DOOR_Y
    hx = C.A - 0.08
    r = y1 - y0 - 0.05
    v.line([(hx, y1 - 0.025), (hx + r, y1 - 0.025)], lw="thick")
    arc = [(hx + r * math.cos(t), y1 - 0.025 - r * math.sin(t)) for t in [k * math.pi / 2 / 24 for k in range(25)]]
    v.line(arc, lw="hair", ls=(0, (3, 2)))
    if dims:
        v.dim_h(-C.A, C.A, -C.B, -16)
        v.dim_h(L.FASCIA_D[0] - C.A, C.A - L.FASCIA_D[0], C.B, 9, text=f"{mm(C.LENGTH - 2 * L.FASCIA_D[0])} (saçak)")
        v.chain_h([-C.A, x0, C.SCREEN_X[0], C.SCREEN_X[1], x1, C.A], -C.B, -9)
        v.dim_v(-C.B, C.B, C.A, 16)
        v.chain_v([-C.B, y0, y1, C.B], C.A, 9)
        v.radius(-O.HX, O.HY, O.R, math.radians(135), "R450")
    if cut_mark:
        for yy, side in ((-C.B - 0.55, -1), (C.B + 0.55, 1)):
            v.line([(0.40, yy), (0.40, yy - side * 0.25)], lw="thick")
            v.text(0.40 + 0.08, yy, "A", size=3.0, weight="medium", va="center")


def elevation(v, face, dims=True, detail=True):
    """Finished elevation of one face. u = horizontal as seen from outside, z = height above chassis base."""
    half = G.HALF[face]
    v.line([(-half - 0.6, 0), (half + 0.6, 0)], lw="thick")
    v.rect(-half, C.SKIRT_H, half, FZ0, fill="#4a4f53", lw="thin")
    # slats
    for _, s, segs in L.slats()[0]:
        if not G.visible(face, s):
            continue
        x, y = O.at(s, sum(C.SLAT_D) / 2)
        u = G.project(face, x, y)
        w = C.SLAT_W * G.facing(face, s)
        for z0, z1 in segs:
            v.rect(u - w / 2, z0, u + w / 2, z1, fill="wood", lw=0.06 if detail else 0)
    # skirt + fascia + cassette joints
    v.rect(-half, 0, half, C.SKIRT_H, fill="alu", lw="thin")
    ext = half - L.FASCIA_D[0]
    v.rect(-ext, FZ0, ext, FZ1, fill="alu", lw="thin")
    for _, s0, s1, _ in L.cassettes():
        for s in (s0, s1):
            if G.visible(face, s):
                u = G.project(face, *O.at(s, L.FASCIA_D[0]))
                v.line([(u, FZ0), (u, FZ1)], lw="thin", color="#d9d9d9", z=3.2)
    # corner tangent lines
    for u in (-(half - O.R), half - O.R):
        v.line([(u, 0.02), (u, FZ0 - 0.02)], lw="hair", ls=(0, (6, 3)), color="#333333")
    # openings
    for name, u0, u1, z0, z1 in G.opening_on(face):
        v.rect(u0, z0, u1, z1, fill="#ffffff", lw="thin")
        if name == "pencere":
            profiles, panes, (sx, sz, sw, sh) = L.window()
            sgn = 1 if face == "front" else -1
            for _, cx, cz, w, h, _ in panes:
                cu = sgn * cx
                v.rect(cu - w / 2, cz - h / 2, cu + w / 2, cz + h / 2, fill="glass", lw=0)
            for _, cx, cz, w, h in profiles:
                cu = sgn * cx
                v.rect(cu - w / 2, cz - h / 2, cu + w / 2, cz + h / 2, fill="#202020", lw=0)
            v.rect(sgn * sx - sw / 2, sz - sh / 2, sgn * sx + sw / 2, sz + sh / 2, fill="#26282a", lw="thin")
            v.text(sgn * sx, sz, "55\" MENÜ EKRANI", size=1.9, ha="center", va="center", color="#efe2c4")
            # canopy + bar shelves
            v.rect(u0 - L.CANOPY["overhang"], C.WIN_HEAD + 0.035, u1 + L.CANOPY["overhang"], C.WIN_HEAD + 0.065,
                   fill="alu", lw="thin")
            for _, a, b in L.bar_shelves():
                v.rect(sgn * a, C.WIN_SILL - L.BAR_SHELF["t"], sgn * b, C.WIN_SILL, fill="#d8b48a", lw="thin")
        else:
            v.rect(u0 + 0.025, z0 + 0.02, u1 - 0.025, z1 - 0.02, fill="alu", lw="thin")
            hu = u1 - 0.14 if face == "right" else u0 + 0.14
            v.line([(hu, 0.85), (hu, 1.30)], lw="thick", color="#c9cdd0")
    # signage zones only: the logo and sign graphics are not final yet
    if face in L.LOGOS:
        u = L.LOGOS[face] if face == "front" else -L.LOGOS[face]
        v.circle(u, L.LOGO_Z, L.LOGO_R, fill="#ffffff", lw="thin", z=4.2, ls=(0, (4, 2)))
        v.text(u, L.LOGO_Z, "LOGO\nALANI", size=0.07 * v.k, ha="center", va="center", z=5)
    if face == "front":
        sg = L.SIGN
        v.rect(sg["x"] - sg["w"] / 2, sg["z"] - sg["h"] / 2, sg["x"] + sg["w"] / 2, sg["z"] + sg["h"] / 2,
               fill="#ffffff", lw="thin", z=4.2)
        v.text(sg["x"], sg["z"], "TABELA ALANI", size=0.07 * v.k, ha="center", va="center", z=5)
    # rooftop condenser above the parapet
    ao = L.AC_OUTDOOR
    ac_top = C.ROOF_Z + ao["feet"] + ao["h"]
    if face in ("front", "back"):
        cu, w = G.project(face, ao["x"], 0), ao["w"]
    else:
        cu, w = G.project(face, 0, ao["y"]), ao["d"]
    v.rect(cu - w / 2, FZ1, cu + w / 2, ac_top, fill="#eeeeee", lw="thin")

    if dims:
        v.dim_h(-half, half, 0, -14)
        us = [-half, half]
        for _, u0, u1, _, _ in G.opening_on(face):
            us += [u0, u1]
        us += [u for u in (-(half - O.R), half - O.R) if all(abs(u - w) > 0.12 for w in us)]
        v.chain_h(us, 0, -7)
        zs = [0, C.SKIRT_H, FZ0, FZ1]
        for _, _, _, z0, z1 in G.opening_on(face):
            zs += [z0, z1]
        v.chain_v(sorted(set(round(z, 4) for z in zs)), -half, -7)
        v.dim_v(0, FZ1, -half, -14)
        v.dim_v(FZ1, ac_top, half, 7, text=f"{mm(ac_top - FZ1)} klima")


def developed(v, d_label=0.0, z0=0.0, z1=C.HEIGHT, faces=True):
    """Background for developed (unfolded) walls: face bands + names along the loop."""
    marks = []
    for k, (a, b) in enumerate(L.ARCS):
        pa = L.loop_pos(a)
        pb = pa + (b - a)
        v.rect(pa, z0, pb, z1, fill="#f1ede6", lw=0)
        marks += [pa, pb]
        v.line([(pa, z0 - 0.05), (pa, z1 + 0.05)], lw="hair", ls=(0, (6, 3)))
        v.line([(pb, z0 - 0.05), (pb, z1 + 0.05)], lw="hair", ls=(0, (6, 3)))
    if faces:
        names = [("Köşe 1", 0), ("ÖN CEPHE", 1), ("Köşe 2", 2), ("SAĞ CEPHE (kapı)", 3), ("Köşe 3", 4),
                 ("ARKA CEPHE", 5), ("Köşe 4", 6), ("SOL CEPHE", 7)]
        edges = [0.0]
        for a, b in L.ARCS:
            pa = L.loop_pos(a)
            edges += [pa, pa + (b - a)]
        edges = sorted(set(round(e, 6) for e in edges + [O.TOTAL]))
        for (name, _), e0, e1 in zip(names, edges, edges[1:]):
            v.text((e0 + e1) / 2, z1 + 0.12, name, size=2.0 if name.startswith("Köşe") else 2.6,
                   weight="medium", ha="center", va="bottom")
    return marks
