"""Blender geometry + animation helpers shared by every module.

Outline math (arc length s, depth d) lives in outline.py.
"""
import math

import bmesh
import bpy
from mathutils import Matrix, Vector

from . import config as C

from .outline import (BREAKS, CQ, HX, HY, TOTAL, R, _SEGS, at, normal2, perim,  # noqa: F401
                      s_back, s_front, s_left, s_right, samples, tangent2)


def normal(s):
    return Vector((*normal2(s), 0.0))


def tangent(s):
    return Vector((*tangent2(s), 0.0))


# ------------------------------------------------------------ collections
def collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def link(obj, coll):
    coll.objects.link(obj)
    return obj


def new_object(name, mesh, coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = rot
    coll.objects.link(obj)
    return obj


def set_materials(mesh, mats):
    for m in mats:
        mesh.materials.append(m)


def smooth(mesh, angle=35):
    mesh.shade_smooth()
    mesh.set_sharp_from_angle(angle=math.radians(angle))


# ------------------------------------------------------------ mesh builders
def band(name, s0, s1, d0, d1, z0, z1, mats, coll, step=0.03):
    """A wall band along the outline: depth d0..d1, height z0..z1 (absolute).

    Faces get material index 0 outside, 1 inside, 2 on the cut edges.
    The object origin sits at the band's middle, on its outer face.
    Returns (object, outward normal at the middle).
    """
    closed = abs((s1 - s0) - TOTAL) < 1e-6
    ss = samples(s0, s1, step)
    if closed:
        ss = ss[:-1]
    sm = (s0 + s1) / 2
    ox, oy = at(sm, d0)
    origin = Vector((ox, oy, (z0 + z1) / 2))

    bm = bmesh.new()
    uv = bm.loops.layers.uv.new("UVMap")
    rings = []
    for s in ss:
        (xo, yo), (xi, yi) = at(s, d0), at(s, d1)
        ring = [
            bm.verts.new(Vector((xo, yo, z0)) - origin),
            bm.verts.new(Vector((xo, yo, z1)) - origin),
            bm.verts.new(Vector((xi, yi, z1)) - origin),
            bm.verts.new(Vector((xi, yi, z0)) - origin),
        ]
        rings.append((s, ring))
    n = len(rings)
    pairs = [(i, i + 1) for i in range(n - 1)]
    if closed:
        pairs.append((n - 1, 0))
    for i, j in pairs:
        (sa, a), (sb, b) = rings[i], rings[j]
        if j == 0:
            sb = s0 + TOTAL  # keep UVs continuous over the seam
        for k, mat in ((0, 0), (1, 2), (2, 1), (3, 2)):
            k2 = (k + 1) % 4
            f = bm.faces.new((a[k], b[k], b[k2], a[k2]))
            f.material_index = mat
            for loop in f.loops:
                v = loop.vert
                s_ = sa if v in a else sb
                loop[uv].uv = (s_, v.co.z + origin.z)
    if not closed:
        for f in (bm.faces.new(rings[0][1]), bm.faces.new(rings[-1][1][::-1])):
            f.material_index = 2
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    set_materials(me, mats)
    obj = new_object(name, me, coll, loc=origin)
    return obj, normal(sm)


def slab(name, d, z0, z1, mats, coll, step=0.03):
    """Solid rounded-rectangle plate inset by d (floor, roof, chassis deck)."""
    pts = [at(s, d) for s in samples(0, TOTAL, step)[:-1]]
    bm = bmesh.new()
    bot = [bm.verts.new((x, y, z0)) for x, y in pts]
    face = bm.faces.new(bot)
    ext = bmesh.ops.extrude_face_region(bm, geom=[face])
    top = [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=top, vec=(0, 0, z1 - z0))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        side = abs(f.normal.z) < 0.5
        for loop in f.loops:
            co = loop.vert.co
            loop[uv].uv = (co.x + co.y, co.z) if side else (co.x, co.y)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    set_materials(me, mats)
    return new_object(name, me, coll)


_box_cache = {}


def box_mesh(sx, sy, sz, mats, bevel=0.0, origin="center"):
    """Box mesh (cached by size+material) with metre-scaled UVs.

    UV u runs along the box's longest axis so wood grain follows the piece.
    origin: 'center' or 'bottom' (for things that grow upward).
    """
    key = (round(sx, 4), round(sy, 4), round(sz, 4), tuple(m.name for m in mats), bevel, origin)
    if key in _box_cache:
        return _box_cache[key]
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    if origin == "bottom":
        bmesh.ops.translate(bm, vec=(0, 0, sz / 2), verts=bm.verts)
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=2,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    dims = (sx, sy, sz)
    longest = max(range(3), key=lambda i: dims[i])
    uv = bm.loops.layers.uv.new("UVMap")
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i]))
        inplane = [i for i in range(3) if i != ax]
        u_ax = longest if longest in inplane else inplane[0]
        v_ax = inplane[1] if u_ax == inplane[0] else inplane[0]
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co[u_ax], loop.vert.co[v_ax])
    me = bpy.data.meshes.new("box")
    bm.to_mesh(me)
    bm.free()
    set_materials(me, mats)
    _box_cache[key] = me
    return me


def box(name, size, loc, coll, mats, rot=(0, 0, 0), bevel=0.0, origin="center"):
    return new_object(name, box_mesh(*size, mats, bevel, origin), coll, loc, rot)


