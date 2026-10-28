"""Exterior shell and its build sequence.

chassis -> sandwich panels -> openings cut -> battens + walnut slats ->
Alucobond fascia -> glazing, menu screen, door, signage.
"""
import math

from mathutils import Matrix, Vector

from . import config as C
from . import layout as L
from . import materials as Mt
from . import util as U

Z = C.z
F = C.f
T = U.TOTAL


def _tilt_euler(n, angle):
    """Rotation that tips a wall piece outward about its base line."""
    axis = Vector((0, 0, 1)).cross(n).normalized()
    return Matrix.Rotation(angle, 3, axis).to_euler()


# ====================================================================== chassis
def build_chassis(M):
    col = U.collection("02 Şasi")
    f0, f1 = C.phase("chassis")
    steel = [M["steel-frame"]] * 3

    base, _ = U.band("şasi taban çerçeve", 0, T, 0.05, 0.17, Z(0.0), Z(C.FRAME_BASE_H), steel, col)
    U.arrive(base, f0, f0 + 20, offset=(0, 0, 2.0), interp="BACK")

    joists = []
    for i, x in enumerate(L.JOIST_X):
        j = U.box(f"şasi kiriş {i}", (0.05, 2 * (C.B - 0.17), 0.10), (x, 0, Z(C.FRAME_BASE_H - 0.05)), col,
                  [M["steel-frame"]])
        joists.append(j)
    for j, st, en in U.stagger(joists, f0 + 12, f0 + 40, 12):
        U.arrive(j, st, en, offset=(0, 0, 1.5), interp="BACK")

    deck = U.slab("döşeme kontrplak", 0.11, Z(C.FRAME_BASE_H), Z(C.FLOOR_H - 0.010), [M["steel-frame"]], col)
    U.arrive(deck, f0 + 34, f0 + 52, offset=(0, 0, 1.2), interp="BACK")

    h = C.RING_Z[0] - C.FRAME_BASE_H
    posts = []
    for pid, s, _role in L.posts():
        x, y = U.at(s, 0.14)
        rz = math.atan2(U.tangent(s).y, U.tangent(s).x)
        posts.append(U.box(f"şasi dikme {pid}", (0.06, 0.06, h), (x, y, Z(C.FRAME_BASE_H)), col,
                           [M["steel-frame"]], rot=(0, 0, rz), origin="bottom"))
    for p, st, en in U.stagger(posts, f0 + 44, f0 + 86, 14):
        U.grow(p, st, en)

    ribs = []
    for k, (a0, a1) in enumerate(L.ARCS):
        for zr in L.RIB_Z:
            rib, _ = U.band(f"köşe kaburga {k + 1} {zr:.2f}", a0, a1, 0.11, 0.13, Z(zr - 0.02), Z(zr + 0.02),
                            steel, col)
            ribs.append(rib)
    for r_, st, en in U.stagger(ribs, f0 + 80, f0 + 96, 8):
        U.arrive(r_, st, en, offset=(0, 0, 0.6), interp="BACK")

    beams = []
    wl = C.WIN_X[1] - C.WIN_X[0]
    wx = sum(C.WIN_X) / 2
    for name, zc in (("lento", C.WIN_HEAD + 0.05), ("denizlik kirişi", C.WIN_SILL - 0.05)):
        beams.append(U.box(f"şasi {name}", (wl, 0.06, 0.10), (wx, -C.B + 0.14, Z(zc)), col, [M["steel-frame"]]))
    dl = C.DOOR_Y[1] - C.DOOR_Y[0]
    beams.append(U.box("şasi kapı lentosu", (0.06, dl, 0.10), (C.A - 0.14, 0, Z(C.DOOR_HEAD + 0.05)), col,
                       [M["steel-frame"]]))
    for b, st, en in U.stagger(beams, f0 + 88, f0 + 100, 10):
        U.arrive(b, st, en, offset=(0, 0, 0.8), interp="BACK")

    ring, _ = U.band("şasi üst çerçeve", 0, T, 0.11, 0.17, Z(C.RING_Z[0]), Z(C.RING_Z[1]), steel, col)
    U.arrive(ring, f0 + 96, f1, offset=(0, 0, 2.5), interp="BACK")


