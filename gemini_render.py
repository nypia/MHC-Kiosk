"""Photoreal renders of the MHC Mola kiosk with a Gemini image model.

The Blender renders in kiosk/art/ are sent as references so the model keeps the
real geometry (rounded corners, slats, black band, centred glazing) and only
lifts the look to photographic. The seal and lockup PNGs go along so the logo
stays the chosen one. Standard library only; reads the key from GEMINI_API_KEY
(or GOOGLE_API_KEY) and never writes it anywhere.

    python gemini_render.py --list                 # image models this key can use
    python gemini_render.py                        # all shots → docs/render/gemini/
    python gemini_render.py --shots aksam --n 2    # one shot, two variations
    python gemini_render.py --model gemini-2.5-flash-image
    python gemini_render.py --print-prompts        # prompts + reference files, no API call
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs" / "render" / "gemini"
API = "https://generativelanguage.googleapis.com/v1beta"
FALLBACK_MODEL = "gemini-2.5-flash-image"

LOGO_REFS = [ROOT / "kiosk/art/logo/rozet_koyu.png", ROOT / "kiosk/art/logo/yatay_koyu.png"]

KIOSK = """\
The building is the "MHC Mola" roadside kiosk, a small free-standing pavilion 5.0 m long, 3.0 m deep and 3.0 m high,
standing on a low concrete plinth on an open paved plaza beside a fuel station.
- Plan is a rounded rectangle: all four vertical corners are smoothly curved (450 mm radius), no sharp corners.
- Walls from the black base skirt up to 2.40 m are clad in closely spaced vertical walnut-brown hardwood slats
  (40 mm wide, 80 mm spacing) that wrap continuously around the curved corners, with a black aluminium skirt at the bottom.
- The top band from 2.40 m to 3.00 m is matte black aluminium composite (Alucobond) panels with fine vertical joints,
  also wrapping the curved corners, with a flat roof and a small white AC condenser sitting on the roof.
- The front has one wide centred service window (3.6 m wide, sill at 1.08 m, head at 2.25 m) in slim black aluminium frames,
  split into three bays; the middle bay holds a large black digital menu screen; a thin LED strip canopy runs above it;
  two small natural-oak bar shelves on black brackets sit under the window.
- Through the glass: a bright white interior with a stainless espresso machine, grinder and shelving, pendant lights.
- On the front black band: the logo exactly as in the logo reference images - the round seal (coffee bean whose centre
  crease is a winding road) followed by "MHC MOLA" in wide geometric capitals with "YOL ÜSTÜ" underneath, in warm cream,
  built as backlit 3D channel letters. A round black double-sided blade sign with the same seal projects from the upper
  left corner of the band on two short black arms."""

RULES = """\
Strict rules:
- Keep the kiosk's shape, proportions, camera angle, slat rhythm, window layout and sign positions identical to the first
  reference image (a CG render of the same kiosk). Change only materials, lighting and surroundings to real photography.
- The logo must match the logo reference images: same seal, same letters "MHC MOLA" and "YOL ÜSTÜ", correctly spelled,
  no other words anywhere on the building. Do not add words like coffee, kahve, çay, tea, tost or cafe on signs.
- Photorealistic architectural photograph, full-frame camera, 35 mm lens, natural depth of field, real wood grain with
  subtle weathering, real reflections in the glass, physically correct shadows, no CG look, no illustration, no people
  posing in front of the window, no watermark, no captions."""

SHOTS = {
    "gunduz": {
        "ref": "kiosk/art/cover.png",
        "scene": """\
Late afternoon golden-hour light from the left, clear sky with a few clouds. Front three-quarter view as in the reference.
Behind the kiosk, slightly out of focus: a modern fuel station canopy with pumps, a few parked cars, trees.
To the right a few wooden café chairs and two white parasols on the plaza. Clean grey concrete pavers, a little dust.""",
    },
    "aksam": {
        "ref": "kiosk/art/cover.png",
        "scene": """\
Blue hour just after sunset, deep blue sky with the last orange glow on the horizon. Same front three-quarter view.
The interior is lit warm white and glows through the glass, the menu screen is bright, the LED canopy strip and the
cream backlit logo letters and round blade sign glow softly. The fuel station canopy behind is lit with white LEDs,
car headlights blur in the distance, wet-looking pavers catch soft reflections of the kiosk lights.""",
    },
    "kus_bakisi": {
        "ref": "kiosk/art/steps/08_final.png",
        "scene": """\
