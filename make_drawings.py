"""Build the fabrication drawing set (A3 PDF + one PNG per sheet).

    python make_drawings.py              # -> docs/uretim/MHC_Kiosk_Usta_Paftalari.pdf (3 sayfa)
                                         #    docs/uretim/MHC_Kiosk_Uretim_Paftalari.pdf (detaylı)
    python make_drawings.py usta_1-3 02  # only these sheets (PNG preview), no PDF

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
from kiosk.drawings.simple import SIMPLE  # noqa: E402

OUT = C.ROOT / "docs" / "uretim"


SETS = [  # (pdf name, title, sheets, png prefix)
    ("MHC_Kiosk_Usta_Paftalari.pdf", "MHC Mola Kiosk - Usta Paftaları (3 sayfa)", SIMPLE, "usta_"),
    ("MHC_Kiosk_Uretim_Paftalari.pdf", "MHC Mola Kiosk - Detaylı Üretim Paftaları", SHEETS, ""),
]


def main(only=()):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "png").mkdir(exist_ok=True)
    for name, title, sheets, prefix in SETS:
        pdf_path = OUT / name
        tmp = OUT / f"_partial_{name}"
        with PdfPages(pdf_path if not only else tmp) as pdf:
            info = pdf.infodict()
            info["Title"] = title
            for no, sheet_title, scale, fn in sheets:
                tag = prefix + no.replace("/", "-")
                if only and tag not in only:
                    continue
                sh = Sheet(no, sheet_title, scale)
                fn(sh)
                sh.save(pdf, OUT / "png" / f"{tag}.png")
                print(f"{tag}  {sheet_title}")
        if only:
            tmp.unlink(missing_ok=True)
        else:
            print("->", pdf_path)


if __name__ == "__main__":
    main(tuple(sys.argv[1:]))
