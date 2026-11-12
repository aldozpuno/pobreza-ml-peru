"""Genera las figuras propias de la tesis que no produce el pipeline: la integración de los
módulos (Figura 1), el flujograma del proceso (Figura 2) y las capturas de código del Anexo 7.

La captura de la web (figuras/fig_web.png) se toma a mano desde el navegador.
Uso: python figuras.py
"""

from __future__ import annotations

import re
from pathlib import Path

import logging

import matplotlib

matplotlib.use("Agg")
logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

AQUI = Path(__file__).parent
RAIZ = AQUI.parents[1]
SALIDA = AQUI / "figuras"

ETAPAS = [("1. Descargar", "Módulos 01, 02, 03, 04, 05,\n34 y 37 del INEI, 2017–2024"),
          ("2. Construir", "Un registro por hogar; los años\nse apilan y se marcan los\nhogares repetidos"),
          ("3. Medir", "Incidencia con FACTOR07 ×\nMIEPERHO; se detiene si difiere\ndel INEI en más de 0.3 pp"),
          ("4. Entrenar", "Cinco modelos por pliegue;\ncalibración isotónica y umbral\nen el año siguiente"),
          ("5. Evaluar", "Métricas, prueba de DeLong,\nerror por departamento\ny valores SHAP"),
          ("6. Reportar", "Tablas y figuras de la tesis\ny datos de la web\nde resultados")]


def flujograma() -> None:
    plt.rcParams["font.family"] = ["Times New Roman", "Liberation Serif", "serif"]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=300)
    ax.set_xlim(0, 60); ax.set_ylim(0, 40); ax.axis("off")
    w, h = 17, 13
    pos = [(1, 24), (21.5, 24), (42, 24), (1, 4), (21.5, 4), (42, 4)]
    for i, ((titulo, texto), (x, y)) in enumerate(zip(ETAPAS, pos)):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.8",
                                    fc="#D9D9D9" if i == 2 else "#F2F2F2", ec="black", lw=0.9))
        ax.text(x + w / 2, y + h - 2.6, titulo, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 1.6, texto, ha="center", va="center", fontsize=9, linespacing=1.4)
    flecha = lambda a, b: ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=1, color="black"))
    flecha((18.1, 30.5), (21.4, 30.5)); flecha((38.6, 30.5), (41.9, 30.5))
    ax.plot([50.5, 50.5, 9.5], [23.9, 20.5, 20.5], color="black", lw=1); flecha((9.5, 20.5), (9.5, 17.1))
    flecha((18.1, 10.5), (21.4, 10.5)); flecha((38.6, 10.5), (41.9, 10.5))
    fig.savefig(SALIDA / "fig_flujograma.png", bbox_inches="tight", facecolor="white", pad_inches=0.05)
    plt.close(fig)


def arquitectura() -> None:
    """Figura 1: cómo se integran los módulos de la ENAHO en una base con un registro por hogar.

    Refleja `processing/assemble.py`: los módulos de personas se resumen por hogar y todo se une
    a la Sumaria por (año, CONGLOME, VIVIENDA, HOGAR); luego se apilan los años.
    """
    plt.rcParams["font.family"] = ["Times New Roman", "Liberation Serif", "serif"]
    fig, ax = plt.subplots(figsize=(9, 4.6), dpi=300)
    ax.set_xlim(0, 60); ax.set_ylim(0, 40); ax.axis("off")
    w, h = 17, 13
    cajas = [
        ((1, 24), "Módulos de personas", "02 (200) Miembros del hogar\n03 (300) Educación\n04 (400) Salud\n05 (500) Empleo", False),
        ((21.5, 24), "Resumen por hogar", "Conteos, promedios y\nproporciones de los\nmiembros de cada hogar", False),
        ((42, 24), "Módulos de hogar", "34 Sumaria (tabla base)\n01 (100) Vivienda y hogar\n37 (700) Programas sociales", False),
        ((11.25, 4), "Unión por hogar", "A la Sumaria, por la llave\naño, CONGLOME,\nVIVIENDA y HOGAR", True),
        ((31.75, 4), "Base apilada 2017–2024", "Un registro por hogar y año;\nse marcan los hogares\nentrevistados más de un año", False),
    ]
    for (x, y), titulo, texto, resaltada in cajas:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.8",
                                    fc="#D9D9D9" if resaltada else "#F2F2F2", ec="black", lw=0.9))
        ax.text(x + w / 2, y + h - 2.6, titulo, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 1.6, texto, ha="center", va="center", fontsize=9, linespacing=1.4)
    flecha = lambda a, b: ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", lw=1, color="black"))
    flecha((18.1, 30.5), (21.4, 30.5))                       # personas → resumen por hogar
    ax.plot([30, 30], [23.9, 20.5], color="black", lw=1)     # resumen ↓
    ax.plot([50.5, 50.5], [23.9, 20.5], color="black", lw=1)  # módulos de hogar ↓
    ax.plot([50.5, 19.75], [20.5, 20.5], color="black", lw=1)
    flecha((19.75, 20.5), (19.75, 17.1))                     # → unión por hogar
    flecha((28.35, 10.5), (31.65, 10.5))                     # unión → base apilada
    fig.savefig(SALIDA / "fig_arquitectura.png", bbox_inches="tight", facecolor="white", pad_inches=0.05)
    plt.close(fig)


def _fuente_codigo() -> str:
    """Fuente monoespaciada disponible en el sistema para las capturas de código."""
    from pygments.formatters.img import FontNotFound, ImageFormatter
    for nombre in ("DejaVu Sans Mono", "Consolas", "Courier New", "Liberation Mono"):
        try:
            ImageFormatter(font_name=nombre)
            return nombre
        except FontNotFound:
            continue
    raise FontNotFound("No hay una fuente monoespaciada para las capturas de código")


def _tramo(ruta: Path, inicio: str, fin: str) -> str:
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    i = next(k for k, l in enumerate(lineas) if l.startswith(inicio))
    j = next(k for k in range(i + 1, len(lineas)) if re.match(fin, lineas[k]))
    return "\n".join(lineas[i:j]).rstrip() + "\n"


def capturas_codigo() -> None:
    from pygments import highlight
    from pygments.formatters import ImageFormatter
    from pygments.lexers import PythonLexer
    src = RAIZ / "src/pobreza"
    piezas = {
        "codigo_medicion": "# src/pobreza/measurement/poverty.py\n"
        + _tramo(src / "measurement/poverty.py", "def _tasa", r"^def incidencia") + "\n"
        + _tramo(src / "measurement/poverty.py", "def incidencia", r"^\S"),
        "codigo_informalidad": "# src/pobreza/processing/empleo.py\n"
        + _tramo(src / "processing/empleo.py", "def informal", r"^def procesar"),
        "codigo_delong": "# src/pobreza/evaluation/inference.py\n"
        + _tramo(src / "evaluation/inference.py", "def delong", r"^def comparar"),
    }
    fuente = _fuente_codigo()
    for nombre, codigo in piezas.items():
        imagen = highlight(codigo, PythonLexer(), ImageFormatter(font_name=fuente, font_size=15,
                                                                 line_numbers=False, image_pad=14))
        (SALIDA / f"{nombre}.png").write_bytes(imagen)


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    arquitectura()
    flujograma()
    capturas_codigo()
    print("Figuras listas en", SALIDA)
