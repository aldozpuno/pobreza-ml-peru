"""Entrenamiento de un estimador en un pliegue y predicción con el modelo resultante.

Secuencia dentro de un pliegue:
    1. ajustar el pipeline con los años de entrenamiento
    2. calibrar las probabilidades con el año de calibración
    3. elegir el umbral con el año de calibración
    4. predecir el año de validación o de prueba
"""

from __future__ import annotations

from dataclasses import dataclass

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from pobreza.config import Config
from pobreza.modeling import estimators, thresholds
from pobreza.modeling.calibration import Calibrador
from pobreza.modeling.splits import Pliegue, particionar

COLUMNAS_SALIDA = ["anio", "conglome", "vivienda", "hogar", "departamento", "dominio",
                   "rural", "pobre", "peso_hogar", "peso_personas", "repetido"]


def preparar_X(datos: pd.DataFrame, predictores: list[str],
               categoricas: list[str]) -> pd.DataFrame:
    """Matriz de predictores: numéricas como float y categorías como texto."""
    X = datos[predictores].copy()
    for columna in predictores:
        if columna in categoricas:
            X[columna] = X[columna].astype("string").fillna("NA").astype(object)
        else:
            X[columna] = pd.to_numeric(X[columna], errors="coerce").astype(float)
    return X


@dataclass
class ModeloEntrenado:
    """Estimador ajustado con su calibrador, su umbral y la descripción del pliegue."""

    estimador: str
    pipeline: Pipeline
    calibrador: Calibrador
    umbral: float
    predictores: list[str]
    categoricas: list[str]
    pliegue: Pliegue

    def probabilidad(self, datos: pd.DataFrame) -> np.ndarray:
        X = preparar_X(datos, self.predictores, self.categoricas)
        return self.calibrador.transformar(self.pipeline.predict_proba(X)[:, 1])

    def clasificar(self, datos: pd.DataFrame) -> np.ndarray:
        return (self.probabilidad(datos) >= self.umbral).astype(int)

    def guardar(self, ruta) -> None:
        joblib.dump(self, ruta)


def entrenar(config: Config, hogares: pd.DataFrame, pliegue: Pliegue, estimador: str,
             predictores: list[str], categoricas: list[str]) -> ModeloEntrenado:
    """Ajusta, calibra y fija el umbral de un estimador en un pliegue."""
    entrenamiento, calibracion, _ = particionar(hogares, pliegue)
    numericas = [p for p in predictores if p not in categoricas]
    cats = [p for p in predictores if p in categoricas]
    pipeline = estimators.construir(estimador, config.modelo["estimadores"].get(estimador, {}),
                                    numericas, cats, config.semilla)

    ajuste = {}
    if config.modelo["pesos"].get("entrenar_con_factor") and estimador != "knn":
        ajuste["modelo__sample_weight"] = entrenamiento["peso_hogar"].to_numpy()
    pipeline.fit(preparar_X(entrenamiento, predictores, cats), entrenamiento["pobre"], **ajuste)

    X_cal = preparar_X(calibracion, predictores, cats)
    prob_cal = pipeline.predict_proba(X_cal)[:, 1]
    calibrador = Calibrador(config.modelo.get("calibracion", "isotonica"))
    calibrador.ajustar(prob_cal, calibracion["pobre"].to_numpy(),
                       calibracion["peso_hogar"].to_numpy())
    criterio = config.modelo["umbral"]
    umbral = thresholds.elegir(calibracion["pobre"].to_numpy(),
                               calibrador.transformar(prob_cal), criterio["criterio"],
                               float(criterio.get("recall_minimo", 0.8)),
                               calibracion["peso_personas"].to_numpy())
    return ModeloEntrenado(estimador, pipeline, calibrador, umbral, predictores, cats, pliegue)


def predecir(modelo: ModeloEntrenado, datos: pd.DataFrame) -> pd.DataFrame:
    """Predicciones por hogar con las columnas necesarias para evaluar y reportar."""
    salida = datos[[c for c in COLUMNAS_SALIDA if c in datos.columns]].copy()
    salida["prob"] = modelo.probabilidad(datos)
    salida["pred"] = (salida["prob"] >= modelo.umbral).astype(int)
    salida["estimador"] = modelo.estimador
    salida["pliegue"] = modelo.pliegue.nombre
    return salida
