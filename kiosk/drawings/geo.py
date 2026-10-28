"""2D geometry for the drawings, derived from outline.py / layout.py."""
import math

from .. import config as C
from .. import layout as L
from .. import outline as O

# face -> (u axis, outward normal); u is the horizontal coordinate as seen from outside
FACES = {
    "front": ((1, 0), (0, -1)),
    "right": ((0, 1), (1, 0)),
    "back": ((-1, 0), (0, 1)),
    "left": ((0, -1), (-1, 0)),
}
HALF = {"front": C.A, "back": C.A, "right": C.B, "left": C.B}
FACE_TITLE = {"front": "ÖN GÖRÜNÜŞ (servis cephesi)", "right": "SAĞ GÖRÜNÜŞ (kapı)", "back": "ARKA GÖRÜNÜŞ",
              "left": "SOL GÖRÜNÜŞ"}


def ring(d, step=0.02):
    return [O.at(s, d) for s in O.samples(0, O.TOTAL, step)[:-1]]


def band(s0, s1, d0, d1, step=0.02):
    ss = O.samples(s0, s1, step)
    return [O.at(s, d0) for s in ss] + [O.at(s, d1) for s in reversed(ss)]


def perimeter(d):
    """Length of the outline offset inward by d."""
    return 4 * O.HX + 4 * O.HY + 2 * math.pi * (O.R - d)


def rounded_area(d):
    a, b, r = C.LENGTH - 2 * d, C.WIDTH - 2 * d, O.R - d
    return a * b - (4 - math.pi) * r * r


def project(face, x, y):
    (ax, ay), _ = FACES[face]
    return x * ax + y * ay


def visible(face, s):
    _, (fx, fy) = FACES[face]
    nx, ny = O.normal2(s)
    return nx * fx + ny * fy > 0.02


def facing(face, s):
    """|tangent . u-axis|: how wide a part of the outline appears in this elevation."""
    (ax, ay), _ = FACES[face]
    tx, ty = O.tangent2(s)
    return abs(tx * ax + ty * ay)


def opening_on(face):
    """Openings visible on a face, as (name, u0, u1, z0, z1)."""
    out = []
    for name, s0, s1, z0, z1 in L.openings():
        if L.face_of((s0 + s1) / 2) == face:
            us = sorted((project(face, *O.at(s0)), project(face, *O.at(s1))))
            out.append((name, us[0], us[1], z0, z1))
    return out


def slat_lengths():
    """{length_mm: count} over all slat pieces."""
    counts = {}
    for _, _, segs in L.slats()[0]:
        for z0, z1 in segs:
            k = round((z1 - z0) * 1000)
            counts[k] = counts.get(k, 0) + 1
    return dict(sorted(counts.items(), reverse=True))
