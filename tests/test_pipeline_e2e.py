"""Prueba de punta a punta: las seis etapas sobre datos sintéticos (sin descarga)."""

import json

import pandas as pd

from pobreza.stages import data_stages, eval_stages, model_stages, report_stages


def test_pipeline_completo(proyecto):
    config = proyecto
    config.rutas.asegurar()

    hogares = data_stages.construccion(config)
    assert {"conglome", "vivienda", "hogar", "pobre", "repetido"} <= set(hogares.columns)
    assert hogares["repetido"].sum() > 0

    anual = data_stages.medicion(config, hogares, estricto=False)
    assert list(anual["anio"]) == config.anios

    predicciones = model_stages.entrenamiento(config, hogares)
    assert set(predicciones["estimador"]) >= {"xgboost", "logit", "xgboost_sin_alquiler"}

    resumen = eval_stages.evaluacion(config)
    assert resumen["metricas_prueba"]["auc_roc"] > 0.6

    report_stages.reportes(config, origen="sintetico")
    figuras = list((config.rutas.reportes / "figuras").glob("*.png"))
    assert len(figuras) == 11
    assert (config.rutas.reportes / "tablas_tesis.docx").exists()
    meta = json.loads((config.rutas.dashboard / "meta.json").read_text(encoding="utf-8"))
    assert meta["origen"] == "sintetico"
    prueba = pd.read_csv(config.rutas.reportes / "datos" / "metricas_prueba.csv")
    assert "Solo hogares no vistos antes" in set(prueba["Variante"])
