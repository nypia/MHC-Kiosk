"""Part layout of the shell (pure Python, no Blender).

Shared by the 3D model (shell.py) and the fabrication drawings, so both always
agree. Positions are arc lengths s along the outer outline (see outline.py),
heights are relative to BASE_Z. Every part gets a fabrication number:
D = steel post, P = wall panel, KM = curved corner module, K = Alucobond
cassette, Ç = slat.
"""
from . import config as C
from . import outline as O

T = O.TOTAL
B = O.BREAKS
LOOP_START = B[7]   # front-left corner: numbering and wrap-around sequences start here
ARCS = [(B[1], B[2]), (B[3], B[4]), (B[5], B[6]), (B[7], B[8])]  # the four corner arcs

FACE_NAMES = {"front": "Ön cephe", "right": "Sağ cephe (kapı)", "back": "Arka cephe",
              "left": "Sol cephe", "corner": "Köşe"}


def loop_pos(s):
    """Position of s along the loop measured from LOOP_START, in [0, T)."""
    return (s - LOOP_START) % T


def face_of(s):
    """Which face a point sits on (corners count as 'corner')."""
    p = s % T
    for a, b in ARCS:
        if a - 1e-9 <= p <= b + 1e-9:
            return "corner"
    if p < B[1] or p > B[8]:
        return "front"
    if p < B[3]:
        return "right"
    if p < B[5]:
        return "back"
    return "left"


def is_curved(s0, s1):
    """True if the range s0..s1 overlaps a corner arc."""
    a0, a1 = loop_pos(s0), loop_pos(s0) + (s1 - s0)
    for a, b in ARCS:
        p, q = loop_pos(a), loop_pos(a) + (b - a)
        if a0 < q - 1e-6 and a1 > p + 1e-6:
            return True
    return False


def openings():
    """(name, s0, s1, z0, z1) of each wall opening."""
    return [
        ("pencere", O.s_front(C.WIN_X[0]), O.s_front(C.WIN_X[1]), C.WIN_SILL, C.WIN_HEAD),
        ("kapı", O.s_right(C.DOOR_Y[0]), O.s_right(C.DOOR_Y[1]), C.SKIRT_H, C.DOOR_HEAD),
    ]


def free_ranges(z0, z1):
    """Arc-length ranges around the loop not blocked by an opening at heights z0..z1."""
    cuts = sorted((loop_pos(a), loop_pos(a) + (b - a))
                  for _, a, b, oz0, oz1 in openings() if oz0 < z1 and oz1 > z0)
    out, cur = [], 0.0
    for a, b in cuts:
        if a > cur:
            out.append((LOOP_START + cur, LOOP_START + a))
        cur = max(cur, b)
    if cur < T:
        out.append((LOOP_START + cur, LOOP_START + T))
    return out


def segments_of_vertical(s, half_w, z0, z1, margin=0.012):
    """Z-ranges of a vertical element at s (width 2*half_w) avoiding openings."""
    ranges = [(z0, z1)]
    for _, a, b, oz0, oz1 in openings():
        p, pa = loop_pos(s), loop_pos(a)
        if pa - half_w - margin <= p <= pa + (b - a) + half_w + margin:
            nxt = []
            for r0, r1 in ranges:
                if r0 < oz0:
                    nxt.append((r0, min(r1, oz0)))
                if r1 > oz1:
                    nxt.append((max(r0, oz1), r1))
            ranges = nxt
    return [(a, b) for a, b in ranges if b - a > 0.04]


# ------------------------------------------------------------------ chassis
def posts():
    """Steel posts: (id, s, role). Two per corner at the arc tangent points."""
    items = []
    for k, (a, b) in enumerate(ARCS):
        items += [(a, "köşe teğet"), (b, "köşe teğet")]
    extra = [(O.s_front(C.WIN_X[0] - 0.03), "pencere sövesi"), (O.s_front(C.WIN_X[1] + 0.03), "pencere sövesi"),
             (O.s_right(C.DOOR_Y[0] - 0.03), "kapı sövesi"), (O.s_right(C.DOOR_Y[1] + 0.03), "kapı sövesi"),
             (O.s_back(-1.4), "ara dikme"), (O.s_back(0.0), "ara dikme"), (O.s_back(1.4), "ara dikme"),
             (O.s_left(0.0), "ara dikme")]
    for s, role in extra:
        # a jamb right next to a corner post is carried by that post
        if all(abs(loop_pos(s) - loop_pos(p)) > 0.10 for p, _ in items):
            items.append((s, role))
    items.sort(key=lambda it: loop_pos(it[0]))
    return [(f"D{i + 1:02d}", s, role) for i, (s, role) in enumerate(items)]


