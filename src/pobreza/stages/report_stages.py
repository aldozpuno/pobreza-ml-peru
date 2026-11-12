"""Etapa 6: figuras y tablas para la tesis, y datos del dashboard.

Salida en `resultados/reportes/`:
    figuras/*.png         → figuras sin título interno, 300 ppp
    tablas_tesis.docx     → todas las tablas en formato EPG, numeradas
    datos/*.csv           → los mismos resultados en formato abierto
"""

from __future__ import annotations

import pandas as pd

from pobreza.config import Config
from pobreza.features import catalog
from pobreza.logging_utils import obtener
from pobreza.modeling.splits import generar_pliegues, tabla_pliegues
from pobreza.reporting import dashboard_export, docx_tables, figures_datos, figures_modelo
from pobreza.reporting import tables as tt
from pobreza.stages.storage import leer_json, leer_tabla

log = obtener("stages.reportes")


def _figuras(config: Config, resumen: dict, panel: pd.DataFrame) -> None:
    carpeta = config.rutas.reportes / "figuras"
    principal = resumen["estimador_principal"]
    figures_datos.incidencia_anual(leer_tabla(config, "incidencia_anual"), carpeta)
    figures_datos.incidencia_area(leer_tabla(config, "incidencia_area"), carpeta)
    figures_datos.hogares_repetidos(panel, carpeta)
    figures_datos.esquema_validacion(generar_pliegues(config), carpeta)
    figures_modelo.comparacion_modelos(leer_tabla(config, "comparacion_modelos"), principal,
                                       carpeta)
    tasa_base = resumen["metricas_prueba"]["tasa_real"] / 100
    figures_modelo.curvas(leer_tabla(config, "curva_roc"), leer_tabla(config, "curva_pr"),
                          tasa_base, carpeta)
    figures_modelo.calibracion(leer_tabla(config, "curva_calibracion"),
                               resumen["metricas_prueba"]["brier"], carpeta)
    figures_modelo.matriz_confusion(leer_tabla(config, "matriz_confusion"), carpeta)
    etiquetas = catalog.etiquetas(config)
    figures_modelo.importancia_shap(leer_tabla(config, "importancia_shap"), etiquetas, carpeta)
    figures_modelo.shap_periodos(leer_tabla(config, "shap_periodos"), etiquetas, carpeta)
    figures_modelo.sesgo_regional(leer_tabla(config, "sesgo_departamental"), carpeta)


def _tablas(config: Config, resumen: dict, panel: pd.DataFrame) -> list[tt.TablaTesis]:
    principal = resumen["estimador_principal"]
    sesgo = leer_tabla(config, "sesgo_departamental")[
        ["departamento", "hogares", "tasa_observada", "tasa_predicha", "sesgo_pp"]]
    return [
        tt.incidencia(leer_tabla(config, "incidencia_anual")),
        tt.panel(panel),
        tt.generico(catalog.diccionario(config), "Variables predictoras del modelo"),
        tt.generico(catalog.tabla_puente(config),
                    "Relación entre las teorías de la pobreza y las variables del modelo"),
        tt.generico(tabla_pliegues(generar_pliegues(config)),
                    "Diseño de la validación temporal con ventana expansiva"),
        tt.comparacion(leer_tabla(config, "comparacion_modelos")),
        tt.metricas_por_pliegue(leer_tabla(config, "metricas_pliegues"), principal),
        tt.prueba(leer_tabla(config, "metricas_prueba")),
        tt.generico(leer_tabla(config, "sensibilidad_alquiler")[
            ["estimador", "auc_roc", "auc_pr", "f1", "recall"]],
            "Sensibilidad del modelo al excluir el alquiler imputado (P106)", decimales=4),
        tt.generico(leer_tabla(config, "vif").head(15),
                    "Factor de inflación de la varianza de los predictores numéricos"),
        tt.generico(sesgo.rename(columns={
            "departamento": "Departamento", "hogares": "Hogares",
            "tasa_observada": "Observada (%)", "tasa_predicha": "Estimada (%)",
            "sesgo_pp": "Diferencia (pp)"}),
            "Pobreza observada y estimada por departamento en el conjunto de prueba",
            "Estimada: promedio de probabilidades calibradas, ponderado por FACTOR07 × "
            "MIEPERHO. " + tt.NOTA_ENAHO),
    ]


def reportes(config: Config, origen: str = "enaho") -> None:
    """Genera figuras, el .docx de tablas y los JSON del dashboard."""
    resumen = leer_json(config.rutas.reportes / "datos" / "resumen_evaluacion.json")
    panel = pd.read_csv(config.rutas.procesados / "resumen_panel.csv")
    _figuras(config, resumen, panel)
    docx_tables.escribir(_tablas(config, resumen, panel),
                         config.rutas.reportes / "tablas_tesis.docx")
    rutas = dashboard_export.exportar(config, origen)
    log.info("Reportes listos en %s; %d archivos para el dashboard", config.rutas.reportes,
             len(rutas))
