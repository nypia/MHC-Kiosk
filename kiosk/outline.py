"""Rounded-rectangle outline of the kiosk (pure Python, no Blender).

Every wall layer (slats, battens, panels, frame, fascia) is a band along this
outline at some depth d measured inward from the outer footprint, addressed by
arc length s along the outer outline. s = 0 is the middle of the front face,
running counter-clockwise (towards +X first), so on the front face s == x.
"""
import math

from . import config as C

R = C.CORNER_R
HX = C.A - R          # half length of the straight part, front/back
HY = C.B - R          # half length of the straight part, sides
CQ = math.pi * R / 2  # quarter-circle arc length

# (length, kind, data): straight = (start point, direction, normal)
#                       arc      = (centre, start angle)
_SEGS = [
    (HX, "line", ((0, -C.B), (1, 0), (0, -1))),
    (CQ, "arc", ((HX, -HY), -math.pi / 2)),
    (2 * HY, "line", ((C.A, -HY), (0, 1), (1, 0))),
    (CQ, "arc", ((HX, HY), 0.0)),
    (2 * HX, "line", ((HX, C.B), (-1, 0), (0, 1))),
    (CQ, "arc", ((-HX, HY), math.pi / 2)),
    (2 * HY, "line", ((-C.A, HY), (0, -1), (-1, 0))),
    (CQ, "arc", ((-HX, -HY), math.pi)),
    (HX, "line", ((-HX, -C.B), (1, 0), (0, -1))),
]
TOTAL = sum(seg[0] for seg in _SEGS)
BREAKS = []
_acc = 0.0
for _seg in _SEGS:
    BREAKS.append(_acc)
    _acc += _seg[0]
BREAKS.append(TOTAL)


def perim(s):
    """Point on the outer outline and its outward normal: (x, y, nx, ny)."""
    s %= TOTAL
    for start, (length, kind, data) in zip(BREAKS, _SEGS):
        if s <= start + length + 1e-9:
            t = s - start
            if kind == "line":
                (px, py), (dx, dy), (nx, ny) = data
                return px + dx * t, py + dy * t, nx, ny
            (cx, cy), a0 = data
            a = a0 + t / R
            nx, ny = math.cos(a), math.sin(a)
            return cx + R * nx, cy + R * ny, nx, ny
    raise AssertionError(s)


def at(s, d=0.0):
    x, y, nx, ny = perim(s)
    return x - d * nx, y - d * ny


def normal2(s):
    """Outward normal (nx, ny)."""
    _, _, nx, ny = perim(s)
    return nx, ny


def tangent2(s):
    """Counter-clockwise tangent (tx, ty)."""
    _, _, nx, ny = perim(s)
    return -ny, nx


# Arc-length addresses of points on the four straight faces.
def s_front(x):
    return x


def s_right(y):
    return HX + CQ + (y + HY)


def s_back(x):
    return HX + 2 * CQ + 2 * HY + (HX - x)


def s_left(y):
    return HX + 3 * CQ + 2 * HX + 2 * HY + (HY - y)


def samples(s0, s1, step=0.03):
    """Arc lengths from s0 to s1: every outline break plus `step` on arcs."""
    out = [s0]
    s = s0
    while s < s1 - 1e-9:
        base = math.floor(s / TOTAL) * TOTAL
        local = s - base
        i = next(k for k in range(1, len(BREAKS)) if BREAKS[k] > local + 1e-9)
        nxt = BREAKS[i] + base
        if _SEGS[i - 1][1] == "arc":
            nxt = min(nxt, s + step)
        s = min(nxt, s1)
        out.append(s)
    return out
