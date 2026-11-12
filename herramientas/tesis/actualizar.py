"""Actualiza el borrador de la tesis con los resultados actuales del pipeline.

Pasos: 1) primera pasada sobre el borrador; 2) se convierte a PDF con LibreOffice o, si no está,
con Microsoft Word, para calcular las páginas (requiere también pdftotext, de Poppler);
3) segunda pasada con los números de página en los índices;
4) se valida y se reemplaza el borrador original (no se dejan copias en la carpeta).

Uso:  python herramientas/tesis/actualizar.py "D:/Proyecto Ing Aldo/BORRADOR DE TESIS FINAL.docx"
Opcional: --respaldo <ruta>  guarda una copia del original antes de reemplazarlo.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))

import armar  # noqa: E402
import paginas  # noqa: E402


def _soffice() -> str | None:
    for nombre in ("soffice", "libreoffice", r"C:\Program Files\LibreOffice\program\soffice.exe"):
        if shutil.which(nombre) or Path(nombre).exists():
            return nombre
    return None


def _pdf_con_word(docx: Path, pdf: Path) -> bool:
    """Convierte a PDF con Microsoft Word (Windows). Abre una instancia propia, en solo lectura,
    y la cierra al terminar; no toca las ventanas de Word que el usuario tenga abiertas."""
    if sys.platform != "win32" or not shutil.which("powershell"):
        return False
    orden = (
        "$ErrorActionPreference='Stop'; $w = New-Object -ComObject Word.Application; "
        "try { $w.Visible = $false; $w.DisplayAlerts = 0; "
        f"$d = $w.Documents.Open('{docx}', $false, $true); "
        f"$d.ExportAsFixedFormat('{pdf}', 17); $d.Close($false) }} finally {{ $w.Quit() }}")
    try:
        subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", orden],
                       check=True, capture_output=True, timeout=600)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
    return pdf.exists()


def _convertir_pdf(docx: Path, carpeta: Path) -> Path | None:
    """PDF del borrador para calcular las páginas: LibreOffice si está, si no Microsoft Word."""
    pdf = carpeta / (docx.stem + ".pdf")
    soffice = _soffice()
    if soffice:
        subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", str(carpeta), str(docx)],
                       check=True, capture_output=True)
        return pdf if pdf.exists() else None
    return pdf if _pdf_con_word(docx, pdf) else None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("borrador", type=Path)
    ap.add_argument("--respaldo", type=Path)
    args = ap.parse_args()
    if args.respaldo:
        shutil.copy2(args.borrador, args.respaldo)
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        paso1, final = tmp / "paso1.docx", tmp / "final.docx"
        armar.main(str(args.borrador), str(paso1))
        pags = {}
        pdf = _convertir_pdf(paso1, tmp) if shutil.which("pdftotext") else None
        if pdf:
            paginas.main(str(paso1), str(pdf), str(tmp / "paginas.json"))
            pags = json.loads((tmp / "paginas.json").read_text(encoding="utf-8"))
        else:
            print("Sin pdftotext (Poppler) o sin LibreOffice ni Word para convertir a PDF: los números de "
                  "página de los índices se actualizan en Word con Ctrl+E y luego F9.")
        armar.main(str(args.borrador), str(final), pags or None)
        shutil.copy2(final, args.borrador)
    print("Borrador actualizado:", args.borrador)


if __name__ == "__main__":
    main()