def cylinder(name, r, h, loc, coll, mats, verts=32, rot=(0, 0, 0), origin="bottom", r2=None, caps=True):
    """Cylinder / cone frustum standing on its base (origin='bottom')."""
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    if origin == "bottom":
        bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    set_materials(me, mats)
    smooth(me, 40)
    return new_object(name, me, coll, loc, rot)


def rounded_box(name, size, radius, loc, coll, mats, rot=(0, 0, 0), segments=4):
    """Box with soft rounded edges (appliances, screens)."""
    obj = box(name, size, loc, coll, mats, rot)
    obj.data = obj.data.copy()
    mod = obj.modifiers.new("bevel", "BEVEL")
    mod.width = radius
    mod.segments = segments
    mod.limit_method = "ANGLE"
    obj.data.shade_smooth()
    obj.modifiers.new("smooth", "WEIGHTED_NORMAL").keep_sharp = True
    return obj


# ------------------------------------------------------------ animation
def _fcurves(obj_or_data):
    ad = obj_or_data.animation_data
    act = ad.action
    if hasattr(act, "fcurves"):          # Blender < 5.0
        return act.fcurves
    from bpy_extras import anim_utils     # Blender 4.4+ layered actions
    return anim_utils.action_get_channelbag_for_slot(act, ad.action_slot).fcurves


def key(target, path, frame, value=None, interp=None, easing=None):
    """Insert a keyframe; interp/easing apply to the segment that STARTS here."""
    if value is not None:
        setattr(target, path, value)
    target.keyframe_insert(path, frame=frame)
    if interp or easing:
        for fc in _fcurves(target):
            if fc.data_path != path:
                continue
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.5:
                    if interp:
                        kp.interpolation = interp
                    if easing:
                        kp.easing = easing


def show_from(obj, frame):
    """Invisible before `frame`, visible from it on."""
    for attr in ("hide_render", "hide_viewport"):
        key(obj, attr, max(frame - 1, 0), True)
        key(obj, attr, frame, False)


def hide_from(obj, frame):
    for attr in ("hide_render", "hide_viewport"):
        key(obj, attr, frame - 1, False)
        key(obj, attr, frame, True)


def arrive(obj, f0, f1, offset=(0, 0, 0), rot_offset=None, interp="BACK", easing="EASE_OUT",
           visible=True):
    """Move obj into its current (final) transform from final+offset over f0..f1."""
    final_loc = obj.location.copy()
    final_rot = obj.rotation_euler.copy()
    key(obj, "location", f0, final_loc + Vector(offset), interp, easing)
    key(obj, "location", f1, final_loc)
    if rot_offset is not None:
        start = final_rot.copy()
        for i in range(3):
            start[i] += rot_offset[i]
        key(obj, "rotation_euler", f0, start, interp, easing)
        key(obj, "rotation_euler", f1, final_rot)
    if visible:
        show_from(obj, f0)


def grow(obj, f0, f1, axis=2, interp="EXPO", easing="EASE_OUT"):
    """Scale one axis from ~0 to 1 (object origin must be at its base)."""
    s = obj.scale.copy()
    s0 = s.copy()
    s0[axis] = 0.001
    key(obj, "scale", f0, s0, interp, easing)
    key(obj, "scale", f1, s)
    show_from(obj, f0)


def stagger(items, f0, f1, dur):
    """Spread item start frames across f0..f1-dur; yields (item, start, end)."""
    n = max(len(items) - 1, 1)
    span = max(f1 - dur - f0, 0)
    for i, it in enumerate(items):
        st = f0 + round(span * i / n)
        yield it, st, st + dur


def look_at(obj, target):
    d = Vector(target) - obj.location
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def matrix_on_outline(s, d, z):
    """World matrix of a frame on the outline: X=tangent, Y=inward, Z=up."""
    x, y = at(s, d)
    t, n = tangent(s), -normal(s)
    return Matrix((
        (t.x, n.x, 0, x),
        (t.y, n.y, 0, y),
        (0, 0, 1, z),
        (0, 0, 0, 1),
    ))


def show_tree(obj, frame):
    """show_from() for an object and all its children (visibility isn't inherited)."""
    show_from(obj, frame)
    for child in obj.children_recursive:
        show_from(child, frame)


def hide_tree(obj, frame):
    hide_from(obj, frame)
    for child in obj.children_recursive:
        hide_from(child, frame)


def empty(name, coll, loc=(0, 0, 0), rot=(0, 0, 0)):
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_size = 0.2
    obj.location = loc
    obj.rotation_euler = rot
    coll.objects.link(obj)
    return obj


def parent(child, par):
    """Parent keeping the child's transform expressed in the parent's local space."""
    child.parent = par
    return child


def quad(name, w, h, coll, mats, loc=(0, 0, 0), rot=(0, 0, 0)):
    """w x h plane in XZ facing -Y with 0..1 UVs (screens, printed graphics)."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([(-w / 2, 0, -h / 2), (w / 2, 0, -h / 2), (w / 2, 0, h / 2), (-w / 2, 0, h / 2)],
                   [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name="UVMap")
    for loop, co in zip(me.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop.index].uv = co
    set_materials(me, mats)
    return new_object(name, me, coll, loc, rot)


def text(name, body, font_file, size, coll, mat, loc=(0, 0, 0), rot=(0, 0, 0), extrude=0.002,
         spacing=1.0, align="CENTER"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.font = bpy.data.fonts.load(str(C.ASSETS / "fonts" / font_file), check_existing=True)
    cu.size = size
    cu.extrude = extrude
    cu.bevel_depth = extrude * 0.25
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.space_character = spacing
    cu.materials.append(mat)
    return new_object(name, cu, coll, loc, rot)
