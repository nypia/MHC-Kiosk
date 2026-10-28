"""Single source of truth: dimensions, palette, build timeline.

Units are metres. The kiosk is centred on the origin, long axis on X.
Front (service windows) faces -Y, door on the +X short side.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "out"

# ---------------------------------------------------------------- footprint
LENGTH = 5.0          # X, outside of slats
WIDTH = 3.0           # Y
HEIGHT = 3.0          # Z, top of fascia
CORNER_R = 0.45       # plan corner radius (outer)
A = LENGTH / 2
B = WIDTH / 2

# Wall build-up, measured inward from the outer footprint (d = depth).
SLAT_D = (0.0, 0.028)        # 28 mm deep walnut slats
BATTEN_D = (0.028, 0.050)    # black battens behind the slats
PANEL_D = (0.050, 0.110)     # 60 mm sandwich panel
FRAME_D = (0.110, 0.170)     # 60x60 steel box section
INNER = PANEL_D[1]           # interior face of the walls

SLAT_W = 0.040
SLAT_PITCH = 0.080

# Heights
PAD_H = 0.12          # concrete pad above plaza (absolute)
BASE_Z = PAD_H        # underside of kiosk chassis (absolute)
# Everything below is relative to BASE_Z; convert with z().
FLOOR_H = 0.16            # finished interior floor
SKIRT_H = 0.14            # black plinth band
FASCIA_Z = (2.40, HEIGHT) # Alucobond crown band
ROOF_Z = 2.96             # top of roof panel (1.5 % fall to the rear-right outlet, drawn flat)
FRAME_BASE_H = 0.12       # top of the 120x120 base frame: posts and wall panels start here
PANEL_TOP = 2.90          # top of wall panels = top of the ring beam
RING_Z = (2.84, 2.90)     # 60x60 top ring beam (raised to give the service plenum ~0.28 m)
CEILING_Z = 2.50          # underside of the suspended service deck (clear height 2.34 m)
DECK_T = 0.064            # deck build-up: 6 mm white board + 40x40 steel grid + 18 mm plywood
AC_INDOOR = (0.90, 0.45, 0.20)  # slim ducted indoor unit envelope (W x D x H)

# Openings (relative to BASE_Z). Front face is y = -B, x measured along it.
WIN_X = (-1.20, 2.00)     # front glazing bay
WIN_SILL = 1.08          # flush with the 0.90 m worktop (+ floor)
WIN_HEAD = 2.20
SCREEN_X = (-0.25, 1.05)  # middle bay: 55" menu screen behind the glass
DOOR_Y = (-0.45, 0.45)    # door on +X side
DOOR_HEAD = 2.20          # clear door height 2.04 m above the finished floor

COUNTER_H = 0.90          # worktop height above finished floor

# Suggested steel and cladding sections (drawings + model). To be confirmed by
# a structural engineer before fabrication.
PROFILES = {
    "taban çerçeve": "120×120×4 kutu profil, köşeler hadde bükümlü",
    "taban kiriş": "100×50×3 kutu profil",
    "dikme": "60×60×3 kutu profil",
    "üst çerçeve": "60×60×3 kutu profil, köşeler hadde bükümlü",
    "lento / denizlik": "60×100×3 kutu profil",
    "köşe kaburga": "40×20×2 kutu profil, R≈330 hadde bükümlü",
    "çatı aşığı": "60×40×2 kutu profil",
    "asma kat taşıyıcı": "40×40×2 kutu profil",
    "asma kat askı": "M10 dişli çubuk + 40×40×4 L köşebent",
    "karkas": "siyah eloksal alüminyum omega 45×22",
}


def z(h):
    """Height above BASE_Z -> absolute world z."""
    return BASE_Z + h


# ---------------------------------------------------------------- palette
# Mirrors the "MHC Kahve" design system tokens (sRGB hex).
PALETTE = {
    "alucobond-black": "#1f1d1c",
    "walnut": "#8a5a3a",
    "walnut-deep": "#4e3020",
    "oak-counter": "#c08a5c",
    "cream": "#efe2c4",
    "concrete": "#c9c4bc",
    "steel": "#9aa0a4",
    "led-warm": "#ffd9a0",
    "screen-ink": "#121212",
    "panel-anthracite": "#383e42",   # RAL 7016 sandwich panel skin
    "panel-white": "#ecebe6",        # RAL 9010 interior skin
}

# ---------------------------------------------------------------- timeline
FPS = 24
DURATION = 45.0
FRAMES = int(FPS * DURATION)

# (start_s, end_s) per build phase
PHASES = {
    "site":      (0.0, 3.0),
    "chassis":   (3.0, 8.0),
    "panels":    (8.0, 14.0),
    "openings":  (14.0, 17.0),
    "slats":     (17.0, 23.0),
    "fascia":    (23.0, 27.0),
    "glazing":   (27.0, 31.0),
    "roof_off":  (31.0, 33.0),
    "interior":  (33.0, 37.0),
    "equipment": (36.5, 40.0),
    "finale":    (40.0, 45.0),
}


def f(seconds):
    """Seconds -> frame number (1-based, Blender convention)."""
    return 1 + round(seconds * FPS)


def phase(name):
    s0, s1 = PHASES[name]
    return f(s0), f(s1)
