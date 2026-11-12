"""Lectura y escritura de resultados intermedios entre etapas.

Todo resultado tabular se guarda como CSV en `resultados/reportes/datos/` para que pueda
abrirse en Excel, y los objetos pequeños como JSON.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from pobreza.config import Config


def carpeta_datos(config: Config) -> Path:
    ruta = config.rutas.reportes / "datos"
    ruta.mkdir(parents=True, exist_ok=True)
    return ruta


def guardar_tabla(config: Config, nombre: str, tabla: pd.DataFrame) -> Path:
    ruta = carpeta_datos(config) / f"{nombre}.csv"
    tabla.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


def leer_tabla(config: Config, nombre: str) -> pd.DataFrame:
    ruta = carpeta_datos(config) / f"{nombre}.csv"
    if not ruta.exists():
        raise FileNotFoundError(f"Falta {ruta}. Ejecute la etapa que lo produce.")
    return pd.read_csv(ruta, dtype={"departamento": str, "codigo": str})


def _a_json(valor: Any) -> Any:
    if isinstance(valor, (np.integer,)):
        return int(valor)
    if isinstance(valor, (np.floating,)):
        return None if np.isnan(valor) else round(float(valor), 6)
    if isinstance(valor, float) and np.isnan(valor):
        return None
    return valor


def guardar_json(ruta: Path, objeto: Any) -> Path:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(objeto, archivo, ensure_ascii=False, indent=2, default=_a_json)
    return ruta


def leer_json(ruta: Path) -> Any:
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)


def registros(tabla: pd.DataFrame, decimales: int = 6) -> list[dict[str, Any]]:
    """Tabla → lista de diccionarios con números redondeados y NaN como None.

    Seis decimales: la web vuelve a redondear al mostrar, y con cuatro un 0.628536 pasaba a
    0.6285 y de ahí a 0,628, distinto del 0.629 de la tesis.
    """
    limpia = tabla.copy()
    for columna in limpia.select_dtypes("number").columns:
        limpia[columna] = limpia[columna].round(decimales)
    limpia = limpia.astype(object).where(limpia.notna(), None)
    return limpia.to_dict(orient="records")
