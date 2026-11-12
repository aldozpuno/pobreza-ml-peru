"""Exporta los resultados como JSON para el dashboard (`dashboard/public/data/`).

Un archivo por página del dashboard. `meta.json` indica si los datos vienen de la
ENAHO o de la base sintética de prueba, para que el dashboard lo avise.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from pobreza import __version__
from pobreza.config import Config
from pobreza.evaluation.regional import DEPARTAMENTOS
from pobreza.features import catalog
from pobreza.modeling.splits import generar_pliegues, tabla_pliegues
from pobreza.stages.storage import guardar_json, leer_json, leer_tabla, registros


def _meta(config: Config, origen: str, resumen: dict) -> dict:
    return {"generado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "origen": origen, "version": __version__, "anios": config.anios,
            "anio_prueba": config.anio_prueba, "estimador": resumen["estimador_principal"],
            "umbral": resumen["umbral"], "pliegue_final": resumen["pliegue_final"]}


def _resumen(config: Config, resumen: dict, panel: pd.DataFrame) -> dict:
    anual = leer_tabla(config, "incidencia_anual")
    prueba = resumen["metricas_prueba"]
    ultimo = anual.iloc[-1]
    return {
        "kpis": {
            "tasa_reproducida": ultimo["tasa_personas"],
            "tasa_oficial": ultimo["tasa_oficial_inei"],
            "tasa_predicha": prueba["tasa_predicha"],
            "tasa_clasificados": prueba["tasa_clasificados"],
            "auc_roc": prueba["auc_roc"], "auc_pr": prueba["auc_pr"],
            "recall": prueba["recall"], "precision": prueba["precision"],
            "hogares_total": int(panel["hogares"].sum()),
            "pct_repetidos": float(100 * panel["repetidos"].sum() / panel["hogares"].sum()),
        },
        "serie_anual": registros(anual),
        "serie_area": registros(leer_tabla(config, "incidencia_area")),
    }


def _territorio(config: Config) -> dict:
    por_dep = leer_tabla(config, "incidencia_departamento")
    por_dep["nombre"] = por_dep["departamento"].map(DEPARTAMENTOS)
    return {"incidencia": registros(por_dep[["anio", "departamento", "nombre",
                                             "tasa_personas", "hogares_muestra"]]),
            "sesgo_prueba": registros(leer_tabla(config, "sesgo_departamental"))}


def _modelo(config: Config, resumen: dict) -> dict:
    principal = resumen["estimador_principal"]
    pliegues = leer_tabla(config, "metricas_pliegues")
    return {
        "comparacion": registros(leer_tabla(config, "comparacion_modelos")),
        "pliegues": registros(pliegues[pliegues["estimador"] == principal]),
        "prueba": registros(leer_tabla(config, "metricas_prueba")),
        "sensibilidad": registros(leer_tabla(config, "sensibilidad_alquiler")),
        "confusion": registros(leer_tabla(config, "matriz_confusion")),
        "calibracion": registros(leer_tabla(config, "curva_calibracion")),
        "roc": registros(leer_tabla(config, "curva_roc")),
        "pr": registros(leer_tabla(config, "curva_pr")),
        "sesgo_regional": resumen["sesgo_regional"],
    }


def _explicabilidad(config: Config) -> dict:
    importancia = leer_tabla(config, "importancia_shap")
    dic = catalog.diccionario(config).set_index("Variable")
    importancia["etiqueta"] = importancia["variable"].map(dic["Etiqueta"])
    importancia["definicion"] = importancia["variable"].map(dic["Definición"])
    importancia["teoria"] = importancia["variable"].map(dic["Teoría"])
    importancia["signo_esperado"] = importancia["variable"].map(dic["Signo esperado"])
    etiquetas = catalog.etiquetas(config)
    periodos = leer_tabla(config, "shap_periodos")
    periodos["etiqueta"] = periodos["variable"].map(etiquetas)
    muestra = leer_tabla(config, "shap_muestra")
    muestra["etiqueta"] = muestra["variable"].map(etiquetas)
    return {"importancia": registros(importancia), "periodos": registros(periodos),
            "muestra": registros(muestra, 3)}


def _metodologia(config: Config, panel: pd.DataFrame) -> dict:
    return {
        "pliegues": registros(tabla_pliegues(generar_pliegues(config))),
        "variables": registros(catalog.diccionario(config)),
        "puente": registros(catalog.tabla_puente(config)),
        "fuga": config.fuga_de_datos,
        "panel": registros(panel),
        "vif": registros(leer_tabla(config, "vif").head(15)),
    }


def exportar(config: Config, origen: str = "enaho") -> list[Path]:
    """Escribe los seis JSON del dashboard y devuelve sus rutas."""
    carpeta = config.rutas.dashboard
    resumen = leer_json(config.rutas.reportes / "datos" / "resumen_evaluacion.json")
    panel = pd.read_csv(config.rutas.procesados / "resumen_panel.csv")
    archivos = {
        "meta": _meta(config, origen, resumen),
        "resumen": _resumen(config, resumen, panel),
        "territorio": _territorio(config),
        "modelo": _modelo(config, resumen),
        "explicabilidad": _explicabilidad(config),
        "metodologia": _metodologia(config, panel),
    }
    return [guardar_json(carpeta / f"{nombre}.json", datos) for nombre, datos in archivos.items()]
