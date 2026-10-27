"""PBR materials for Cycles. Colours come from config.PALETTE (design tokens)."""
import bpy

from . import config as C

TEX = C.ASSETS / "tex"
_cache = {}


def srgb(hex_):
    """'#rrggbb' -> linear RGBA (Blender colour sockets are scene-linear)."""
    h = hex_.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def tok(name):
    return srgb(C.PALETTE[name])


def _new(name):
    mat = bpy.data.materials.new(name)
    if hasattr(mat, "use_nodes"):
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    return mat, nt, bsdf


def _image(nt, file, colorspace="sRGB"):
    node = nt.nodes.new("ShaderNodeTexImage")
    img = bpy.data.images.load(str(TEX / file), check_existing=True)
    img.colorspace_settings.name = colorspace
    node.image = img
    return node


def principled(name, color, rough=0.5, metal=0.0, coat=0.0, spec=0.5, emission=None):
    if name in _cache:
        return _cache[name]
    mat, nt, b = _new(name)
    b.inputs["Base Color"].default_value = color if isinstance(color, tuple) else tok(color)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Specular IOR Level"].default_value = spec
    if emission:
        b.inputs["Emission Color"].default_value = tok(emission) if isinstance(emission, str) else emission
        b.inputs["Emission Strength"].default_value = 0.0
    mat.diffuse_color = b.inputs["Base Color"].default_value
    _cache[name] = mat
    return mat


