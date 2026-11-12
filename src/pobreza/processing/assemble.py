"""Ensamblado: une los módulos de cada año y apila los años en una sola base.

La Sumaria es la tabla base (un hogar con encuesta completa por fila). Los demás
módulos se unen por (anio, conglome, vivienda, hogar) con `left join`, de modo que
ningún hogar de la Sumaria se pierde aunque le falte un módulo.
"""

from __future__ import annotations

from collections.abc import Callable

import pandas as pd

from pobreza.config import Config
from pobreza.data.readers import leer_modulo
from pobreza.features.derived import agregar_derivadas
from pobreza.logging_utils import obtener
from pobreza.processing import (educacion, empleo, miembros, panel, programas, salud,
                                sumaria, vivienda)
from pobreza.processing.keys import LLAVE_ANIO_HOGAR

log = obtener("processing.assemble")

PROCESADORES: dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "vivienda": vivienda.procesar,
    "miembros": miembros.procesar,
    "educacion": educacion.procesar,
    "salud": salud.procesar,
    "empleo": empleo.procesar,
    "programas": programas.procesar,
}

LectorModulo = Callable[[Config, int, str], pd.DataFrame]


def construir_anio(config: Config, anio: int, leer: LectorModulo = leer_modulo) -> pd.DataFrame:
    """Base de hogares de un año: Sumaria + el resto de módulos."""
    base = sumaria.procesar(leer(config, anio, "sumaria"))
    for nombre, procesar in PROCESADORES.items():
        tabla = procesar(leer(config, anio, nombre))
        base = base.merge(tabla, on=LLAVE_ANIO_HOGAR, how="left", validate="one_to_one")
        sin_dato = base[tabla.columns.difference(LLAVE_ANIO_HOGAR)].isna().all(axis=1).mean()
        log.info("%s %-9s unido | hogares sin dato del módulo: %.1f %%", anio, nombre,
                 100 * sin_dato)
    return base


def anio_en_cache(config: Config, anio: int, leer: LectorModulo = leer_modulo) -> pd.DataFrame:
    """Base de un año desde `datos/intermedios/` si ya se construyó; si no, la construye.

    Para reconstruir un año (por ejemplo, tras cambiar un procesador), borre su archivo.
    """
    ruta = config.rutas.intermedios / f"hogares_{anio}.parquet"
    if ruta.exists():
        log.info("%s tomado de %s", anio, ruta.name)
        return pd.read_parquet(ruta)
    base = construir_anio(config, anio, leer)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    base.to_parquet(ruta, index=False)
    return base


def construir(config: Config, leer: LectorModulo = leer_modulo) -> pd.DataFrame:
    """Base apilada de todos los años, con variables derivadas y marca de repetidos."""
    anios = [anio_en_cache(config, anio, leer) for anio in config.anios]
    hogares = pd.concat(anios, ignore_index=True)
    hogares = agregar_derivadas(hogares)
    hogares = panel.enlazar_entre_anios(hogares)
    verificar_estabilidad(config, hogares)
    log.info("Base apilada: %d observaciones hogar-año, %d hogares distintos por llave",
             len(hogares), panel.hogares_distintos(hogares))
    return hogares


def verificar_estabilidad(config: Config, hogares: pd.DataFrame) -> list[tuple[int, str]]:
    """Avisa de predictores constantes o vacíos en algún año (p. ej., una variable que
    el INEI dejó de publicar). Un predictor así engaña al modelo en ese año."""
    problemas = []
    for variable in config.variables_activas():
        if variable not in hogares or variable == "covid":  # constante por año a propósito
            continue
        por_anio = hogares.groupby("anio")[variable].agg(["nunique", "count"])
        for anio, fila in por_anio.iterrows():
            if fila["count"] == 0 or fila["nunique"] <= 1:
                problemas.append((int(anio), variable))
                log.warning("%s: '%s' es constante o vacía; revise el módulo de origen",
                            anio, variable)
    return problemas


def guardar(config: Config, hogares: pd.DataFrame) -> None:
    """Escribe la base y el resumen de hogares repetidos en `datos/procesados/`."""
    config.rutas.asegurar()
    hogares.to_parquet(config.rutas.procesados / "hogares.parquet", index=False)
    panel.resumen(hogares).to_csv(config.rutas.procesados / "resumen_panel.csv", index=False)


def cargar(config: Config) -> pd.DataFrame:
    """Lee la base construida; falla con instrucciones si aún no existe."""
    ruta = config.rutas.procesados / "hogares.parquet"
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta}. Ejecute primero: pobreza construir")
    return pd.read_parquet(ruta)