JOIST_X = (-2.0, -1.0, 0.0, 1.0, 2.0)
RIB_Z = (1.30, 2.30)  # curved corner ribs between base frame and top ring


# ------------------------------------------------------------------ panels
def _raw_panel_pieces():
    pieces = [
        (B[8], T + O.s_front(C.WIN_X[0]), "wall"),
        (O.s_front(C.WIN_X[0]), O.s_front(C.WIN_X[1]), "window"),
        (O.s_front(C.WIN_X[1]), B[2], "wall"),
        (B[2], O.s_right(C.DOOR_Y[0]), "wall"),
        (O.s_right(C.DOOR_Y[0]), O.s_right(C.DOOR_Y[1]), "door"),
        (O.s_right(C.DOOR_Y[1]), B[3], "wall"),
        (B[3], B[4], "wall"),
    ]
    back = [B[4] + (B[5] - B[4]) * k / 4 for k in range(5)]
    pieces += [(back[k], back[k + 1], "wall") for k in range(4)]
    pieces.append((B[5], B[6], "wall"))
    left = [B[6] + (B[7] - B[6]) * k / 2 for k in range(3)]
    pieces += [(left[k], left[k + 1], "wall") for k in range(2)]
    pieces.append((B[7], B[8], "wall"))
    return sorted(pieces, key=lambda p: loop_pos(p[0] + 1e-6))


PANEL_GAP = 0.0015


def panels():
    """Wall modules around the loop.

    Each: dict(id, s0, s1, kind, curved, spans=[(z0, z1, is_cutout)]).
    Straight modules are sandwich panels (P..), curved ones are bent-sheet
    corner modules (KM..). Cut-outs are removed on site (window, door).
    """
    out, np, nk = [], 0, 0
    for s0, s1, kind in _raw_panel_pieces():
        curved = is_curved(s0, s1)
        if curved:
            nk += 1
            pid = f"KM{nk}"
        else:
            np += 1
            pid = f"P{np:02d}"
        z0, z1 = C.FRAME_BASE_H, C.PANEL_TOP
        if kind == "wall":
            spans = [(z0, z1, False)]
        elif kind == "window":
            spans = [(z0, C.WIN_SILL, False), (C.WIN_SILL, C.WIN_HEAD, True), (C.WIN_HEAD, z1, False)]
        else:
            spans = [(z0, C.DOOR_HEAD, True), (C.DOOR_HEAD, z1, False)]
        out.append(dict(id=pid, s0=s0 + PANEL_GAP, s1=s1 - PANEL_GAP, kind=kind, curved=curved, spans=spans,
                        face=face_of((s0 + s1) / 2) if not curved else "corner"))
    return out


# ------------------------------------------------------------------ cladding
RAIL_Z = (0.30, 1.30, 2.30)
RAIL_H = 0.045


def rails():
    """Batten rails: (z, s0, s1)."""
    return [(zr, a + 0.002, b - 0.002) for zr in RAIL_Z for a, b in free_ranges(zr, zr + RAIL_H)]


def slats():
    """Vertical slats: (id, s, [(z0, z1), ...]). Even pitch close to SLAT_PITCH all round."""
    count = round(T / C.SLAT_PITCH)
    pitch = T / count
    out = []
    for i in range(count):
        s = LOOP_START + (i + 0.5) * pitch
        segs = segments_of_vertical(s, C.SLAT_W / 2, C.SKIRT_H + 0.005, C.FASCIA_Z[0])
        out.append((f"Ç{i + 1:03d}", s, segs))
    return out, pitch


# ------------------------------------------------------------------ fascia
CASSETTE_JOINT = 0.008
FASCIA_D = (-0.018, 0.030)   # cassette face 18 mm proud of the slat face


def cassettes():
    """Alucobond fascia cassettes: (id, s0, s1, curved), numbered from the front-left corner."""
    cuts = [B[8] + (T + B[1] - B[8]) * k / 4 for k in range(5)]
    cuts += [B[2], B[2] + (B[3] - B[2]) / 2, B[3]]
    cuts += [B[4] + (B[5] - B[4]) * k / 4 for k in range(5)]
    cuts += [B[6], B[6] + (B[7] - B[6]) / 2, B[7], B[8]]
    cuts = sorted({round(loop_pos(c), 6) for c in cuts})
    cuts.append(T)
    j = CASSETTE_JOINT / 2
    out = []
    for k in range(len(cuts) - 1):
        s0, s1 = LOOP_START + cuts[k] + j, LOOP_START + cuts[k + 1] - j
        out.append((f"K{k + 1:02d}", s0, s1, is_curved(s0, s1)))
    return out
