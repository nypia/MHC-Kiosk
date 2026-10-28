"""Build the whole animated kiosk scene and save kiosk.blend.

    blender -b -P build.py                 # with an installed Blender
    python build.py                        # with the `bpy` pip module
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import bpy  # noqa: E402

from kiosk import config as C  # noqa: E402
from kiosk import layout as L  # noqa: E402
from kiosk import cameras, interior, materials, shell, site, finale  # noqa: E402


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.name = "MHC Kiosk"
    sc.render.engine = "CYCLES"
    sc.render.fps = C.FPS
    sc.frame_start = 1
    sc.frame_end = C.FRAMES
    sc.unit_settings.system = "METRIC"
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    cy = sc.cycles
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.max_bounces = 8
    cy.glossy_bounces = 4
    cy.transmission_bounces = 8
    cy.transparent_max_bounces = 8
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.sample_clamp_indirect = 8.0
    return sc


def check(sc):
    """Sanity checks on the finished model."""
    objs = [o for o in sc.objects if o.type == "MESH" and o.name.startswith("alucobond kaset")]
    xs = [v for o in objs for v in (o.matrix_world @ c.co for c in o.data.vertices)]
    ext = (max(v.x for v in xs) - min(v.x for v in xs), max(v.y for v in xs) - min(v.y for v in xs))
    top = max(v.z for v in xs) - C.BASE_Z
    assert abs(ext[0] - (C.LENGTH + 0.036)) < 0.01 and abs(ext[1] - (C.WIDTH + 0.036)) < 0.01, ext
    assert abs(top - C.HEIGHT) < 0.01, top
    clear = C.CEILING_Z - C.FLOOR_H
    door = C.DOOR_HEAD - C.FLOOR_H
    plenum = C.RING_Z[0] - (C.CEILING_Z + C.DECK_T)
    assert clear >= 2.30 and door >= 2.00 and plenum >= C.AC_INDOOR[2] + 0.05, (clear, door, plenum)
    panels = L.panels()
    covered = sum(p["s1"] - p["s0"] + 2 * L.PANEL_GAP for p in panels)
    assert abs(covered - L.O.TOTAL) < 1e-6, covered
    print(f"envelope {ext[0]:.3f} x {ext[1]:.3f} x {top:.3f} m (fascia proud 18 mm), "
          f"clear height {clear:.2f}, door {door:.2f}, plenum {plenum:.3f}, "
          f"{len(panels)} wall modules, {len(sc.objects)} objects")


def main():
    sc = setup_scene()
    M = materials.library()
    bg, sun = site.build_world()
    site.build_ground(M)
    shell.build_chassis(M)
    roof, cutouts = shell.build_panels(M)
    shell.animate_openings(cutouts)
    shell.build_cladding(M)
    shell.build_fascia(M, roof)
    parts = shell.build_glazing(M)
    lights = interior.build(M)
    site.build_terrace(M)
    finale.animate(M, roof=roof, hatch=parts["hatch"], world_bg=bg, sun=sun, lights=lights)
    cameras.build(sc)
    sc.frame_set(C.FRAMES)
    check(sc)
    path = C.ROOT / "kiosk.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(path), relative_remap=True, compress=True)
    print("saved", path)


if __name__ == "__main__":
    main()