# ====================================================================== panels
def build_panels(M):
    col = U.collection("03 Sandviç panel")
    f0, f1 = C.phase("panels")
    mats = [M["anthracite"], M["panel-white"], M["panel-core"]]
    groups, cutouts = [], []
    for pn in L.panels():
        spans = pn["spans"]
        group = []
        for k, (z0, z1, is_cut) in enumerate(spans):
            obj, n = U.band(f"panel {pn['id']}{'abc'[k] if len(spans) > 1 else ''}", pn["s0"], pn["s1"],
                            *C.PANEL_D, Z(z0), Z(z1), mats, col)
            group.append((obj, n))
            if is_cut:
                cutouts.append((obj, n))
        groups.append(group)

    for group, st, en in U.stagger(groups, f0, f1 - 14, 18):
        for k, (obj, n) in enumerate(group):
            U.arrive(obj, st + 2 * k, en + 2 * k, offset=n * 1.6 + Vector((0, 0, 1.0)), interp="BACK")

    roof = U.slab("çatı paneli", 0.05, Z(C.PANEL_TOP), Z(C.ROOF_Z), [M["anthracite"]], col)
    U.arrive(roof, f1 - 16, f1, offset=(0, 0, 3.0), interp="BACK")
    return roof, cutouts


def animate_openings(cutouts):
    f0, f1 = C.phase("openings")
    for i, (obj, n) in enumerate(cutouts):
        st = f0 + 6 + i * 26
        loc = obj.location.copy()
        U.key(obj, "location", st, loc, "SINE", "EASE_IN_OUT")
        U.key(obj, "rotation_euler", st, obj.rotation_euler.copy())
        U.key(obj, "location", st + 10, loc + n * 0.10, "QUAD", "EASE_IN")
        U.key(obj, "rotation_euler", st + 10, obj.rotation_euler.copy(), "QUAD", "EASE_IN")
        U.key(obj, "location", st + 28, loc + n * 1.1 + Vector((0, 0, -0.9)))
        U.key(obj, "rotation_euler", st + 28, _tilt_euler(n, 0.9))
        U.hide_from(obj, st + 28)


# ====================================================================== cladding
def build_cladding(M):
    col = U.collection("04 Ahşap çıta kaplama")
    f0, f1 = C.phase("slats")
    alu = [M["alucobond"]] * 2 + [M["alucobond-edge"]]

    skirt, _ = U.band("süpürgelik", 0, T, -0.006, 0.05, Z(0.0), Z(C.SKIRT_H), alu, col)
    U.arrive(skirt, f0, f0 + 14, offset=(0, 0, -0.2), interp="EXPO")

    rails = []
    for k, (zr, a, b) in enumerate(L.rails()):
        obj, n = U.band(f"karkas {zr:.2f} {k}", a, b, *C.BATTEN_D, Z(zr), Z(zr + L.RAIL_H), [M["batten"]] * 3, col)
        rails.append((obj, n))
    for (obj, n), st, en in U.stagger(rails, f0 + 4, f0 + 22, 10):
        U.arrive(obj, st, en, offset=n * 0.4, interp="EXPO")

    d = sum(C.SLAT_D) / 2
    depth = C.SLAT_D[1] - C.SLAT_D[0]
    slats = []
    for sid, s, segs in L.slats()[0]:
        x, y = U.at(s, d)
        t = U.tangent(s)
        rz = math.atan2(t.y, t.x)
        pieces = []
        for z0, z1 in segs:
            length = round(z1 - z0, 3)
            pieces.append(U.box(f"çıta {sid}", (C.SLAT_W, depth, length), (x, y, Z((z0 + z1) / 2)), col,
                                [M["walnut"]], rot=(0, 0, rz), bevel=0.002))
        slats.append((pieces, U.normal(s)))
    for (pieces, n), st, en in U.stagger(slats, f0 + 20, f1, 9):
        for p in pieces:
            U.arrive(p, st, en, offset=n * 0.35 + Vector((0, 0, 0.04)), interp="BACK")


