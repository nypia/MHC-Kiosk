"""Download the CC0 textures, HDRI and fonts the scene needs into assets/.

Poly Haven (CC0) for HDRI + PBR textures, Google Fonts (OFL) for type.
Standard library only, so it runs with any Python 3.9+ (or Blender's own Python).

    python fetch_assets.py            # 2k textures, 4k HDRI (preview / default)
    python fetch_assets.py --final    # 4k textures, 8k HDRI (final render)
"""
import argparse
import json
import pathlib
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent / "assets"
API = "https://api.polyhaven.com/files/"

HDRI = "buikslotermeerplein"

# local name -> Poly Haven asset id
TEXTURES = {
    "wood": "wood_table_001",      # facade slats, tinted to walnut
    "oak": "oak_veneer_01",        # counters, bar shelves
    "floor": "laminate_floor_02",  # interior floor
    "concrete": "concrete_floor_02",
    "paving": "concrete_pavement",
}
MAPS = {"diff": "Diffuse", "rough": "Rough", "nor": "nor_gl"}

FONTS = {
    "Fraunces-SemiBold.ttf": "https://fonts.gstatic.com/s/fraunces/v38/6NUh8FyLNQOQZAnv9bYEvDiIdE9Ea92uemAk_WBq8U_9v0c2Wa0K7iN7hzFUPJH58njr1K03gg7S2nfgRYIcaRyjDg.ttf",
    "Jost-Regular.ttf": "https://fonts.gstatic.com/s/jost/v20/92zPtBhPNqw79Ij1E865zBUv7myjJQVG.ttf",
    "Jost-Medium.ttf": "https://fonts.gstatic.com/s/jost/v20/92zPtBhPNqw79Ij1E865zBUv7myRJQVG.ttf",
    # logo concepts
    "JosefinSans-SemiBold.ttf": "https://fonts.gstatic.com/s/josefinsans/v34/Qw3PZQNVED7rKGKxtqIqX5E-AVSJrOCfjY46_ObXXME.ttf",
    "CormorantGaramond-SemiBold.ttf": "https://fonts.gstatic.com/s/cormorantgaramond/v21/co3umX5slCNuHLi8bLeY9MK7whWMhyjypVO7abI26QOD_iE9GnM.ttf",
    "Pacifico-Regular.ttf": "https://fonts.gstatic.com/s/pacifico/v23/FwZY7-Qmy14u9lezJ96A.ttf",
    "Montserrat-Medium.ttf": "https://fonts.gstatic.com/s/montserrat/v31/JTUHjIg1_i6t8kCHKm4532VJOt5-QNFgpCtZ6Ew-.ttf",
    "DMSerifDisplay-Regular.ttf": "https://fonts.gstatic.com/s/dmserifdisplay/v17/-nFnOHM81r4j6k0gjAW3mujVU2B2K_c.ttf",
}


UA = {"User-Agent": "mhc-kiosk-fetch/1.0"}


def _open(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA))


def get_json(url):
    with _open(url) as r:
        return json.load(r)


def download(url, dest):
    if dest.exists() and dest.stat().st_size > 0:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print("  ", dest.relative_to(ROOT.parent))
    tmp = dest.with_suffix(dest.suffix + ".part")
    with _open(url) as r, open(tmp, "wb") as f:
        while chunk := r.read(1 << 20):
            f.write(chunk)
    tmp.rename(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true", help="4k textures + 8k HDRI")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]  # blender -P ... -- args
    args = ap.parse_args(argv)
    tex_res, hdri_res = ("4k", "8k") if args.final else ("2k", "4k")

    print("HDRI")
    files = get_json(API + HDRI)
    download(files["hdri"][hdri_res]["hdr"]["url"], ROOT / "hdri" / f"{HDRI}.hdr")

    print("Textures")
    for name, asset in TEXTURES.items():
        files = get_json(API + asset)
        for short, key in MAPS.items():
            download(files[key][tex_res]["jpg"]["url"], ROOT / "tex" / f"{name}_{short}.jpg")

    print("Fonts")
    for fname, url in FONTS.items():
        download(url, ROOT / "fonts" / fname)
    print("done")


if __name__ == "__main__":
    main()
