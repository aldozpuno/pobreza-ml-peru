"""Diagnóstico de multicolinealidad (VIF) de los predictores numéricos.

El VIF se informa para la tesis; no elimina variables automáticamente, porque los
árboles de XGBoost toleran la colinealidad y la decisión debe justificarse por escrito.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor


def vif(datos: pd.DataFrame, columnas: list[str], muestra: int = 20000,
        semilla: int = 42) -> pd.DataFrame:
    """Tabla con el VIF de cada variable, ordenada de mayor a menor."""
    matriz = datos[columnas].apply(pd.to_numeric, errors="coerce")
    matriz = matriz.fillna(matriz.median())
    matriz = matriz.loc[:, matriz.std() > 0]
    if len(matriz) > muestra:
        matriz = matriz.sample(muestra, random_state=semilla)
    valores = np.column_stack([np.ones(len(matriz)), matriz.to_numpy(dtype=float)])
    with np.errstate(divide="ignore", invalid="ignore"):
        resultado = [variance_inflation_factor(valores, i + 1) for i in range(matriz.shape[1])]
    tabla = pd.DataFrame({"Variable": matriz.columns, "VIF": resultado})
    tabla["Diagnóstico"] = np.select(
        [tabla["VIF"] >= 10, tabla["VIF"] >= 5], ["Alta (≥ 10)", "Moderada (5–10)"], "Baja (< 5)")
    return tabla.sort_values("VIF", ascending=False).reset_index(drop=True)