# ====================================================================== fascia
def build_fascia(M, roof):
    col = U.collection("05 Alucobond saçak")
    f0, f1 = C.phase("fascia")
    alu = [M["alucobond"]] * 2 + [M["alucobond-edge"]]
    z0, z1 = Z(C.FASCIA_Z[0]), Z(C.FASCIA_Z[1])

    backing, _ = U.band("saçak derz fonu", 0, T, 0.03, 0.05, z0, z1, [M["alucobond-edge"]] * 3, col)
    U.arrive(backing, f0, f0 + 10, offset=(0, 0, 0.3), interp="EXPO")

    cassettes = []
    for kid, s0, s1, _curved in L.cassettes():
        obj, n = U.band(f"alucobond kaset {kid}", s0, s1, *L.FASCIA_D, z0, z1, alu, col)
        cassettes.append((obj, n))
    for (obj, n), st, en in U.stagger(cassettes, f0 + 6, f1 - 10, 12):
        U.arrive(obj, st, en, offset=n * 0.7 + Vector((0, 0, 0.25)), interp="BACK")

    coping, _ = U.band("parapet kapağı", 0, T, -0.022, 0.07, z1 - 0.015, z1 + 0.004, alu, col)
    U.arrive(coping, f1 - 12, f1, offset=(0, 0, 0.5), interp="EXPO")

    # Rooftop condenser, parented to the roof so it leaves with it.
    # The roof's origin is the world origin, so local == world here.
    ao = L.AC_OUTDOOR
    ac = U.box("klima dış ünite", (ao["w"], ao["d"], ao["h"]), (ao["x"], ao["y"], Z(C.ROOF_Z) + ao["feet"] + ao["h"] / 2), col,
               [M["white-appliance"]], bevel=0.01)
    U.parent(ac, roof)
    fan = U.cylinder("klima fan ızgarası", 0.2, 0.01, (-0.12, -0.151, 0.0), col, [M["black-plastic"]],
                     rot=(math.pi / 2, 0, 0), origin="center")
    U.parent(fan, ac)
    U.arrive(ac, f1 - 20, f1 - 4, offset=(0, 0, 2.0), interp="BACK", visible=False)
    U.show_tree(ac, f1 - 20)
    return ac


# ====================================================================== glazing
def _logo(M, col, name, loc, rot):
    root = U.empty(name, col, loc, rot)
    disk = U.cylinder(f"{name} disk", L.LOGO_R, L.LOGO_T, (0, 0, 0), col, [M["alucobond"]], verts=96,
                      rot=(math.pi / 2, 0, 0), origin="center")
    U.parent(disk, root)
    up = (math.pi / 2, 0, 0)
    U.parent(U.text(f"{name} MHC", "MHC", "Fraunces-SemiBold.ttf", 0.27, col, M["cream"],
                    loc=(0, -0.026, 0.05), rot=up, extrude=0.003), root)
    U.parent(U.text(f"{name} KAHVE", "KAHVE", "Jost-Medium.ttf", 0.075, col, M["cream"],
                    loc=(0, -0.026, -0.13), rot=up, extrude=0.003, spacing=1.7), root)
    return root


