"""Menu screen artwork (1920x1080) rendered with Pillow from the brand tokens.

The result is committed as kiosk/art/menu.png so Blender's bundled Python
(which has no Pillow) can build the scene. Re-run after editing the menu:
    python -m kiosk.menu_art
"""
from PIL import Image, ImageDraw, ImageFont

from . import config as C

W, H = 1920, 1080

MENU = [
    ("Kahve", [("Espresso", 70), ("Americano", 95), ("Latte", 110), ("Cappuccino", 110),
               ("Filtre kahve", 90), ("Türk kahvesi", 80)]),
    ("Tost", [("Kaşarlı tost", 120), ("Karışık tost", 150), ("Sucuklu tost", 160),
              ("Hindi füme sandviç", 170), ("Ayvalık tostu", 190)]),
    ("Çay", [("Demlik çay", 40), ("Fincan çay", 50), ("Bitki çayı", 60),
             ("Limonata", 80), ("Sıcak çikolata", 95)]),
]


def _rgb(token):
    h = C.PALETTE[token].lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def render(path):
    fonts = C.ASSETS / "fonts"
    serif = lambda s: ImageFont.truetype(str(fonts / "Fraunces-SemiBold.ttf"), s)
    sans = lambda s: ImageFont.truetype(str(fonts / "Jost-Regular.ttf"), s)
    sans_m = lambda s: ImageFont.truetype(str(fonts / "Jost-Medium.ttf"), s)
    ink, cream = _rgb("screen-ink"), _rgb("cream")
    muted = tuple(int(c * 0.62 + i * 0.38) for c, i in zip(cream, ink))
    wood = _rgb("oak-counter")

    im = Image.new("RGB", (W, H), ink)
    d = ImageDraw.Draw(im)

    # Header: the MHC Mola logo (kiosk/art/logo/logo_seffaf.png, from brand.py) + a short line
    logo = Image.open(C.ROOT / "kiosk" / "art" / "logo" / "logo_seffaf.png").convert("RGBA")
    lh = 190
    logo = logo.resize((round(logo.width * lh / logo.height), lh), Image.LANCZOS)
    im.paste(logo, (80, 50), logo)
    d.text((W - 80, 150), "Yola devam etmeden önce.", font=sans(34), fill=muted, anchor="rm")
    d.line((80, 268, W - 80, 268), fill=muted, width=2)

    col_w = (W - 160) // 3
    for i, (title, items) in enumerate(MENU):
        x0 = 80 + i * col_w + (40 if i else 0)
        x1 = 80 + (i + 1) * col_w - 40
        d.text((x0, 330), title, font=serif(64), fill=wood, anchor="ls")
        y = 410
        for name, price in items:
            d.text((x0, y), name, font=sans(38), fill=cream, anchor="ls")
            d.text((x1, y), f"{price} TL", font=sans_m(38), fill=cream, anchor="rs")
            y += 104
        if i:
            d.line((x0 - 40, 300, x0 - 40, H - 120), fill=(48, 46, 44), width=2)

    d.line((80, H - 90, W - 80, H - 90), fill=(48, 46, 44), width=2)
    d.text((W // 2, H - 48), "Sipariş için soldaki pencere  ·  Teslim sağda", font=sans(30),
           fill=muted, anchor="mm")
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return path


if __name__ == "__main__":
    print(render(C.ROOT / "kiosk" / "art" / "menu.png"))
