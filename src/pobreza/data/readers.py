"""Lectura de los archivos de la ENAHO (Stata, SPSS o CSV), dentro o fuera de un zip.

Normaliza los nombres de columnas (minúsculas, `$` → `_`, `año` → `anio`) y conserva
solo las columnas que el módulo necesita. Las columnas que no existen en un año se
crean vacías y se informan, para que un cambio de cuestionario no rompa el pipeline.
"""

from __future__ import annotations

import io
import tempfile
import unicodedata
import zipfile
from pathlib import Path

import pandas as pd
import pyreadstat

from pobreza.config import Config
from pobreza.data.catalog import Modulo, modulo
from pobreza.logging_utils import obtener
from pobreza.processing.keys import normalizar_llaves

log = obtener("data.readers")


def normalizar_columna(nombre: str) -> str:
    texto = unicodedata.normalize("NFKD", str(nombre)).encode("ascii", "ignore").decode()
    texto = texto.strip().lower().replace("$", "_")
    return "anio" if texto in {"ano", "anio", "year"} else texto


def _leer_bytes(nombre: str, contenido: bytes) -> pd.DataFrame:
    sufijo = Path(nombre).suffix.lower()
    if sufijo == ".csv":
        return pd.read_csv(io.BytesIO(contenido), sep=None, engine="python",
                           encoding="latin-1", dtype=str)
    # En Windows un archivo temporal abierto no se puede volver a abrir: se escribe,
    # se cierra y recién entonces lo lee pyreadstat.
    with tempfile.TemporaryDirectory() as carpeta:
        temporal = Path(carpeta) / f"modulo{sufijo}"
        temporal.write_bytes(contenido)
        lector = pyreadstat.read_dta if sufijo == ".dta" else pyreadstat.read_sav
        datos, _ = lector(str(temporal), apply_value_formats=False)
    return datos


def _buscar_en_zip(ruta_zip: Path, mod: Modulo) -> tuple[str, bytes]:
    with zipfile.ZipFile(ruta_zip) as archivo:
        candidatos = [n for n in archivo.namelist() if mod.coincide(n)]
        if not candidatos:
            raise FileNotFoundError(f"{ruta_zip.name}: no hay archivo que coincida con "
                                    f"{mod.patron_archivo}")
        elegido = sorted(candidatos, key=lambda n: (not n.lower().endswith(".dta"), len(n)))[0]
        return elegido, archivo.read(elegido)


def _buscar_suelto(carpeta: Path, mod: Modulo) -> tuple[str, bytes]:
    for ruta in sorted(carpeta.rglob("*")):
        if ruta.is_file() and mod.coincide(ruta.name):
            return ruta.name, ruta.read_bytes()
    raise FileNotFoundError(f"No se encontró el módulo {mod.nombre} en {carpeta}")


def leer_modulo(config: Config, anio: int, nombre_modulo: str) -> pd.DataFrame:
    """Lee un módulo de un año desde `datos/crudos/<año>/` (zip o archivo suelto)."""
    mod = modulo(nombre_modulo)
    carpeta = config.rutas.crudos / str(anio)
    zip_modulo = carpeta / f"{nombre_modulo}.zip"
    if zip_modulo.exists():
        nombre, contenido = _buscar_en_zip(zip_modulo, mod)
    else:
        nombre, contenido = _buscar_suelto(carpeta, mod)
    datos = _leer_bytes(nombre, contenido)
    datos.columns = [normalizar_columna(c) for c in datos.columns]
    return seleccionar_columnas(datos, mod, anio)


def seleccionar_columnas(datos: pd.DataFrame, mod: Modulo, anio: int) -> pd.DataFrame:
    """Conserva las columnas del módulo; crea vacías las ausentes y lo registra."""
    faltantes = [c for c in mod.columnas if c not in datos.columns]
    if faltantes:
        log.warning("%s %s: columnas ausentes %s (se dejan vacías)", anio, mod.nombre, faltantes)
    salida = normalizar_llaves(datos.reindex(columns=list(mod.columnas)))
    salida["anio"] = anio
    return salida
