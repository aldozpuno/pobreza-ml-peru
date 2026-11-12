"""Etapas de datos: descarga, construcción de la base y medición de la pobreza."""

from __future__ import annotations

import pandas as pd

from pobreza.config import Config
from pobreza.data.download import descargar_todo
from pobreza.data.readers import leer_modulo
from pobreza.logging_utils import obtener
from pobreza.measurement import poverty
from pobreza.processing import assemble
from pobreza.stages.storage import guardar_tabla

log = obtener("stages.datos")


def descarga(config: Config) -> None:
    """Etapa 1: baja los zips del INEI (o usa los que ya estén en `datos/crudos`)."""
    rutas = descargar_todo(config)
    log.info("Descarga lista: %d archivos", len(rutas))


def construccion(config: Config, leer=leer_modulo) -> pd.DataFrame:
    """Etapa 2: base apilada de hogares con identificadores y marca de repetidos."""
    hogares = assemble.construir(config, leer)
    assemble.guardar(config, hogares)
    return hogares


def medicion(config: Config, hogares: pd.DataFrame | None = None,
             estricto: bool = True) -> pd.DataFrame:
    """Etapa 3: incidencia anual y por departamento; valida la variable objetivo."""
    hogares = assemble.cargar(config) if hogares is None else hogares
    anual = poverty.validar(config, poverty.incidencia(hogares, ["anio"]), estricto=estricto)
    guardar_tabla(config, "incidencia_anual", anual)
    guardar_tabla(config, "incidencia_departamento",
                  poverty.incidencia(hogares, ["anio", "departamento"]))
    guardar_tabla(config, "incidencia_area",
                  poverty.incidencia(hogares, ["anio", "rural"]))
    return anual
