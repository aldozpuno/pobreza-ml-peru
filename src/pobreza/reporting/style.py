"""Estilo de las figuras para la tesis (Guía EPG UNA Puno / APA 7).

Reglas que aplica:
    - sin título dentro de la imagen: el rótulo "Figura N" y su título los pone la tesis
    - etiquetas en español, fuente con serifa, tamaño legible al ancho del texto (15 cm)
    - gris para el contexto y un solo color de acento para lo que la figura quiere mostrar
    - 300 ppp, fondo blanco
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ANCHO_TEXTO_CM = 15.0
ACENTO = "#1F5FA8"
ACENTO_SUAVE = "#8FB3DE"
GRIS = "#8C8C8C"
GRIS_CLARO = "#D9D9D9"
TEXTO = "#222222"
BUENO = "#2E7D32"
MALO = "#C62828"


def cm(valor: float) -> float:
    return valor / 2.54


def aplicar_estilo() -> None:
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"],
        "font.size": 10,
        "axes.titlesize": 10,
        "axes.labelsize": 10,
        "axes.edgecolor": GRIS,
        "axes.labelcolor": TEXTO,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRIS_CLARO,
        "grid.linewidth": 0.6,
        "xtick.color": TEXTO,
        "ytick.color": TEXTO,
        "legend.frameon": False,
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "savefig.facecolor": "white",
        "axes.formatter.use_locale": False,
    })


def figura(alto_cm: float = 8.0, ancho_cm: float = ANCHO_TEXTO_CM, **kwargs):
    """Crea una figura al ancho del texto de la tesis."""
    aplicar_estilo()
    return plt.subplots(figsize=(cm(ancho_cm), cm(alto_cm)), **kwargs)


def decimal(valor: float, decimales: int = 1) -> str:
    """Número con punto decimal, como en el texto y las tablas de la tesis (la web usa coma)."""
    return f"{valor:.{decimales}f}"


def miles(valor: float, _posicion=None) -> str:
    """Entero con espacio de miles (30 000), como en las tablas de la tesis."""
    return f"{int(round(valor)):,}".replace(",", " ")


def guardar(fig, carpeta: Path, nombre: str) -> Path:
    """Guarda la figura en PNG a 300 ppp y la cierra."""
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.png"
    fig.savefig(ruta)
    plt.close(fig)
    return ruta
