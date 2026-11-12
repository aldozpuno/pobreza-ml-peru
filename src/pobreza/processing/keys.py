"""Identificadores de hogar y persona.

En la ENAHO un hogar se identifica por CONGLOME (6), VIVIENDA (3) y HOGAR (2), y una
persona además por CODPERSO (2). Según el año y el formato, estos códigos llegan como
texto o como número; aquí se rellenan con ceros para que los cruces entre módulos
y entre años no fallen en silencio.
"""

from __future__ import annotations

import pandas as pd

ANCHOS = {"conglome": 6, "vivienda": 3, "hogar": 2, "codperso": 2, "ubigeo": 6}
LLAVE_HOGAR = ["conglome", "vivienda", "hogar"]
LLAVE_ANIO_HOGAR = ["anio", *LLAVE_HOGAR]


def _rellenar(serie: pd.Series, ancho: int) -> pd.Series:
    texto = serie.astype("string").str.strip().str.replace(r"\.0$", "", regex=True)
    return texto.str.zfill(ancho)


def normalizar_llaves(datos: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia con los identificadores como texto de ancho fijo."""
    datos = datos.copy()
    for columna, ancho in ANCHOS.items():
        if columna in datos.columns:
            datos[columna] = _rellenar(datos[columna], ancho)
    return datos


def id_hogar(datos: pd.DataFrame) -> pd.Series:
    """Identificador único del hogar dentro de un año: CONGLOME-VIVIENDA-HOGAR."""
    return datos["conglome"] + "-" + datos["vivienda"] + "-" + datos["hogar"]


def verificar_unicidad(datos: pd.DataFrame, llave: list[str], contexto: str) -> pd.DataFrame:
    """Elimina filas repetidas por la llave e informa cuántas había."""
    repetidas = datos.duplicated(subset=llave, keep="first")
    if repetidas.any():
        from pobreza.logging_utils import obtener
        obtener("processing.keys").warning(
            "%s: %d filas repetidas por %s; se conserva la primera", contexto,
            int(repetidas.sum()), llave)
    return datos.loc[~repetidas].copy()
