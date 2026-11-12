"""Registro de mensajes del pipeline en consola y en archivo."""

from __future__ import annotations

import logging
from pathlib import Path

FORMATO = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"


def configurar(archivo: Path | None = None, nivel: int = logging.INFO) -> None:
    """Configura el registro una sola vez; si se da `archivo`, también escribe ahí."""
    raiz = logging.getLogger("pobreza")
    if raiz.handlers:
        return
    raiz.setLevel(nivel)
    consola = logging.StreamHandler()
    consola.setFormatter(logging.Formatter(FORMATO, "%H:%M:%S"))
    raiz.addHandler(consola)
    if archivo is not None:
        archivo.parent.mkdir(parents=True, exist_ok=True)
        en_archivo = logging.FileHandler(archivo, encoding="utf-8")
        en_archivo.setFormatter(logging.Formatter(FORMATO))
        raiz.addHandler(en_archivo)


def obtener(nombre: str) -> logging.Logger:
    """Devuelve un registrador hijo de `pobreza` (por ejemplo, `pobreza.data`)."""
    return logging.getLogger(f"pobreza.{nombre}")
