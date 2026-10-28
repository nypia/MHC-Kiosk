"""Interior fit-out: floor, ceiling + lights, counters, shelving, equipment.

Front counter runs under the window (-Y), back counter along the back wall (+Y),
tall storage front-left, glass-door fridge back-left, door on +X.
"""
import math

import bpy

from . import config as C
from . import materials as Mt
from . import util as U

Z = C.z
TOP = C.FLOOR_H + C.COUNTER_H          # worktop surface, relative
WALL = C.B - 0.17                      # counters stand clear of the frame posts
DEPTH = 0.62


def _group(name, coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    return U.empty(name, coll, loc, rot)


def _add(root, *objs):
    for o in objs:
        U.parent(o, root)
    return objs[0] if len(objs) == 1 else objs


# ----------------------------------------------------------------- counters
def _counter(M, coll, name, x0, x1, side, doors_steel=()):
    """Base run between x0..x1. side=-1 front wall (faces +Y), +1 back wall (faces -Y).

    Built in a local frame where the cabinet front faces -Y; the root is
    rotated 180 deg for the front counter so its doors face the aisle.
    """
    length = x1 - x0
    cy = side * (WALL - DEPTH / 2)
    rot = (0, 0, 0) if side > 0 else (0, 0, math.pi)
    body = _group(f"{name} gövde", coll, ((x0 + x1) / 2, cy, Z(C.FLOOR_H)), rot)
    carcass_h = C.COUNTER_H - 0.04 - 0.10
    _add(body,
         U.box(f"{name} baza", (length - 0.02, DEPTH - 0.10, 0.10), (0, 0.04, 0), coll, [M["black-plastic"]],
               origin="bottom"),
         U.box(f"{name} karkas", (length, DEPTH - 0.04, carcass_h), (0, 0.02, 0.10), coll, [M["cabinet"]],
               origin="bottom"))
    n = max(1, round(length / 0.55))
    w = length / n
    for i in range(n):
        dx = -length / 2 + w * (i + 0.5)
        steel = i in doors_steel
        door = U.box(f"{name} kapak {i}", (w - 0.004, 0.018, carcass_h - 0.006),
                     (dx, -DEPTH / 2 + 0.009, 0.10 + carcass_h / 2), coll,
                     [M["steel"] if steel else M["cabinet"]], bevel=0.002)
        handle = U.box(f"{name} kulp {i}", (0.16 if not steel else w - 0.12, 0.02, 0.012),
                       (dx, -DEPTH / 2 - 0.012, 0.10 + carcass_h - 0.06), coll,
                       [M["chrome"] if steel else M["black-plastic"]], bevel=0.003)
        _add(body, door, handle)
    top = _group(f"{name} tezgâh", coll, ((x0 + x1) / 2, cy, Z(TOP - 0.02)), rot)
    _add(top, U.box(f"{name} tezgâh tablası", (length + 0.02, DEPTH + 0.02, 0.04), (0, -0.01, 0), coll,
                    [M["oak"]], bevel=0.003))
    return body, top


def _tall_unit(M, coll, name, x0, x1, side, h, glass_door=False):
    cy = side * (WALL - 0.30)
    root = _group(name, coll, ((x0 + x1) / 2, cy, Z(C.FLOOR_H)), (0, 0, 0) if side > 0 else (0, 0, math.pi))
    w = x1 - x0
    mat = [M["white-appliance"]] if glass_door else [M["cabinet"]]
    _add(root, U.box(f"{name} gövde", (w, 0.60, h), (0, 0, 0), coll, mat, bevel=0.004, origin="bottom"))
    if glass_door:
        _add(root,
             U.box(f"{name} cam kapak", (w - 0.08, 0.012, h - 0.36), (0, -0.305, 0.22 + (h - 0.36) / 2), coll,
                   [M["glass"]]),
             U.box(f"{name} kapak çerçeve", (w - 0.04, 0.014, 0.05), (0, -0.30, h - 0.12), coll, [M["black-plastic"]]),
             U.box(f"{name} kulp", (0.02, 0.03, 0.55), (w / 2 - 0.07, -0.33, 1.0), coll, [M["chrome"]], bevel=0.004),
             U.box(f"{name} tabela", (w - 0.02, 0.01, 0.10), (0, -0.305, h - 0.06), coll, [M["alucobond"]]))
        colours = [(0.6, 0.05, 0.03, 1), (0.95, 0.6, 0.05, 1), (0.1, 0.35, 0.12, 1), (0.85, 0.85, 0.8, 1)]
        bottle_mats = [Mt.principled(f"bottle {k}", c, rough=0.15, coat=0.8) for k, c in enumerate(colours)]
        for row, sz in enumerate((0.36, 0.72, 1.08, 1.44)):
            _add(root, U.box(f"{name} raf {row}", (w - 0.08, 0.5, 0.01), (0, 0.0, sz), coll, [M["glass"]]))
            for k in range(6):
                bx = -w / 2 + 0.09 + k * (w - 0.18) / 5
                _add(root, U.cylinder(f"{name} şişe {row}{k}", 0.032, 0.22, (bx, -0.12, sz + 0.005), coll,
                                      [bottle_mats[(row + k) % 4]], verts=16, r2=0.028))
    else:
        for k, dx in enumerate((-w / 4, w / 4)):
            _add(root,
                 U.box(f"{name} kapak {k}", (w / 2 - 0.004, 0.018, h - 0.12), (dx, -0.309, 0.10 + (h - 0.12) / 2),
                       coll, [M["cabinet"]], bevel=0.002),
                 U.box(f"{name} kulp {k}", (0.012, 0.02, 0.30), (dx + (w / 4 - 0.05) * (1 if k == 0 else -1), -0.33, 1.0),
                       coll, [M["black-plastic"]], bevel=0.003))
    return root


# ----------------------------------------------------------------- equipment
def espresso_machine(M, coll, loc, rot):
    r = _group("espresso makinesi", coll, loc, rot)
    st, ch, bk = [M["steel"]], [M["chrome"]], [M["black-plastic"]]
    _add(r,
         U.rounded_box("espresso gövde", (0.74, 0.50, 0.36), 0.02, (0, 0.02, 0.07 + 0.18), coll, st),
         U.rounded_box("espresso yan panel sol", (0.03, 0.52, 0.38), 0.008, (-0.375, 0.02, 0.26), coll, bk),
         U.rounded_box("espresso yan panel sağ", (0.03, 0.52, 0.38), 0.008, (0.375, 0.02, 0.26), coll, bk),
         U.box("espresso fincan ızgarası", (0.70, 0.46, 0.012), (0, 0.02, 0.44), coll, ch),
         U.box("espresso damlama tepsisi", (0.66, 0.16, 0.025), (0, -0.30, 0.08), coll, ch, bevel=0.004),
         U.box("espresso ekran", (0.16, 0.006, 0.05), (0, -0.233, 0.36), coll,
               [Mt.principled("espresso display", (0.02, 0.05, 0.08, 1), rough=0.1, emission=(0.3, 0.6, 1.0, 1))]))
    for k in range(4):
        _add(r, U.cylinder(f"espresso ayak {k}", 0.015, 0.07, ((-0.33, 0.33)[k % 2], (-0.18, 0.22)[k // 2], 0), coll,
                           bk, verts=12))
    for k, gx in enumerate((-0.18, 0.18)):
        _add(r,
             U.cylinder(f"grup başlığı {k}", 0.045, 0.06, (gx, -0.25, 0.20), coll, ch, verts=32),
             U.cylinder(f"portafiltre {k}", 0.038, 0.035, (gx, -0.25, 0.17), coll, ch, verts=32),
             U.box(f"portafiltre sap {k}", (0.025, 0.16, 0.025), (gx, -0.35, 0.18), coll, bk, bevel=0.008,
                   rot=(-0.25, 0, 0)),
             U.cylinder(f"buhar çubuğu {k}", 0.005, 0.22, (gx * 1.75, -0.25, 0.10), coll, ch, verts=10),
             U.cylinder(f"buhar düğmesi {k}", 0.018, 0.03, (gx * 1.75, -0.24, 0.31), coll, bk, verts=16,
                        rot=(math.pi / 2, 0, 0), origin="center"))
    for k in range(6):
        cx = -0.25 + k * 0.1
        _add(r, U.cylinder(f"üst fincan {k}", 0.035, 0.06, (cx, 0.05, 0.446), coll, [M["ceramic"]], verts=20,
                           r2=0.042))
    return r


def grinder(M, coll, loc, rot):
    r = _group("kahve değirmeni", coll, loc, rot)
    _add(r,
         U.rounded_box("değirmen taban", (0.20, 0.26, 0.05), 0.01, (0, 0, 0.025), coll, [M["black-plastic"]]),
         U.rounded_box("değirmen gövde", (0.18, 0.22, 0.36), 0.03, (0, 0.03, 0.05 + 0.18), coll,
                       [M["black-plastic"]]),
         U.cylinder("değirmen motor kapağı", 0.07, 0.06, (0, 0.02, 0.41), coll, [M["steel"]], verts=32),
         U.cylinder("değirmen hazne", 0.085, 0.24, (0, 0.02, 0.47), coll, [M["frosted"]], verts=32, r2=0.11),
         U.cylinder("değirmen çekirdek", 0.078, 0.14, (0, 0.02, 0.475), coll, [M["coffee"]], verts=32, r2=0.095),
         U.cylinder("değirmen kapak", 0.112, 0.02, (0, 0.02, 0.71), coll, [M["black-plastic"]], verts=32),
         U.box("değirmen çatal", (0.08, 0.06, 0.012), (0, -0.09, 0.16), coll, [M["steel"]]))
    return r


def toaster(M, coll, loc, rot):
    r = _group("tost makinesi", coll, loc, rot)
    st, bk = [M["steel"]], [M["black-plastic"]]
    grill = Mt.noisy("grill plate", (0.03, 0.03, 0.03, 1), rough=0.55, metal=0.6, scale=60)
    _add(r,
         U.rounded_box("tost alt gövde", (0.52, 0.42, 0.12), 0.01, (0, 0, 0.06 + 0.02), coll, st),
         U.box("tost alt plaka", (0.46, 0.34, 0.012), (0, 0, 0.146), coll, [grill]),
         U.box("tost ekmek", (0.2, 0.2, 0.03), (-0.08, -0.02, 0.165), coll, [M["bread"]], bevel=0.01),
         U.box("tost üst plaka", (0.46, 0.34, 0.012), (0, 0, 0.20), coll, [grill]),
         U.rounded_box("tost üst kapak", (0.50, 0.40, 0.07), 0.015, (0, 0, 0.24), coll, st),
         U.cylinder("tost kolu", 0.014, 0.44, (-0.22, -0.26, 0.27), coll, bk, verts=16, rot=(0, math.pi / 2, 0),
                    origin="center"),
         U.box("tost termostat paneli", (0.30, 0.01, 0.06), (0, -0.213, 0.08), coll, bk),
         U.cylinder("tost menteşe", 0.02, 0.5, (-0.25, 0.20, 0.21), coll, st, verts=16, rot=(0, math.pi / 2, 0),
                    origin="center"))
    for k in range(2):
        _add(r, U.cylinder(f"tost düğme {k}", 0.018, 0.02, (-0.08 + k * 0.16, -0.22, 0.08), coll, [M["red"]],
                           verts=16, rot=(math.pi / 2, 0, 0), origin="center"))
    return r


def tea_urn(M, coll, loc, rot):
    """Turkish double tea urn (çay kazanı) with two demlik teapots on top."""
    r = _group("çay makinesi", coll, loc, rot)
    st, ch, bk = [M["steel"]], [M["chrome"]], [M["black-plastic"]]
    _add(r, U.box("çay tepsisi", (0.66, 0.36, 0.03), (0, 0, 0), coll, st, bevel=0.005, origin="bottom"))
    for k, cx in enumerate((-0.165, 0.165)):
        _add(r,
             U.cylinder(f"çay kazanı {k}", 0.15, 0.40, (cx, 0.0, 0.03), coll, st, verts=48),
             U.cylinder(f"çay kazanı bilezik {k}", 0.153, 0.02, (cx, 0.0, 0.10), coll, ch, verts=48),
             U.cylinder(f"çay kazanı omuz {k}", 0.15, 0.06, (cx, 0.0, 0.43), coll, st, verts=48, r2=0.075),
             U.cylinder(f"musluk {k}", 0.012, 0.09, (cx, -0.18, 0.13), coll, ch, verts=12, rot=(math.pi / 2, 0, 0),
                        origin="center"),
             U.cylinder(f"musluk kolu {k}", 0.008, 0.06, (cx, -0.215, 0.16), coll, bk, verts=10),
             U.cylinder(f"demlik {k}", 0.07, 0.11, (cx, 0.0, 0.49), coll, ch, verts=32, r2=0.06),
             U.cylinder(f"demlik kapak {k}", 0.045, 0.02, (cx, 0.0, 0.60), coll, ch, verts=24),
             U.cylinder(f"demlik topuz {k}", 0.012, 0.025, (cx, 0.0, 0.62), coll, bk, verts=12),
             U.cylinder(f"demlik ağız {k}", 0.008, 0.09, (cx, -0.08, 0.53), coll, ch, verts=10, rot=(-0.9, 0, 0),
                        origin="center"))
    return r


def sink(M, coll, loc, rot):
    r = _group("evye", coll, loc, rot)
    st, ch = [M["steel"]], [M["chrome"]]
    basin_dark = Mt.noisy("sink basin", (0.35, 0.36, 0.37, 1), rough=0.3, metal=1.0, scale=30)
    _add(r,
         U.box("evye tabla", (0.56, 0.50, 0.012), (0, 0, 0.006), coll, st, bevel=0.003),
         U.box("evye hazne", (0.44, 0.36, 0.004), (0, -0.03, 0.0125), coll, [basin_dark]),
         U.cylinder("batarya gövde", 0.022, 0.30, (0, 0.20, 0.012), coll, ch, verts=24),
         U.cylinder("batarya ağız", 0.012, 0.20, (0, 0.10, 0.31), coll, ch, verts=16, rot=(math.pi / 2, 0, 0),
                    origin="center"),
         U.cylinder("batarya kolu", 0.008, 0.08, (0.04, 0.20, 0.27), coll, ch, verts=10, rot=(0, 1.2, 0),
                    origin="center"),
         U.cylinder("sabunluk", 0.03, 0.16, (0.20, 0.20, 0.012), coll, [M["ceramic"]], verts=20))
    return r


def pos_terminal(M, coll, loc, rot):
    r = _group("ödeme terminali", coll, loc, rot)
    screen_mat = Mt.principled("pos screen", (0.02, 0.02, 0.02, 1), rough=0.05, coat=1.0,
                               emission=(0.55, 0.62, 0.7, 1))
    _add(r,
         U.cylinder("pos ayak", 0.07, 0.015, (0, 0, 0), coll, [M["black-plastic"]], verts=32),
         U.box("pos boyun", (0.03, 0.03, 0.14), (0, 0.02, 0.015), coll, [M["steel"]], origin="bottom",
               rot=(-0.25, 0, 0)),
         U.rounded_box("pos tablet", (0.26, 0.012, 0.18), 0.008, (0, -0.005, 0.20), coll, [M["black-plastic"]],
                       rot=(-0.45, 0, 0)),
         U.box("pos ekran", (0.24, 0.002, 0.16), (0, -0.012, 0.202), coll, [screen_mat], rot=(-0.45, 0, 0)),
         U.rounded_box("kart okuyucu", (0.08, 0.14, 0.03), 0.01, (0.20, 0.0, 0.015), coll, [M["black-plastic"]]))
    return r


def pastry_case(M, coll, loc, rot):
    r = _group("pasta vitrini", coll, loc, rot)
    _add(r,
         U.box("vitrin taban", (0.62, 0.40, 0.06), (0, 0, 0), coll, [M["steel"]], bevel=0.004, origin="bottom"),
         U.box("vitrin cam", (0.62, 0.40, 0.30), (0, 0, 0.06), coll, [M["glass"]], origin="bottom"),
         U.box("vitrin raf", (0.58, 0.36, 0.006), (0, 0, 0.20), coll, [M["glass"]]))
    pastry = Mt.principled("pastry", (0.72, 0.44, 0.17, 1), rough=0.6, coat=0.2)
    for k in range(4):
        _add(r, U.cylinder(f"poğaça {k}", 0.045, 0.04, (-0.21 + k * 0.14, -0.05, 0.065), coll, [pastry], verts=20,
                           r2=0.03))
        _add(r, U.cylinder(f"simit {k}", 0.055, 0.025, (-0.21 + k * 0.14, 0.06, 0.205), coll, [M["bread"]],
                           verts=20, r2=0.05))
    return r


def tea_glasses(M, coll, loc, rot, rows=2, cols=8):
    """Rows of ince belli çay bardağı on saucers."""
    r = _group("çay bardakları", coll, loc, rot)
    saucer = Mt.principled("saucer", (0.82, 0.8, 0.76, 1), rough=0.1, coat=0.8)
    tea = Mt.glass("tea glass", tint=(0.95, 0.97, 0.97, 1))
    for i in range(rows):
        for j in range(cols):
            p = (j * 0.085, i * 0.09, 0)
            _add(r,
                 U.cylinder(f"tabak {i}{j}", 0.04, 0.008, p, coll, [saucer], verts=20, r2=0.035),
                 U.cylinder(f"bardak alt {i}{j}", 0.022, 0.045, (p[0], p[1], 0.008), coll, [tea], verts=20, r2=0.017),
                 U.cylinder(f"bardak üst {i}{j}", 0.017, 0.05, (p[0], p[1], 0.053), coll, [tea], verts=20, r2=0.026))
    return r


def cup_stacks(M, coll, loc, rot):
    r = _group("karton bardaklar", coll, loc, rot)
    sizes = [(0.040, 0.30), (0.045, 0.32), (0.050, 0.34)]
    for k, (rad, h) in enumerate(sizes):
        _add(r,
             U.cylinder(f"bardak kulesi {k}", rad * 0.75, h, (k * 0.12, 0, 0), coll, [M["paper"]], verts=24, r2=rad),
             U.cylinder(f"bardak kapak {k}", rad * 1.02, 0.012, (k * 0.12, 0, h), coll, [M["alucobond"]], verts=24))
    for k in range(2):
        _add(r, U.cylinder(f"süt potu {k}", 0.045, 0.11, (0.42 + k * 0.11, 0.02, 0), coll, [M["steel"]], verts=24,
                           r2=0.038))
    return r


def shelf_goods(M, coll, loc, rot):
    r = _group("raf ürünleri", coll, loc, rot)
    label = Mt.principled("bag label", "alucobond-black", rough=0.5)
    for k in range(5):
        _add(r,
             U.box(f"kahve paketi {k}", (0.10, 0.07, 0.22), (k * 0.13, 0, 0), coll, [M["kraft"]], bevel=0.01,
                   origin="bottom"),
             U.box(f"kahve etiketi {k}", (0.07, 0.002, 0.07), (k * 0.13, -0.036, 0.11), coll, [label]))
    for k in range(3):
        _add(r, U.cylinder(f"kavanoz {k}", 0.05, 0.16, (0.75 + k * 0.13, 0, 0), coll, [M["glass"]], verts=24),
             U.cylinder(f"kavanoz içi {k}", 0.045, 0.11, (0.75 + k * 0.13, 0, 0.004), coll,
                        [(M["coffee"], M["kraft"], M["bread"])[k]], verts=24),
             U.cylinder(f"kavanoz kapak {k}", 0.052, 0.025, (0.75 + k * 0.13, 0, 0.16), coll, [M["oak"]], verts=24))
    return r


def pendant(M, coll, name, loc, drop):
    r = _group(name, coll, loc)
    _add(r,
         U.cylinder(f"{name} rozet", 0.05, 0.015, (0, 0, -0.015), coll, [M["lamp-shade"]], verts=24),
         U.cylinder(f"{name} kablo", 0.002, drop, (0, 0, -drop), coll, [M["black-plastic"]], verts=8),
         U.cylinder(f"{name} abajur", 0.11, 0.18, (0, 0, -drop - 0.18), coll, [M["lamp-shade"]], verts=48, r2=0.025,
                    caps=False),
         U.cylinder(f"{name} ampul", 0.035, 0.04, (0, 0, -drop - 0.19), coll, [M["bulb"]], verts=24, r2=0.025))
    return r


# ----------------------------------------------------------------- build
CEIL = Z(C.CEILING_Z)


def service_deck(M, coll):
    """Suspended service deck (teknik asma kat) at +2.50 with the ducted AC above it.

    Build-up from below: 6 mm white board, 40x40 steel grid on the joist
    lines, 18 mm plywood. It hangs from the ring beam with M10 rods. On top:
    slim ducted indoor unit, supply duct to a linear slot over the window,
    return grille, condensate and refrigerant lines, electrical panel.
    Everything is parented to one root so it installs as a unit.
    """
    root = _group("teknik asma kat", coll)
    board_top = CEIL + 0.006
    grid_top = board_top + 0.040
    deck_top = CEIL + C.DECK_T
    plywood = Mt.principled("plywood", (0.62, 0.48, 0.30, 1), rough=0.8)
    galv = M["steel-frame"]
    copper = Mt.principled("copper", (0.78, 0.42, 0.25, 1), rough=0.3, metal=1.0)
    white = [M["panel-white"]]
    _add(root,
         U.slab("asma tavan beyaz panel", 0.17, CEIL, board_top, white, coll),
         U.slab("asma kat kontrplak", 0.17, grid_top, deck_top, [plywood], coll))
    for k, x in enumerate((-2.0, -1.0, 0.0, 1.0, 2.0)):
        _add(root, U.box(f"asma kat taşıyıcı {k}", (0.04, 2 * (C.B - 0.17), 0.04), (x, 0, board_top + 0.02), coll,
                         [galv]))
        for y in (-0.7, 0.7):
            rod = Z(C.RING_Z[0]) - deck_top
            _add(root, U.cylinder(f"asma kat askı {k} {y:+.1f}", 0.005, rod, (x, y, deck_top), coll, [galv], verts=8))

    # Underside: access hatch, supply slot over the window, return grille.
    black = [M["black-plastic"]]
    hx, hy = -1.55, 0.05
    for k, (dx, dy, w, d) in enumerate(((0, 0.3, 0.62, 0.01), (0, -0.3, 0.62, 0.01), (0.3, 0, 0.01, 0.62),
                                        (-0.3, 0, 0.01, 0.62))):
        _add(root, U.box(f"bakım kapağı çerçeve {k}", (w, d, 0.004), (hx + dx, hy + dy, CEIL - 0.002), coll, black))
    _add(root,
         U.box("üfleme menfezi", (1.40, 0.07, 0.006), (0.40, -1.15, CEIL - 0.003), coll, black),
         U.box("emiş menfezi", (0.60, 0.30, 0.006), (0.30, 0.75, CEIL - 0.003), coll, black))
    for k in range(7):
        _add(root, U.box(f"emiş menfezi lamel {k}", (0.58, 0.004, 0.008), (0.30, 0.62 + k * 0.042, CEIL - 0.007),
                         coll, [M["steel"]]))

    # Equipment on the deck.
    aw, ad, ah = C.AC_INDOOR
    ux, uy = 0.30, 0.35
    _add(root,
         U.rounded_box("klima iç ünite (kanallı)", (aw, ad, ah), 0.01, (ux, uy, deck_top + ah / 2), coll,
                       [M["white-appliance"]]),
         U.box("üfleme kanalı", (0.70, 1.20, 0.15), (ux + 0.05, uy - ad / 2 - 0.60, deck_top + 0.085), coll, [galv]),
         U.box("üfleme kanalı ağız", (1.40, 0.12, 0.06), (0.40, -1.15, deck_top + 0.03), coll, [galv]),
         U.box("emiş plenumu", (0.62, 0.32, 0.12), (0.30, 0.75, deck_top + 0.06), coll, [galv]),
         U.box("elektrik panosu", (0.40, 0.14, 0.24), (-1.50, 0.95, deck_top + 0.12), coll, [M["cabinet"]],
               bevel=0.004),
         U.box("LED sürücü kutusu", (0.25, 0.10, 0.05), (-1.00, 1.05, deck_top + 0.025), coll, black),
         U.box("ekran oynatıcı", (0.15, 0.12, 0.04), (0.40, -0.80, deck_top + 0.02), coll, black))
    pipe_x = ux + aw / 2 - 0.05
    _add(root,
         U.cylinder("yoğuşma hattı", 0.012, 0.85, (pipe_x, uy + ad / 2, deck_top + 0.03), coll, white, verts=12,
                    rot=(-1.5708, 0, 0), origin="bottom"))
    for k, dx in enumerate((0.0, 0.04)):
        _add(root, U.cylinder(f"bakır hat {k}", 0.008, Z(C.ROOF_Z) - deck_top - 0.12, (1.30 + dx, 0.90, deck_top + 0.12),
                              coll, [copper], verts=12))

    # Lights under the deck.
    lights = {"area": [], "point": [], "emit": [M["bulb"]]}
    led_panel = Mt.principled("ceiling led panel", (0.95, 0.95, 0.95, 1), rough=0.4, emission="led-warm")
    lights["emit"].append(led_panel)
    for k, lx in enumerate((-0.9, 0.9)):
        _add(root, U.box(f"tavan LED panel {k}", (0.6, 0.6, 0.008), (lx, 0.25, CEIL - 0.004), coll, [led_panel]))
        data = bpy.data.lights.new(f"tavan ışığı {k}", "AREA")
        data.shape, data.size = "SQUARE", 0.6
        data.color = (1.0, 0.86, 0.68)
        data.energy = 0.0
        obj = bpy.data.objects.new(f"tavan ışığı {k}", data)
        coll.objects.link(obj)
        obj.location = (lx, 0.25, CEIL - 0.01)
        _add(root, obj)
        lights["area"].append((data, 160.0))
    for k, px in enumerate((-0.65, 0.40, 1.40)):
        _add(root, pendant(M, coll, f"sarkıt lamba {k}", (px, -0.98, CEIL), 0.18))
        data = bpy.data.lights.new(f"sarkıt ışığı {k}", "POINT")
        data.shadow_soft_size = 0.03
        data.color = (1.0, 0.8, 0.55)
        data.energy = 0.0
        obj = bpy.data.objects.new(f"sarkıt ışığı {k}", data)
        coll.objects.link(obj)
        obj.location = (px, -0.98, CEIL - 0.18 - 0.16)  # inside the shade
        _add(root, obj)
        lights["point"].append((data, 22.0))
    return root, lights


def build(M):
    coll = U.collection("07 İç mekân")
    ecoll = U.collection("08 Ekipman")
    i0, i1 = C.phase("interior")
    e0, e1 = C.phase("equipment")

    floor = U.slab("zemin laminat", 0.11, Z(C.FLOOR_H - 0.012), Z(C.FLOOR_H), [M["floor"]], coll)
    U.arrive(floor, i0, i0 + 12, offset=(0, 0, 1.5), interp="EXPO")

    deck, lights = service_deck(M, coll)
    U.arrive(deck, C.phase("finale")[0], C.phase("finale")[0] + 14, offset=(0, 0, 3.0), interp="BACK",
             visible=False)
    U.show_tree(deck, C.phase("finale")[0])

    # Cabinets and counters.
    front_body, front_top = _counter(M, coll, "ön tezgâh", -1.42, 1.98, -1, doors_steel=(1, 2))
    back_body, back_top = _counter(M, coll, "arka tezgâh", -1.32, 1.98, +1)
    storage = _tall_unit(M, coll, "kiler dolabı", -2.02, -1.46, -1, 2.05)
    fridge = _tall_unit(M, coll, "içecek dolabı", -2.0, -1.36, +1, 1.95, glass_door=True)
    carcasses = [front_body, back_body, storage, fridge]
    for root, st, en in U.stagger(carcasses, i0 + 10, i0 + 52, 16):
        U.arrive(root, st, en, offset=(0, 0, 2.6), interp="BACK", visible=False)
        U.show_tree(root, st)
    for root, st, en in U.stagger([front_top, back_top], i0 + 56, i0 + 72, 12):
        U.arrive(root, st, en, offset=(0, 0, 1.4), interp="BACK", visible=False)
        U.show_tree(root, st)

    # Back-wall floating shelves with under-shelf LED.
    shelf_led = Mt.principled("shelf led", (0.9, 0.9, 0.9, 1), rough=0.3, emission="led-warm")
    lights["emit"].append(shelf_led)
    shelves = []
    for k, h in enumerate((1.50, 1.86)):
        root = _group(f"duvar rafı {k}", coll, (-0.15, WALL - 0.13, Z(C.FLOOR_H + h)))
        _add(root,
             U.box(f"duvar rafı {k} tabla", (2.3, 0.26, 0.035), (0, 0, 0), coll, [M["oak"]], bevel=0.003),
             U.box(f"duvar rafı {k} LED", (2.2, 0.01, 0.004), (0, -0.09, -0.0195), coll, [shelf_led]))
        shelves.append(root)
    for root, st, en in U.stagger(shelves, i1 - 14, i1 + 4, 10):
        U.arrive(root, st, en, offset=(0, -0.6, 0.0), interp="BACK", visible=False)
        U.show_tree(root, st)

    # Equipment, dropped in one by one. Front counter faces +Y (barista side).
    top = Z(TOP)
    face_aisle_front, face_aisle_back = (0, 0, math.pi), (0, 0, 0)
    fy, by = -(WALL - DEPTH / 2) - 0.03, WALL - DEPTH / 2
    equipment = [
        espresso_machine(M, ecoll, (1.35, fy, top), face_aisle_front),
        grinder(M, ecoll, (1.86, fy + 0.02, top), face_aisle_front),
        pastry_case(M, ecoll, (-0.70, fy, top), face_aisle_front),
        pos_terminal(M, ecoll, (-1.15, fy + 0.12, top), face_aisle_front),
        toaster(M, ecoll, (-0.85, by, top), face_aisle_back),
        tea_urn(M, ecoll, (0.05, by + 0.05, top), face_aisle_back),
        sink(M, ecoll, (1.45, by, top - 0.012), face_aisle_back),
    ]
    small = [
        cup_stacks(M, ecoll, (0.0, fy - 0.12, top), (0, 0, 0)),
        tea_glasses(M, ecoll, (-1.15, WALL - 0.17, Z(C.FLOOR_H + 1.5175)), (0, 0, 0), rows=2, cols=9),
        shelf_goods(M, ecoll, (-1.1, WALL - 0.14, Z(C.FLOOR_H + 1.8775)), (0, 0, 0)),
        tea_glasses(M, ecoll, (0.45, WALL - 0.17, Z(C.FLOOR_H + 1.5175)), (0, 0, 0), rows=2, cols=7),
    ]
    extinguisher = _group("yangın tüpü", ecoll, (2.12, 1.05, Z(C.FLOOR_H)))
    _add(extinguisher,
         U.cylinder("yangın tüpü gövde", 0.075, 0.45, (0, 0, 0.02), ecoll, [M["red"]], verts=32),
         U.cylinder("yangın tüpü vana", 0.02, 0.08, (0, 0, 0.47), ecoll, [M["black-plastic"]], verts=16))
    bin_ = _group("çöp kovası", ecoll, (-2.05, 0.0, Z(C.FLOOR_H)))
    _add(bin_, U.cylinder("çöp kovası gövde", 0.17, 0.62, (0, 0, 0), ecoll, [M["steel"]], verts=40, r2=0.18))
    equipment += [extinguisher, bin_]
    for root, st, en in U.stagger(equipment, e0 + 4, e1 - 30, 16):
        U.arrive(root, st, en, offset=(0, 0, 1.8), interp="BACK", visible=False)
        U.show_tree(root, st)
    for root, st, en in U.stagger(small, e1 - 34, e1 - 8, 12):
        U.arrive(root, st, en, offset=(0, 0, 0.6), interp="BACK", visible=False)
        U.show_tree(root, st)
    return lights
