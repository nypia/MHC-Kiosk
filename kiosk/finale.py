"""Roof lift for the interior fit-out, roof return, lights on, dusk, hatch opens."""
from mathutils import Vector

from . import config as C
from . import materials as Mt
from . import util as U

F = C.f


def _key_value(owner, attr, frames_values):
    for fr, v in frames_values:
        setattr(owner, attr, v)
        owner.keyframe_insert(attr, frame=fr)


def animate(M, roof, hatch, world_bg, sun, lights):
    r0, r1 = C.phase("roof_off")
    f0, f1 = C.phase("finale")
    home = roof.location.copy()
    away = home + Vector((7.5, 2.0, 6.0))

    # Crane the roof module (with ceiling, pendants and condenser) off ...
    U.key(roof, "location", r0, home, "SINE", "EASE_IN_OUT")
    U.key(roof, "location", r0 + 14, home + Vector((0, 0, 1.4)), "SINE", "EASE_IN_OUT")
    U.key(roof, "location", r1, away)
    U.hide_tree(roof, r1)
    # ... and back on once the fit-out is done.
    U.key(roof, "location", f0, away, "BACK", "EASE_OUT")
    U.key(roof, "location", f0 + 36, home)
    U.show_tree(roof, f0)

    on0, on1 = f0 + 38, f0 + 60
    for data, energy in lights["area"] + lights["point"]:
        _key_value(data, "energy", ((on0, 0.0), (on1, energy)))
    for mat, strength in zip(lights["emit"], (30.0, 6.0, 8.0)):
        Mt.key_emission(mat, on0, 0.0)
        Mt.key_emission(mat, on1, strength)
    Mt.key_emission(M["cream"], on0, 0.6)
    Mt.key_emission(M["cream"], on1, 2.0)
    Mt.key_emission(M["led"], on0, 18.0)
    Mt.key_emission(M["led"], on1, 30.0)

    # Late-afternoon dim so the interior glow reads.
    _key_value(sun, "energy", ((f0 + 20, sun.energy), (f1 - 12, 1.3)))
    strength = world_bg.inputs["Strength"]
    for fr, v in ((f0 + 20, 1.0), (f1 - 12, 0.5)):
        strength.default_value = v
        strength.keyframe_insert("default_value", frame=fr)

    # Pick-up hatch slides open.
    h = hatch.location.copy()
    U.key(hatch, "location", f0 + 66, h, "SINE", "EASE_IN_OUT")
    U.key(hatch, "location", f0 + 90, h + Vector((0, 0, 0.50)))
