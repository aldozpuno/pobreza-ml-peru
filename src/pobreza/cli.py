"""Interfaz de línea de comandos.

    pobreza descargar    # etapa 1: zips del INEI
    pobreza construir    # etapa 2: base apilada de hogares
    pobreza medir        # etapa 3: incidencia y validación contra el INEI
    pobreza entrenar     # etapa 4: modelos por pliegue
    pobreza evaluar      # etapa 5: métricas, sesgo regional, SHAP
    pobreza reportar     # etapa 6: figuras, tablas EPG y dashboard
    pobreza todo         # las seis etapas en orden

Opciones comunes: --raiz (carpeta del proyecto), --no-estricto (no detener si la tasa
reproducida difiere del INEI; solo para pruebas).
"""

from __future__ import annotations

import argparse

from pobreza.config import cargar_config
from pobreza.logging_utils import configurar
from pobreza.stages import data_stages, eval_stages, model_stages, report_stages

ETAPAS = ["descargar", "construir", "medir", "entrenar", "evaluar", "reportar"]


def ejecutar(etapa: str, raiz: str | None = None, estricto: bool = True,
             origen: str = "enaho") -> None:
    config = cargar_config(raiz)
    config.rutas.asegurar()
    configurar(config.rutas.reportes / "pipeline.log")
    pasos = ETAPAS if etapa == "todo" else [etapa]
    for paso in pasos:
        if paso == "descargar":
            data_stages.descarga(config)
        elif paso == "construir":
            data_stages.construccion(config)
        elif paso == "medir":
            data_stages.medicion(config, estricto=estricto)
        elif paso == "entrenar":
            model_stages.entrenamiento(config)
        elif paso == "evaluar":
            eval_stages.evaluacion(config)
        elif paso == "reportar":
            report_stages.reportes(config, origen)


def main(argv: list[str] | None = None) -> None:
    analizador = argparse.ArgumentParser(prog="pobreza", description=__doc__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter)
    analizador.add_argument("etapa", choices=[*ETAPAS, "todo"])
    analizador.add_argument("--raiz", default=None, help="carpeta raíz del proyecto")
    analizador.add_argument("--no-estricto", action="store_true",
                            help="no detener si la tasa difiere del INEI")
    analizador.add_argument("--origen", default="enaho", choices=["enaho", "sintetico"],
                            help="origen de los datos que se anuncia en el dashboard")
    argumentos = analizador.parse_args(argv)
    ejecutar(argumentos.etapa, argumentos.raiz, not argumentos.no_estricto, argumentos.origen)


if __name__ == "__main__":
    main()
