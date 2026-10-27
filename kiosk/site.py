"""Plaza, concrete pad, HDRI world + sun, terrace furniture."""
import math

import bpy
from mathutils import Vector

from . import config as C
from . import materials as Mt
from . import util as U

Z = C.z

HDRI = C.ASSETS / "hdri" / "buikslotermeerplein.hdr"
# Brightest region of the HDRI sits at azimuth -22.4 deg, elevation 22.6 deg.
# Rotate the world so it lights the front (-Y) face from the front-right.
HDRI_SUN_AZ = -22.4
SUN_AZ = -62.0
SUN_EL = 26.0
WORLD_ROT = math.radians(HDRI_SUN_AZ - SUN_AZ)


def build_world():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    if hasattr(world, "use_nodes"):
        world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.inputs["Rotation"].default_value = (0, 0, WORLD_ROT)
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(str(HDRI), check_existing=True)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 1.0
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], env.inputs["Vector"])
    nt.links.new(env.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])

    sun_data = bpy.data.lights.new("güneş", "SUN")
    sun_data.energy = 3.2
    sun_data.angle = math.radians(1.2)
    sun_data.color = (1.0, 0.94, 0.86)
    sun = bpy.data.objects.new("güneş", sun_data)
    bpy.context.scene.collection.objects.link(sun)
    az, el = math.radians(SUN_AZ), math.radians(SUN_EL)
    d = Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el)))
    sun.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    return bg, sun_data


def build_ground(M):
    col = U.collection("01 Saha")
    f0, f1 = C.phase("site")
    size = 160.0
    me = bpy.data.meshes.new("meydan")
    h = size / 2
    me.from_pydata([(-h, -h, 0), (h, -h, 0), (h, h, 0), (-h, h, 0)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for loop in me.loops:
        co = me.vertices[loop.vertex_index].co
        uv.data[loop.index].uv = (co.x, co.y)
    me.materials.append(M["paving"])
    U.new_object("meydan zemini", me, col)

    pad = U.slab("beton platform", -0.45, 0.0, C.PAD_H, [M["concrete"]], col)
    U.grow(pad, f0 + 12, f1 - 6, interp="EXPO")


def _umbrella_set(M, col, name, loc):
    """Round table, three chairs and a market umbrella; returns its root empty."""
    root = U.empty(name, col, loc)
    black, oak = [M["black-plastic"]], [M["oak"]]
    parts = [
        U.cylinder(f"{name} masa tabla", 0.36, 0.03, (0, 0, 0.72), col, oak, verts=48),
        U.cylinder(f"{name} masa ayak", 0.03, 0.72, (0, 0, 0), col, black, verts=16),
        U.cylinder(f"{name} masa taban", 0.24, 0.02, (0, 0, 0), col, black, verts=32),
        U.cylinder(f"{name} şemsiye direk", 0.02, 2.45, (0, 0, 0.75), col, [M["oak"]], verts=12),
        U.cylinder(f"{name} şemsiye", 1.35, 0.42, (0, 0, 2.62), col, [M["umbrella"]], verts=8, r2=0.04),
        U.cylinder(f"{name} şemsiye tepe", 0.05, 0.08, (0, 0, 3.03), col, [M["umbrella"]], verts=8),
    ]
    for k in range(3):
        a = math.radians(90 + k * 120)
        cx, cy = 0.62 * math.cos(a), 0.62 * math.sin(a)
        rz = a + math.pi / 2
        chair = U.empty(f"{name} sandalye {k}", col, (cx, cy, 0), (0, 0, rz))
        bits = [U.box(f"{name} sandalye {k} oturak", (0.42, 0.42, 0.03), (0, 0, 0.45), col, oak, bevel=0.004),
                U.box(f"{name} sandalye {k} sırt", (0.42, 0.025, 0.36), (0, 0.2, 0.68), col, oak, bevel=0.004)]
        for i, (lx, ly) in enumerate(((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18))):
            bits.append(U.box(f"{name} sandalye {k} ayak {i}", (0.025, 0.025, 0.44), (lx, ly, 0), col, black,
                              origin="bottom"))
        for b in bits:
            U.parent(b, chair)
        parts.append(chair)
    for p in parts:
        U.parent(p, root)
    return root


def build_terrace(M):
    col = U.collection("09 Teras")
    f0, f1 = C.phase("finale")
    sets = [_umbrella_set(M, col, f"teras {i}", loc) for i, loc in
            enumerate(((4.4, -3.2, 0), (6.9, -1.0, 0), (4.6, -6.0, 0), (7.4, -4.4, 0)))]
    for root, st, en in U.stagger(sets, f0 + 6, f0 + 54, 18):
        U.arrive(root, st, en, offset=(0, 0, 3.0), interp="BACK", visible=False)
        U.show_tree(root, st)
