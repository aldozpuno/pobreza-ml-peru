"""Funciones auxiliares compartidas por los procesadores de módulos."""

from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

from pobreza.processing.keys import LLAVE_ANIO_HOGAR

# Códigos que el INEI usa como "sin dato" en variables numéricas.
CODIGOS_FALTANTES = {99, 999, 9999, 99999, 999999}


def a_numero(datos: pd.DataFrame, columnas: Iterable[str]) -> pd.DataFrame:
    """Convierte columnas a número; lo que no se puede convertir queda como NaN."""
    datos = datos.copy()
    for columna in columnas:
        if columna in datos.columns:
            datos[columna] = pd.to_numeric(datos[columna], errors="coerce")
    return datos


def sin_faltantes(serie: pd.Series, codigos: set[int] = CODIGOS_FALTANTES) -> pd.Series:
    """Reemplaza los códigos de faltante del INEI por NaN."""
    return serie.where(~serie.isin(codigos))


def indicador(condicion: pd.Series, origen: pd.Series) -> pd.Series:
    """1/0 según la condición, pero NaN donde el dato de origen falta."""
    return condicion.astype(float).where(origen.notna())


def edad_valida(edad: pd.Series) -> pd.Series:
    """Edad en años; valores fuera de 0–110 se tratan como faltantes."""
    return edad.where(edad.between(0, 110))


def por_hogar(datos: pd.DataFrame, agregaciones: dict) -> pd.DataFrame:
    """Agrupa personas por hogar con `agregaciones` (estilo `named aggregation` de pandas)."""
    return datos.groupby(LLAVE_ANIO_HOGAR, as_index=False).agg(**agregaciones)


def cociente(numerador: pd.Series, denominador: pd.Series) -> pd.Series:
    """División que devuelve NaN cuando el denominador es 0."""
    return numerador / denominador.replace(0, np.nan)
