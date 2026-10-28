"""Assembly-step illustrations for the fabrication drawings (sheet 03) and the cover.

    python render_steps.py            # bpy pip module
    blender -b kiosk.blend -P render_steps.py

Writes kiosk/art/steps/NN.png (committed, so the drawings build without Blender).
Interior fit-out and terrace are hidden: the drawings cover the shell only.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import bpy  # noqa: E402
from mathutils import Vector  # noqa: E402

from kiosk import config as C  # noqa: E402

F = C.f
OUT = C.ROOT / "kiosk" / "art" / "steps"
STEPS = [  # (file, frame)
    ("01_sasi", F(8.0) - 1),      # one frame before the first panel appears
    ("02_panel", F(14.0)),
    ("03_bosluk", F(17.0)),
    ("04_cita", F(23.0) - 1),     # before the fascia backing appears
    ("05_alucobond", F(27.0)),
    ("06_cam_kapi", F(31.0)),
    ("08_final", C.FRAMES),
    ("07_asma_kat", F(40.0) + 14),   # last: it removes the roof
]


def main(res=(1200, 800), samples=48):
    if not bpy.data.filepath:
        bpy.ops.wm.open_mainfile(filepath=str(C.ROOT / "kiosk.blend"))
    sc = bpy.context.scene
    for name in ("07 İç mekân", "08 Ekipman", "09 Teras"):
        bpy.data.collections[name].hide_render = True
    cam_data = bpy.data.cameras.new("adım kamera")
    cam_data.lens = 50
    cam = bpy.data.objects.new("adım kamera", cam_data)
    sc.collection.objects.link(cam)
    cam.location = (-7.6, -9.2, 6.4)
    cam.rotation_euler = (Vector((0.4, 0.0, 1.1)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    r = sc.render
    r.resolution_x, r.resolution_y = res
    r.use_motion_blur = False
    sc.cycles.samples = samples
    sc.cycles.use_adaptive_sampling = True
    OUT.mkdir(parents=True, exist_ok=True)
    for name, frame in STEPS:
        sc.frame_set(frame)
        if name == "07_asma_kat":
            roof = bpy.data.objects["çatı paneli"]
            for o in [roof] + list(roof.children_recursive):
                o.animation_data_clear()
                o.hide_render = True
        r.filepath = str(OUT / f"{name}.png")
        bpy.ops.render.render(write_still=True)
        print("step ->", r.filepath, flush=True)


if __name__ == "__main__":
    main()
