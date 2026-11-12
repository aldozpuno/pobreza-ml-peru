"""Explicabilidad del modelo principal con valores SHAP (solo para XGBoost).

Los valores SHAP se calculan sobre el margen del clasificador (log-odds), antes de la
calibración isotónica, que es monótona y no cambia el orden de los hogares. Las
categorías codificadas en one-hot se vuelven a sumar en su variable de origen.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import shap

from pobreza.modeling.training import ModeloEntrenado, preparar_X


def _variable_origen(columnas: list[str], predictores: list[str]) -> list[str]:
    origen = []
    for columna in columnas:
        candidatas = [p for p in predictores if columna == p or columna.startswith(f"{p}_")]
        origen.append(max(candidatas, key=len) if candidatas else columna)
    return origen


def valores(modelo: ModeloEntrenado, datos: pd.DataFrame, n: int, semilla: int
            ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(SHAP por variable de origen, valores originales de esas variables) para `n` hogares."""
    if modelo.estimador != "xgboost":
        raise ValueError("La explicación SHAP está implementada para XGBoost")
    muestra = datos.sample(min(n, len(datos)), random_state=semilla)
    X = preparar_X(muestra, modelo.predictores, modelo.categoricas)
    preprocesar = modelo.pipeline.named_steps["preprocesar"]
    Xt = preprocesar.transform(X)
    columnas = list(preprocesar.get_feature_names_out())
    explicador = shap.TreeExplainer(modelo.pipeline.named_steps["modelo"])
    matriz = np.asarray(explicador.shap_values(Xt))
    por_columna = pd.DataFrame(matriz, columns=columnas, index=X.index)
    origen = _variable_origen(columnas, modelo.predictores)
    por_variable = por_columna.T.groupby(origen, sort=False).sum().T
    return por_variable, X


def importancia(shap_var: pd.DataFrame, X: pd.DataFrame,
                categoricas: tuple[str, ...] = ()) -> pd.DataFrame:
    """Importancia global (media de |SHAP|) y dirección del efecto de cada variable.

    Las variables categóricas (códigos sin orden) no tienen dirección: se marcan "±".
    """
    filas = []
    for variable in shap_var.columns:
        numerica = variable in X and variable not in categoricas
        valores_var = pd.to_numeric(X[variable], errors="coerce") if numerica else None
        direccion = np.nan
        if valores_var is not None and valores_var.notna().sum() > 10 and valores_var.std() > 0:
            direccion = float(pd.Series(valores_var).corr(shap_var[variable], method="spearman"))
        filas.append({"variable": variable,
                      "importancia": float(shap_var[variable].abs().mean()),
                      "direccion": direccion})
    tabla = pd.DataFrame(filas).sort_values("importancia", ascending=False)
    tabla["signo_observado"] = np.select([tabla["direccion"] > 0.1, tabla["direccion"] < -0.1],
                                         ["+", "-"], "±")
    return tabla.reset_index(drop=True)


def comparar_periodos(modelo: ModeloEntrenado, hogares: pd.DataFrame, antes: list[int],
                      despues: list[int], n: int, semilla: int) -> pd.DataFrame:
    """Importancia SHAP antes y después de la COVID-19 con el mismo modelo."""
    tablas = []
    for etiqueta, anios in (("antes", antes), ("despues", despues)):
        subconjunto = hogares[hogares["anio"].isin(anios)]
        shap_var, X = valores(modelo, subconjunto, n, semilla)
        tablas.append(importancia(shap_var, X, tuple(modelo.categoricas))[["variable", "importancia"]]
                      .rename(columns={"importancia": f"importancia_{etiqueta}"}))
    tabla = tablas[0].merge(tablas[1], on="variable")
    tabla["cambio"] = tabla["importancia_despues"] - tabla["importancia_antes"]
    return tabla.sort_values("importancia_despues", ascending=False).reset_index(drop=True)
