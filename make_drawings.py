"""Build the fabrication drawing set (A3 PDF + one PNG per sheet).

    python make_drawings.py              # -> docs/uretim/MHC_Kiosk_Uretim_Paftalari.pdf
    python make_drawings.py 02 05        # only these sheets (PNG preview), no PDF

Needs matplotlib (pip install matplotlib). The 3D step images come from
render_steps.py and are committed under kiosk/art/steps/.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

from kiosk import config as C  # noqa: E402
from kiosk.drawings.sheet import Sheet  # noqa: E402
from kiosk.drawings.sheets import SHEETS  # noqa: E402

OUT = C.ROOT / "docs" / "uretim"


def main(only=()):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    pdf_path = OUT / "MHC_Kiosk_Uretim_Paftalari.pdf"
    with PdfPages(pdf_path if not only else OUT / "_partial.pdf") as pdf:
        info = pdf.infodict()
        info["Title"] = "MHC Kahve Kiosku - Üretim Paftaları"
        info["Subject"] = "Şasi, sandviç panel, köşe modülü, çıta, Alucobond, cam, asma kat"
        for no, title, scale, fn in SHEETS:
            if only and no not in only:
                continue
            sh = Sheet(no, title, scale)
            fn(sh)
            sh.save(pdf, OUT / "png" / f"{no}.png")
            print(f"{no}  {title}")
    if only:
        (OUT / "_partial.pdf").unlink()
    else:
        print("->", pdf_path)


if __name__ == "__main__":
    main(tuple(sys.argv[1:]))
