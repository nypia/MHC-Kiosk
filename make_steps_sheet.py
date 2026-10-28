"""Combine the 8 assembly-step renders into one labelled image.

    python make_steps_sheet.py   # -> docs/uretim/montaj_adimlari.jpg
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent
STEPS = ROOT / "kiosk" / "art" / "steps"
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "docs" / "uretim" / "montaj_adimlari.jpg"

ITEMS = [
    ("01_sasi", "1 · Demir şasi", "Taban çerçeve, kirişler, dikmeler, üst çerçeve"),
    ("02_panel", "2 · Sandviç panel", "Düz yüzlere panel, köşelere kavisli modül, çatı"),
    ("03_bosluk", "3 · Boşluklar", "Ortada 3600 × 1170 cam, yanda kapı boşluğu"),
    ("04_cita", "4 · Karkas ve çıta", "Siyah karkas, 40×28 ahşap çıta, 40 mm ara"),
    ("05_alucobond", "5 · Alükobond", "Üst bant 600, logo ve daire tabela"),
    ("06_cam_kapi", "6 · Cam ve kapı", "Doğrama, cam, menü ekranı, kapı, bar rafları"),
    ("07_asma_kat", "7 · Asma tavan + klima", "+2500 tavan, üstünde gizli kanallı klima"),
    ("08_final", "8 · Teslim", "Işıklar, servis kapağı, son kontroller"),
]
INK, CREAM, PAPER, GREY = (31, 29, 28), (239, 226, 196), (244, 239, 230), (110, 104, 98)


def main(cols=4, cell_w=900, gap=36, margin=60):
    imgs = [Image.open(STEPS / f"{name}.png").convert("RGB") for name, _, _ in ITEMS]
    cell_h = round(cell_w * imgs[0].height / imgs[0].width)
    rows = (len(imgs) + cols - 1) // cols
    text_h = 130
    head_h = 150
    W = margin * 2 + cols * cell_w + (cols - 1) * gap
    H = margin + head_h + rows * (cell_h + text_h) + (rows - 1) * gap + margin
    sheet = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(sheet)
    f = lambda name, s: ImageFont.truetype(str(FONTS / name), s)  # noqa: E731
    d.text((margin, margin), "MHC Mola · Kiosk montaj sırası", font=f("Jost-Medium.ttf", 64), fill=INK)
    d.text((margin, margin + 84), "5000 × 3000 × 3000 mm  ·  şasi  ·  panel  ·  çıta  ·  alükobond  ·  cam  ·  asma tavan",
           font=f("Jost-Regular.ttf", 34), fill=GREY)
    for i, (im, (_, title, desc)) in enumerate(zip(imgs, ITEMS)):
        c, r = i % cols, i // cols
        x = margin + c * (cell_w + gap)
        y = margin + head_h + r * (cell_h + text_h + gap)
        sheet.paste(im.resize((cell_w, cell_h), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + cell_w - 1, y + cell_h - 1), outline=(200, 194, 184), width=2)
        d.text((x, y + cell_h + 22), title, font=f("Jost-Medium.ttf", 44), fill=INK)
        d.text((x, y + cell_h + 80), desc, font=f("Jost-Regular.ttf", 30), fill=GREY)
    sheet.save(OUT, quality=92, optimize=True)
    print(OUT, sheet.size)


if __name__ == "__main__":
    main()