High three-quarter drone view as in the reference, overcast soft daylight. The kiosk sits on its concrete plinth at the
edge of a fuel station forecourt: pump islands and the station canopy partly in frame at one side, painted parking
lines, a few cars, a green verge with young trees. The roof is visible with the small white AC condenser.""",
    },
}


def key():
    k = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not k:
        sys.exit("GEMINI_API_KEY bulunamadı. Anahtarı ortam değişkeni olarak tanımlayıp tekrar çalıştırın.")
    return k


def call(method, path, body=None):
    req = urllib.request.Request(f"{API}/{path}", method=method,
                                 data=None if body is None else json.dumps(body).encode(),
                                 headers={"x-goog-api-key": key(), "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {detail[:800]}") from None


def image_models():
    models, token = [], ""
    while True:
        page = call("GET", f"models?pageSize=200{'&pageToken=' + token if token else ''}")
        models += page.get("models", [])
        token = page.get("nextPageToken")
        if not token:
            break
    return [m for m in models
            if "image" in m["name"] and "generateContent" in m.get("supportedGenerationMethods", [])]


def pick_model():
    """Newest image-capable Gemini model, preferring the Pro tier."""
    def rank(m):
        name = m["name"].split("/")[-1]
        version = [int(x) for x in re.findall(r"\d+", name.split("-image")[0])] or [0]
        return ("pro" in name, "preview" not in name, version)
    models = image_models()
    return max(models, key=rank)["name"].split("/")[-1] if models else FALLBACK_MODEL


def inline(path):
    path = ROOT / path
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(path.read_bytes()).decode()}}


def prompt(shot):
    return "\n\n".join([
        "Turn the first reference image (a CG render) into a photorealistic photograph of the same kiosk. "
        "The other reference images are the kiosk's logo: the round seal and the horizontal lockup.",
        KIOSK, SHOTS[shot]["scene"], RULES])


def request(shot, model, size=True):
    image_config = {"aspectRatio": "16:9"}
    if size and "pro" in model:
        image_config["imageSize"] = "2K"
    parts = [{"text": prompt(shot)}, inline(SHOTS[shot]["ref"])] + [inline(p) for p in LOGO_REFS]
    return {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"responseModalities": ["TEXT", "IMAGE"], "imageConfig": image_config}}


def generate(shot, model):
    try:
        res = call("POST", f"models/{model}:generateContent", request(shot, model))
    except RuntimeError as e:
        if "imageSize" not in str(e) and "image_size" not in str(e):
            raise
        res = call("POST", f"models/{model}:generateContent", request(shot, model, size=False))
    images, notes = [], []
    for cand in res.get("candidates", []):
        for part in cand.get("content", {}).get("parts", []):
            data = part.get("inlineData") or part.get("inline_data")
            if data:
                images.append((data.get("mimeType") or data.get("mime_type"), base64.b64decode(data["data"])))
            elif part.get("text"):
                notes.append(part["text"].strip())
    if not images:
        reason = res.get("promptFeedback") or [c.get("finishReason") for c in res.get("candidates", [])]
        raise RuntimeError(f"görsel dönmedi: {reason} {' '.join(notes)[:300]}")
    return images, notes


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true", help="görüntü üretebilen modelleri listele")
    ap.add_argument("--shots", default=",".join(SHOTS), help=f"virgülle: {', '.join(SHOTS)}")
    ap.add_argument("--n", type=int, default=1, help="her çekim için varyasyon sayısı")
    ap.add_argument("--model", help="model adı (verilmezse en yeni görüntü modeli seçilir)")
    ap.add_argument("--print-prompts", action="store_true", help="API çağırmadan promptları ve referansları yaz")
    args = ap.parse_args()
    shots = [s.strip() for s in args.shots.split(",") if s.strip()]
    unknown = [s for s in shots if s not in SHOTS]
    if unknown:
        sys.exit(f"bilinmeyen çekim: {', '.join(unknown)}")

    if args.print_prompts:
        for s in shots:
            refs = [SHOTS[s]["ref"]] + [str(p.relative_to(ROOT)) for p in LOGO_REFS]
            print(f"=== {s}  (referanslar: {', '.join(refs)})\n{prompt(s)}\n")
        return
    if args.list:
        for m in image_models():
            print(f"{m['name'].split('/')[-1]:45s} {m.get('displayName', '')}")
        return

    model = args.model or pick_model()
    print(f"model: {model}")
    OUT.mkdir(parents=True, exist_ok=True)
    for s in shots:
        for i in range(1, args.n + 1):
            print(f"{s} #{i} …", flush=True)
            try:
                images, notes = generate(s, model)
            except RuntimeError as e:
                print(f"  HATA: {e}")
                continue
            for k, (mime, data) in enumerate(images):
                ext = ".jpg" if "jpeg" in (mime or "") else ".png"
                path = OUT / f"{s}_{i}{'' if k == 0 else chr(97 + k)}{ext}"
                path.write_bytes(data)
                print(f"  → {path.relative_to(ROOT)} ({len(data) // 1024} KB)")
            if notes:
                print(f"  not: {' '.join(notes)[:200]}")


if __name__ == "__main__":
    main()
