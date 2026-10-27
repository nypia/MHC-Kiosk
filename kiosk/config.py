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
ROOF_Z = 2.86             # top of roof panel

# Openings (relative to BASE_Z). Front face is y = -B, x measured along it.
WIN_X = (-1.20, 2.00)     # front glazing bay
WIN_SILL = 1.08          # flush with the 0.90 m worktop (+ floor)
WIN_HEAD = 2.20
SCREEN_X = (-0.25, 1.05)  # middle bay: 55" menu screen behind the glass
DOOR_Y = (-0.45, 0.45)    # door on +X side
DOOR_HEAD = 2.10

COUNTER_H = 0.90          # worktop height above finished floor


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
