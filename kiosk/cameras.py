"""Animated build camera + the four hero stills (C01-C04)."""
import math

import bpy

from . import config as C
from . import util as U

F = C.f

# time (s): camera position, look-at target, focal length (mm)
PATH = [
    (0.0, (-10.5, -12.5, 5.2), (0.0, 0.0, 0.6), 30),
    (3.0, (-8.5, -10.0, 4.2), (0.0, 0.0, 0.8), 30),
    (8.0, (-6.5, -9.0, 3.4), (0.2, 0.0, 1.3), 30),
    (14.0, (-1.5, -8.6, 2.4), (0.4, -0.5, 1.5), 32),
    (17.0, (-6.2, -6.4, 1.7), (-0.6, -0.4, 1.4), 30),
    (23.0, (-5.0, -4.4, 1.25), (-0.8, -0.3, 2.3), 26),
    (27.0, (0.4, -6.0, 1.7), (0.45, -1.5, 1.75), 30),
    (31.0, (0.4, -5.2, 1.8), (0.4, -1.4, 1.7), 32),
    (33.0, (2.5, -6.5, 8.5), (0.2, 0.0, 0.8), 28),
    (37.0, (-1.5, -5.5, 9.0), (0.0, 0.1, 0.8), 28),
    (40.0, (-2.5, -5.0, 8.0), (0.0, 0.0, 0.9), 28),
    (42.5, (-5.6, -10.0, 2.6), (0.6, -0.3, 1.6), 30),
    (45.0, (-4.6, -8.6, 1.7), (0.6, -0.4, 1.5), 32),
]

# name: (position, target, lens, frame, ortho_scale or None)
STILLS = {
    "C01 Ön cephe": ((-4.6, -8.6, 1.65), (0.6, -0.4, 1.5), 32, C.FRAMES, None),
    "C02 Köşe detayı": ((-3.6, -3.9, 0.9), (-1.0, -1.2, 2.4), 24, C.FRAMES, None),
    "C03 Teras": ((-5.4, -10.2, 6.2), (2.2, -1.8, 0.7), 28, C.FRAMES, None),
    "C04 Üstten, çatı açık": ((0.0, 0.0, 12.0), (0.0, 0.0, 0.0), 50, F(39.8), 6.6),
}


def _camera(name, coll, lens, sensor=36.0):
    data = bpy.data.cameras.new(name)
    data.lens = lens
    data.sensor_width = sensor
    data.clip_start = 0.05
    data.clip_end = 400
    obj = bpy.data.objects.new(name, data)
    coll.objects.link(obj)
    return obj


def build(scene):
    coll = U.collection("10 Kameralar")
    cam = _camera("kamera animasyon", coll, PATH[0][3])
    target = U.empty("kamera hedef", coll)
    con = cam.constraints.new("TRACK_TO")
    con.target = target
    con.track_axis = "TRACK_NEGATIVE_Z"
    con.up_axis = "UP_Y"
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = target
    cam.data.dof.aperture_fstop = 5.6
    for t, loc, tgt, lens in PATH:
        fr = F(t)
        U.key(cam, "location", fr, loc, "BEZIER")
        U.key(target, "location", fr, tgt, "BEZIER")
        cam.data.lens = lens
        cam.data.keyframe_insert("lens", frame=fr)
    scene.camera = cam

    for name, (loc, tgt, lens, frame, ortho) in STILLS.items():
        c = _camera(name, coll, lens)
        c.location = loc
        if ortho:
            c.data.type = "ORTHO"
            c.data.ortho_scale = ortho
            c.rotation_euler = (0, 0, 0)
        else:
            U.look_at(c, tgt)
            c.data.dof.use_dof = True
            c.data.dof.focus_distance = (c.location - c.location.__class__(tgt)).length
            c.data.dof.aperture_fstop = 8.0
        c["still_frame"] = frame
    return cam