def textured(name, tex, size_m, hue=0.5, sat=1.0, val=1.0, rough_mult=1.0, rough_add=0.0,
             normal=0.6, random_offset=True, rotate=0.0, tint=None, tint_mix=0.0, coat=0.0):
    """Image-based PBR (diffuse/rough/normal) on the mesh UVs, which are in metres.

    size_m: real-world size one texture tile covers. random_offset shifts the
    texture per object so repeated pieces (slats, panels) don't look cloned.
    """
    if name in _cache:
        return _cache[name]
    mat, nt, b = _new(name)
    nodes, links = nt.nodes, nt.links

    uv = nodes.new("ShaderNodeTexCoord")
    mapping = nodes.new("ShaderNodeMapping")
    mapping.inputs["Scale"].default_value = (1 / size_m, 1 / size_m, 1)
    mapping.inputs["Rotation"].default_value = (0, 0, rotate)
    vec = uv.outputs["UV"]
    if random_offset:
        info = nodes.new("ShaderNodeObjectInfo")
        mul = nodes.new("ShaderNodeVectorMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = (7.31, 3.17, 0)
        comb = nodes.new("ShaderNodeCombineXYZ")
        links.new(info.outputs["Random"], comb.inputs[0])
        links.new(info.outputs["Random"], comb.inputs[1])
        links.new(comb.outputs[0], mul.inputs[0])
        add = nodes.new("ShaderNodeVectorMath")
        add.operation = "ADD"
        links.new(vec, add.inputs[0])
        links.new(mul.outputs[0], add.inputs[1])
        vec = add.outputs[0]
    links.new(vec, mapping.inputs["Vector"])

    diff = _image(nt, f"{tex}_diff.jpg")
    rough = _image(nt, f"{tex}_rough.jpg", "Non-Color")
    nor = _image(nt, f"{tex}_nor.jpg", "Non-Color")
    for n in (diff, rough, nor):
        links.new(mapping.outputs[0], n.inputs["Vector"])

    hsv = nodes.new("ShaderNodeHueSaturation")
    hsv.inputs["Hue"].default_value = hue
    hsv.inputs["Saturation"].default_value = sat
    hsv.inputs["Value"].default_value = val
    links.new(diff.outputs["Color"], hsv.inputs["Color"])
    col = hsv.outputs["Color"]
    if tint is not None:
        mix = nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs["Factor"].default_value = tint_mix
        links.new(col, mix.inputs[6])
        mix.inputs[7].default_value = tok(tint)
        col = mix.outputs[2]
    links.new(col, b.inputs["Base Color"])

    rm = nodes.new("ShaderNodeMath")
    rm.operation = "MULTIPLY_ADD"
    rm.inputs[1].default_value = rough_mult
    rm.inputs[2].default_value = rough_add
    rm.use_clamp = True
    links.new(rough.outputs["Color"], rm.inputs[0])
    links.new(rm.outputs[0], b.inputs["Roughness"])

    nmap = nodes.new("ShaderNodeNormalMap")
    nmap.inputs["Strength"].default_value = normal
    links.new(nor.outputs["Color"], nmap.inputs["Color"])
    links.new(nmap.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Coat Weight"].default_value = coat
    mat.diffuse_color = tok(tint) if tint else (0.5, 0.5, 0.5, 1)
    _cache[name] = mat
    return mat


def noisy(name, color, rough=0.4, metal=0.0, rough_var=0.15, bump=0.05, scale=40.0, coat=0.0):
    """Flat colour with procedural roughness break-up (painted steel, plastics)."""
    if name in _cache:
        return _cache[name]
    mat, nt, b = _new(name)
    nodes, links = nt.nodes, nt.links
    b.inputs["Base Color"].default_value = color if isinstance(color, tuple) else tok(color)
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 8
    ramp = nodes.new("ShaderNodeMapRange")
    ramp.inputs["To Min"].default_value = rough - rough_var
    ramp.inputs["To Max"].default_value = rough + rough_var
    links.new(noise.outputs["Fac"], ramp.inputs["Value"])
    links.new(ramp.outputs["Result"], b.inputs["Roughness"])
    if bump:
        bn = nodes.new("ShaderNodeBump")
        bn.inputs["Strength"].default_value = bump
        bn.inputs["Distance"].default_value = 0.001
        links.new(noise.outputs["Fac"], bn.inputs["Height"])
        links.new(bn.outputs["Normal"], b.inputs["Normal"])
    mat.diffuse_color = b.inputs["Base Color"].default_value
    _cache[name] = mat
    return mat


def glass(name="glass", tint=(0.92, 0.96, 0.95, 1.0), rough=0.0):
    if name in _cache:
        return _cache[name]
    mat, nt, b = _new(name)
    b.inputs["Base Color"].default_value = tint
    b.inputs["Roughness"].default_value = rough
    b.inputs["Transmission Weight"].default_value = 1.0
    b.inputs["IOR"].default_value = 1.52
    mat.diffuse_color = (0.6, 0.7, 0.7, 0.3)
    _cache[name] = mat
    return mat


def emissive_image(name, path, strength=0.0):
    """A screen: glossy black glass over an emissive image (strength animated)."""
    if name in _cache:
        return _cache[name]
    mat, nt, b = _new(name)
    nodes, links = nt.nodes, nt.links
    img = nodes.new("ShaderNodeTexImage")
    img.image = bpy.data.images.load(str(path), check_existing=True)
    links.new(img.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Base Color"].default_value = (0.004, 0.004, 0.004, 1)
    b.inputs["Roughness"].default_value = 0.08
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Emission Strength"].default_value = strength
    mat.diffuse_color = (0.02, 0.02, 0.02, 1)
    _cache[name] = mat
    return mat


def emission_socket(mat):
    return mat.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]


def key_emission(mat, frame, value, interp="BEZIER"):
    sock = emission_socket(mat)
    sock.default_value = value
    sock.keyframe_insert("default_value", frame=frame)


def library():
    """Every shared material, created once. Access as M['walnut'] etc."""
    return {
        "walnut": textured("walnut slat", "wood", 1.2, hue=0.53, sat=0.80, val=1.25,
                           rough_mult=0.7, rough_add=0.18, normal=0.5),
        "oak": textured("oak", "oak", 1.0, hue=0.5, sat=0.9, val=1.0, rough_mult=0.8,
                        rough_add=0.1, normal=0.3, coat=0.15),
        "floor": textured("floor laminate", "floor", 1.6, hue=0.5, sat=0.6, val=0.85,
                          normal=0.3, random_offset=False),
        "concrete": textured("concrete", "concrete", 2.5, sat=0.4, val=1.15, normal=0.4,
                             random_offset=False),
        "paving": textured("paving", "paving", 2.0, sat=0.5, val=1.05, normal=0.6,
                           random_offset=False),
        "anthracite": noisy("panel anthracite", "panel-anthracite", rough=0.42, metal=0.2,
                            rough_var=0.08, bump=0.02),
        "panel-white": noisy("panel white", "panel-white", rough=0.38, rough_var=0.05, bump=0.01),
        "panel-core": principled("panel PIR core", (0.85, 0.72, 0.36, 1), rough=0.9),
        "steel-frame": noisy("galvanised steel", (0.55, 0.57, 0.58, 1), rough=0.45, metal=1.0,
                             rough_var=0.15, bump=0.03, scale=12),
        "batten": principled("batten black", "alucobond-black", rough=0.7),
        "alucobond": noisy("alucobond black", "alucobond-black", rough=0.28, metal=0.55,
                           rough_var=0.04, bump=0.0, coat=0.25),
        "alucobond-edge": principled("alucobond joint", (0.01, 0.01, 0.01, 1), rough=0.6),
        "cream": principled("sign cream", "cream", rough=0.35, emission="cream"),
        "led": principled("led strip", (0.9, 0.9, 0.9, 1), rough=0.3, emission="led-warm"),
        "glass": glass(),
        "frosted": glass("frosted glass", rough=0.25),
        "steel": noisy("stainless", "steel", rough=0.22, metal=1.0, rough_var=0.06, bump=0.0),
        "chrome": principled("chrome", (0.9, 0.9, 0.9, 1), rough=0.06, metal=1.0),
        "black-plastic": noisy("black plastic", (0.015, 0.015, 0.015, 1), rough=0.45,
                               rough_var=0.1, bump=0.01, scale=200),
        "rubber": principled("rubber", (0.01, 0.01, 0.01, 1), rough=0.85),
        "white-appliance": noisy("white appliance", (0.82, 0.82, 0.8, 1), rough=0.3,
                                 rough_var=0.05, bump=0.0, coat=0.3),
        "ceramic": principled("ceramic", (0.86, 0.85, 0.82, 1), rough=0.12, coat=0.6),
        "red": principled("extinguisher red", (0.45, 0.02, 0.02, 1), rough=0.3, coat=0.5),
        "cabinet": noisy("cabinet front", (0.78, 0.76, 0.72, 1), rough=0.35, rough_var=0.05,
                         bump=0.0),
        "coffee": principled("coffee beans", (0.05, 0.02, 0.01, 1), rough=0.4),
        "paper": principled("paper cup", "cream", rough=0.6),
        "kraft": principled("kraft", (0.42, 0.27, 0.15, 1), rough=0.8),
        "bread": principled("toast bread", (0.6, 0.38, 0.16, 1), rough=0.75),
        "umbrella": principled("umbrella canvas", (0.80, 0.78, 0.73, 1), rough=0.85),
        "lamp-shade": principled("pendant shade", "alucobond-black", rough=0.4, metal=0.6),
        "bulb": principled("bulb", (1, 1, 1, 1), rough=0.2, emission="led-warm"),
    }
