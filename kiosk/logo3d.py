"""MHC Mola logo as extruded Blender curves, read from kiosk/art/logo/logo_geometry.json.

The JSON is written by brand.py (matplotlib + shapely), so Blender's own Python
needs neither. Logos are built flat in XY (x right, y up) and stood up to face
-Y; the caller rotates the returned root for other faces.
"""
import json
import math

import bpy

from . import config as C
from . import util as U

GEOMETRY = C.ROOT / "kiosk" / "art" / "logo" / "logo_geometry.json"
_data = None


def data():
    global _data
    if _data is None:
        _data = json.loads(GEOMETRY.read_text())
    return _data


def _curve(name, shapes, scale, depth, mat, coll):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "2D"
    cu.fill_mode = "BOTH"
    cu.extrude = depth / 2
    cu.bevel_depth = min(depth * 0.08, 0.002)
    for shape in shapes:
        for ring in [shape["outer"]] + shape["holes"]:
            pts = ring[:-1] if ring[0] == ring[-1] else ring
            sp = cu.splines.new("POLY")
            sp.points.add(len(pts) - 1)
            for p, (x, y) in zip(sp.points, pts):
                p.co = (x * scale, y * scale, 0.0, 1.0)
            sp.use_cyclic_u = True
    cu.materials.append(mat)
    return U.new_object(name, cu, coll)


def logo(name, which, size, depth, mats, coll, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0)):
    """which: 'wordmark' (size = height) or 'badge' (size = disk diameter, disk not included).

    mats: {"fg": material, "accent": material}. Returns the root empty.
    """
    root = U.empty(name, coll, loc, rot)
    by_key = {}
    for part in data()[which]["parts"]:
        by_key.setdefault(part["key"], []).extend(part["shapes"])
    for key, shapes in by_key.items():
        U.parent(_curve(f"{name} {key}", shapes, size, depth, mats[key], coll), root)
    return root


def width(which, size):
    return data()[which].get("aspect", 1.0) * size
