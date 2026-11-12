"""Etapa 4: entrenamiento de todos los estimadores en todos los pliegues.

Guarda en `resultados/modelos/`:
    predicciones.parquet  → una fila por hogar evaluado, estimador y pliegue
    umbrales.csv          → umbral elegido en cada pliegue (año de calibración)
    modelo_final.joblib   → estimador principal entrenado para la prueba final
"""

from __future__ import annotations

import joblib
import pandas as pd

from pobreza.config import Config
from pobreza.features import catalog
from pobreza.logging_utils import obtener
from pobreza.modeling.splits import Pliegue, generar_pliegues, particionar
from pobreza.modeling.training import ModeloEntrenado, entrenar, predecir
from pobreza.processing import assemble

log = obtener("stages.modelo")
SUFIJO_SIN_ALQUILER = "_sin_alquiler"


def _correr(config: Config, hogares: pd.DataFrame, pliegue: Pliegue, estimador: str,
            predictores: list[str], categoricas: list[str], etiqueta: str
            ) -> tuple[ModeloEntrenado, pd.DataFrame]:
    modelo = entrenar(config, hogares, pliegue, estimador, predictores, categoricas)
    _, _, evaluacion = particionar(hogares, pliegue)
    predicciones = predecir(modelo, evaluacion).assign(estimador=etiqueta)
    log.info("%-26s %-13s umbral %.3f", etiqueta, pliegue.nombre, modelo.umbral)
    return modelo, predicciones


def entrenamiento(config: Config, hogares: pd.DataFrame | None = None) -> pd.DataFrame:
    """Entrena cada estimador en cada pliegue y el análisis de sensibilidad."""
    hogares = assemble.cargar(config) if hogares is None else hogares
    predictores = catalog.predictores(config)
    categoricas = catalog.categoricas(config)
    pliegues = generar_pliegues(config)
    ajustes = config.modelo["estimadores"]
    principal = ajustes["principal"]
    for pliegue in pliegues:
        log.info(pliegue.describir())

    tablas, umbrales = [], []
    for estimador in ajustes["comparar"]:
        for pliegue in pliegues:
            modelo, pred = _correr(config, hogares, pliegue, estimador, predictores,
                                   categoricas, estimador)
            tablas.append(pred)
            umbrales.append({"estimador": estimador, "pliegue": pliegue.nombre,
                             "umbral": modelo.umbral})
            if estimador == principal and pliegue.es_prueba_final:
                _guardar_final(config, modelo)

    if config.modelo.get("sensibilidad", {}).get("sin_alquiler_imputado"):
        sin_alquiler = [p for p in predictores if p != "alquiler_imputado"]
        final = next(p for p in pliegues if p.es_prueba_final)
        _, pred = _correr(config, hogares, final, principal, sin_alquiler, categoricas,
                          principal + SUFIJO_SIN_ALQUILER)
        tablas.append(pred)

    predicciones = pd.concat(tablas, ignore_index=True)
    config.rutas.modelos.mkdir(parents=True, exist_ok=True)
    predicciones.to_parquet(config.rutas.modelos / "predicciones.parquet", index=False)
    pd.DataFrame(umbrales).to_csv(config.rutas.modelos / "umbrales.csv", index=False)
    return predicciones


def _guardar_final(config: Config, modelo: ModeloEntrenado) -> None:
    config.rutas.modelos.mkdir(parents=True, exist_ok=True)
    modelo.guardar(config.rutas.modelos / "modelo_final.joblib")


def cargar_final(config: Config) -> ModeloEntrenado:
    return joblib.load(config.rutas.modelos / "modelo_final.joblib")


def cargar_predicciones(config: Config) -> pd.DataFrame:
    ruta = config.rutas.modelos / "predicciones.parquet"
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}. Ejecute primero: pobreza entrenar")
    return pd.read_parquet(ruta)
