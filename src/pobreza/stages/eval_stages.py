"""Etapa 5: evaluación del desempeño, del sesgo territorial y explicabilidad.

Responde directamente a las observaciones del asesor:
    - métricas de prueba con y sin hogares repetidos (APPEND frente a panel)
    - métricas sin ponderar y ponderadas por el factor de expansión
    - sensibilidad sin el alquiler imputado (P106)
"""

from __future__ import annotations

import pandas as pd

from pobreza.config import Config
from pobreza.evaluation import explain, inference, metrics, regional
from pobreza.features import catalog, collinearity
from pobreza.logging_utils import obtener
from pobreza.processing import assemble
from pobreza.stages.model_stages import (SUFIJO_SIN_ALQUILER, cargar_final,
                                         cargar_predicciones)
from pobreza.stages.storage import carpeta_datos, guardar_json, guardar_tabla

log = obtener("stages.evaluacion")
PRUEBA = "Prueba final"


def _metricas_prueba(prueba: pd.DataFrame) -> pd.DataFrame:
    variantes = {
        "Todos los hogares, sin ponderar": (prueba, False),
        "Todos los hogares, ponderado (FACTOR07)": (prueba, True),
        "Solo hogares no vistos antes": (prueba[prueba["repetido"] == 0], False),
        "Solo hogares repetidos": (prueba[prueba["repetido"] == 1], False),
    }
    return pd.DataFrame([{"Variante": nombre, **metrics.metricas(datos, ponderar)}
                         for nombre, (datos, ponderar) in variantes.items() if len(datos)])


def evaluacion(config: Config) -> dict:
    """Calcula y guarda todas las tablas de evaluación; devuelve un resumen."""
    pred = cargar_predicciones(config)
    principal = config.modelo["estimadores"]["principal"]
    validacion = pred[pred["pliegue"] != PRUEBA]
    prueba_todos = pred[pred["pliegue"] == PRUEBA]
    prueba = prueba_todos[prueba_todos["estimador"] == principal]

    por_pliegue = metrics.tabla(pred, ["estimador", "pliegue"])
    guardar_tabla(config, "metricas_pliegues", por_pliegue)
    comparacion = (metrics.tabla(validacion, ["estimador", "pliegue"])
                   .drop(columns="pliegue").groupby("estimador", sort=False).mean()
                   .reset_index().sort_values("auc_pr", ascending=False))
    guardar_tabla(config, "comparacion_modelos", comparacion)
    guardar_tabla(config, "metricas_prueba", _metricas_prueba(prueba))
    guardar_tabla(config, "sensibilidad_alquiler",
                  metrics.tabla(prueba_todos[prueba_todos["estimador"].isin(
                      [principal, principal + SUFIJO_SIN_ALQUILER])], ["estimador"]))
    guardar_tabla(config, "prueba_delong", inference.comparar_con_principal(prueba_todos, principal))
    guardar_tabla(config, "matriz_confusion", metrics.matriz_confusion(prueba))
    guardar_tabla(config, "curva_calibracion", metrics.curva_calibracion(prueba))
    for nombre, curva in metrics.curvas(prueba).items():
        guardar_tabla(config, f"curva_{nombre}", curva)

    sesgo = regional.sesgo_por_departamento(prueba)
    guardar_tabla(config, "sesgo_departamental", sesgo)

    resumen = {"estimador_principal": principal,
               "metricas_prueba": metrics.metricas(prueba),
               "sesgo_regional": regional.resumen_sesgo(sesgo)}
    resumen.update(_explicabilidad(config))
    guardar_json(carpeta_datos(config) / "resumen_evaluacion.json", resumen)
    log.info("Prueba %s: AUC-ROC %.3f | AUC-PR %.3f | recall %.3f", config.anio_prueba,
             resumen["metricas_prueba"]["auc_roc"], resumen["metricas_prueba"]["auc_pr"],
             resumen["metricas_prueba"]["recall"])
    return resumen


def _explicabilidad(config: Config) -> dict:
    """SHAP global, por periodo y muestra para el gráfico de enjambre; VIF."""
    hogares = assemble.cargar(config)
    modelo = cargar_final(config)
    ajustes = config.modelo["explicabilidad"]
    n, semilla = int(ajustes["muestra_shap"]), config.semilla
    prueba = hogares[hogares["anio"] == config.anio_prueba]

    shap_var, X = explain.valores(modelo, prueba, n, semilla)
    importancia = explain.importancia(shap_var, X, tuple(modelo.categoricas))
    guardar_tabla(config, "importancia_shap", importancia)
    guardar_tabla(config, "shap_periodos", explain.comparar_periodos(
        modelo, hogares, ajustes["periodo_pre"], ajustes["periodo_post"], n, semilla))
    principales = importancia["variable"].head(12).tolist()
    muestra = shap_var[principales].head(400).melt(var_name="variable", value_name="shap")
    muestra["valor"] = X[principales].head(400).apply(
        lambda s: pd.to_numeric(s, errors="coerce").rank(pct=True)).melt()["value"].to_numpy()
    guardar_tabla(config, "shap_muestra", muestra)

    numericas = [p for p in catalog.predictores(config) if p not in catalog.categoricas(config)]
    guardar_tabla(config, "vif", collinearity.vif(hogares, numericas, semilla=semilla))
    return {"umbral": modelo.umbral, "predictores": modelo.predictores,
            "pliegue_final": modelo.pliegue.describir()}