def build_glazing(M):
    col = U.collection("06 Cam, ekran, kapı, tabela")
    f0, f1 = C.phase("glazing")
    alu, black = [M["alucobond"]], [M["black-plastic"]]
    fy = -C.B                       # front outer face
    x0, x1 = C.WIN_X
    sill, head = C.WIN_SILL, C.WIN_HEAD
    ny = Vector((0, -1, 0))

    # Reveal liners and window frame profiles.
    frame = []
    ly, ld = fy + (C.INNER - 0.018) / 2, C.INNER + 0.018
    frame += [U.box("pencere söve sol", (0.02, ld, head - sill), (x0 + 0.01, ly, Z((sill + head) / 2)), col, alu),
              U.box("pencere söve sağ", (0.02, ld, head - sill), (x1 - 0.01, ly, Z((sill + head) / 2)), col, alu),
              U.box("pencere söve üst", (x1 - x0, ld, 0.02), ((x0 + x1) / 2, ly, Z(head - 0.01)), col, alu),
              U.box("pencere denizlik", (x1 - x0, ld + 0.03, 0.02), ((x0 + x1) / 2, ly - 0.015, Z(sill + 0.01)),
                    col, alu)]
    py = fy + 0.085
    prof, panes_l, (scr_x, scr_z, scr_w, scr_h) = L.window()
    for name, cx, cz, w, h in prof:
        frame.append(U.box(f"doğrama {name}", (w, 0.05, h), (cx, py, Z(cz)), col, black, bevel=0.002))
    for obj, st, en in U.stagger(frame, f0, f0 + 20, 8):
        U.arrive(obj, st, en, offset=ny * 0.5, interp="BACK")

    # Menu screen (55", landscape) hung just inside the middle bay.
    scr_y = fy + C.INNER + 0.035
    screen = U.rounded_box("menü ekranı gövde", (scr_w, 0.04, scr_h), 0.006, (scr_x, scr_y, Z(scr_z)), col, black)
    menu = Mt.emissive_image("menu screen", C.ROOT / "kiosk" / "art" / "menu.png")
    disp = U.quad("menü ekranı panel", scr_w - 0.03, scr_h - 0.03, col, [menu], loc=(0, -0.0205, 0))
    U.parent(disp, screen)
    for k, dx in enumerate((-0.4, 0.4)):
        rod_h = Z(C.CEILING_Z) - Z(scr_z + scr_h / 2)
        rod = U.cylinder(f"ekran askı {k}", 0.008, rod_h, (dx, 0.0, scr_h / 2), col, [M["steel"]], verts=12)
        U.parent(rod, screen)
    U.arrive(screen, f0 + 16, f0 + 34, offset=(0, 0.9, 0.5), interp="BACK", visible=False)
    U.show_tree(screen, f0 + 16)
    # power on with a short flicker
    on = f0 + 52
    for fr, v in ((0, 0.0), (on, 0.0), (on + 2, 3.0), (on + 4, 0.4), (on + 6, 4.0), (on + 7, 3.2), (on + 12, 4.0)):
        Mt.key_emission(menu, fr, v)

    # Glass panes; the lower right pane is the sliding pick-up hatch.
    panes = [(name, cx, cz, w, h, py + inset) for name, cx, cz, w, h, inset in panes_l]
    glass = []
    for name, cx, cz, w, h, y in panes:
        glass.append(U.box(f"cam {name}", (w + 0.02, 0.008, h + 0.02), (cx, y, Z(cz)), col, [M["glass"]]))
    for obj, st, en in U.stagger(glass, f0 + 30, f0 + 50, 10):
        U.arrive(obj, st, en, offset=ny * 0.6, interp="BACK")
    hatch = glass[-1]

    # Canopy with LED strip over the window.
    cy = fy - 0.07
    canopy = U.box("pencere saçağı", (x1 - x0 + 0.08, 0.16, 0.03), ((x0 + x1) / 2, cy + 0.01, Z(head + 0.05)), col,
                   alu, bevel=0.003)
    led = U.box("LED şerit", (x1 - x0, 0.012, 0.004), ((x0 + x1) / 2, cy - 0.04, Z(head + 0.033)), col, [M["led"]])
    for obj in (canopy, led):
        U.arrive(obj, f0 + 6, f0 + 20, offset=ny * 0.6, interp="BACK")
    for fr, v in ((0, 0.0), (on + 8, 0.0), (on + 14, 18.0)):
        Mt.key_emission(M["led"], fr, v)

    # Outside bar shelves under the order and pick-up windows.
    shelves = []
    for name, a, b in L.bar_shelves():
        w = b - a
        cx = (a + b) / 2
        top = sill
        sh = U.box(f"bar rafı {name}", (w, L.BAR_SHELF["depth"], L.BAR_SHELF["t"]), (cx, fy - 0.15, Z(top - 0.02)),
                   col, [M["oak"]], bevel=0.003)
        parts = [sh]
        for k, bx in enumerate((a + 0.12, b - 0.12)):
            arm = U.box(f"konsol {name} {k}", (0.012, 0.24, 0.025), (bx, fy - 0.13, Z(top - 0.0525)), col, black)
            leg = U.box(f"konsol dikme {name} {k}", (0.012, 0.02, 0.22), (bx, fy - 0.01, Z(top - 0.15)), col, black)
            ang = math.atan2(0.17, 0.20)
            strut = U.box(f"konsol payanda {name} {k}", (0.012, 0.262, 0.018),
                          (bx, fy - 0.11, Z(top - 0.15)), col, black, rot=(ang, 0, 0))
            parts += [arm, leg, strut]
        shelves.append(parts)
    for parts, st, en in U.stagger(shelves, f0 + 40, f0 + 60, 12):
        for p in parts:
            U.arrive(p, st, en, offset=(0, -0.5, 0.1), interp="BACK")

    # Door on the +X side.
    dx = C.A
    dy0, dy1 = C.DOOR_Y
    dz0, dz1 = C.SKIRT_H, C.DOOR_HEAD
    lx, ldd = dx - (C.INNER - 0.018) / 2, C.INNER + 0.018
    door_parts = [
        U.box("kapı söve sol", (ldd, 0.02, dz1 - dz0), (lx, dy0 + 0.01, Z((dz0 + dz1) / 2)), col, alu),
        U.box("kapı söve sağ", (ldd, 0.02, dz1 - dz0), (lx, dy1 - 0.01, Z((dz0 + dz1) / 2)), col, alu),
        U.box("kapı söve üst", (ldd, dy1 - dy0, 0.02), (lx, 0, Z(dz1 - 0.01)), col, alu),
    ]
    leaf = U.box("kapı kanadı", (0.05, dy1 - dy0 - 0.05, dz1 - dz0 - 0.04), (dx - 0.08, 0, Z((dz0 + dz1) / 2)), col,
                 alu, bevel=0.004)
    handle = U.cylinder("kapı kolu", 0.014, 0.45, (0.05, (dy1 - dy0) / 2 - 0.12, -0.05), col, [M["steel"]],
                        verts=16, origin="center")
    U.parent(handle, leaf)
    for k, hz in enumerate((-0.2, 0.15)):
        U.parent(U.cylinder(f"kapı kolu ayak {k}", 0.008, 0.05, (0.025, (dy1 - dy0) / 2 - 0.12, hz - 0.05), col,
                            [M["steel"]], verts=12, rot=(0, math.pi / 2, 0), origin="center"), leaf)
    door_parts.append(leaf)
    for obj, st, en in U.stagger(door_parts, f0 + 20, f0 + 44, 12):
        U.arrive(obj, st, en, offset=(0.8, 0, 0.2), interp="BACK", visible=False)
        U.show_tree(obj, st)

    # Signage: logo disks + "KAHVE · TOST · ÇAY" board, installed as the fascia closes.
    fs0, fs1 = C.phase("fascia")
    zc = Z(L.LOGO_Z)
    logos = [_logo(M, col, "logo ön", (L.LOGOS["front"], fy - 0.018 - 0.055, zc), (0, 0, 0)),
             _logo(M, col, "logo yan", (-C.A - 0.018 - 0.055, L.LOGOS["left"], zc), (0, 0, -math.pi / 2))]
    sg = L.SIGN
    board = U.empty("tabela", col, (sg["x"], fy - 0.018 - 0.03, Z(sg["z"])))
    U.parent(U.box("tabela pano", (sg["w"], sg["t"], sg["h"]), (0, 0, 0), col, alu, bevel=0.004), board)
    for k, (bx, bz, bw, bh) in enumerate(((0, 0.107, 1.27, 0.006), (0, -0.107, 1.27, 0.006),
                                          (-0.632, 0, 0.006, 0.22), (0.632, 0, 0.006, 0.22))):
        U.parent(U.box(f"tabela çerçeve {k}", (bw, 0.004, bh), (bx, -0.016, bz), col, [M["cream"]]), board)
    U.parent(U.text("tabela yazı", sg["text"], "Fraunces-SemiBold.ttf", 0.115, col, M["cream"],
                    loc=(0, -0.016, 0.0), rot=(math.pi / 2, 0, 0), extrude=0.002, spacing=1.08), board)
    for root, st in ((logos[0], fs1 - 14), (board, fs1 - 8), (logos[1], fs1 - 4)):
        n = Vector((0, -1, 0)) if root is not logos[1] else Vector((-1, 0, 0))
        U.arrive(root, st, st + 16, offset=n * 0.6 + Vector((0, 0, 0.3)), interp="BACK", visible=False)
        U.show_tree(root, st)
    for fr, v in ((0, 0.0), (on + 10, 0.0), (on + 16, 0.6)):
        Mt.key_emission(M["cream"], fr, v)

    return {"hatch": hatch, "screen": screen}
