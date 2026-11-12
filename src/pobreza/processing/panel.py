"""Hogares que aparecen en más de un año (observación del asesor sobre el APPEND).

La ENAHO vuelve a entrevistar a una parte de su muestra en años consecutivos. Aquí se
identifica a esos hogares por dos vías independientes y se informa cuánto coinciden:

1. `entrevistado_anio_anterior`: la pregunta PANEL del módulo 100 (1 = Sí).
2. `visto_antes`: la llave CONGLOME-VIVIENDA-HOGAR ya apareció en un año anterior.

Ninguna de las dos se da por buena sin verificar: el resumen muestra cuántos hogares
marca cada una y cuántos marcan ambas.
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.keys import id_hogar


def enlazar_entre_anios(hogares: pd.DataFrame) -> pd.DataFrame:
    """Agrega `visto_anio_anterior`, `visto_antes` y `repetido` a la base apilada."""
    datos = hogares.copy()
    datos["id_hogar"] = id_hogar(datos)
    primera_vez = datos.groupby("id_hogar")["anio"].transform("min")
    datos["visto_antes"] = (datos["anio"] > primera_vez).astype(int)
    siguiente = (datos[["id_hogar", "anio"]].drop_duplicates()
                 .assign(anio=lambda d: d["anio"] + 1, visto_anio_anterior=1))
    datos = datos.merge(siguiente, on=["id_hogar", "anio"], how="left")
    datos["visto_anio_anterior"] = datos["visto_anio_anterior"].fillna(0).astype(int)
    pregunta = datos.get("entrevistado_anio_anterior", pd.Series(0, index=datos.index))
    datos["repetido"] = ((pregunta.fillna(0) == 1) | (datos["visto_antes"] == 1)).astype(int)
    return datos


def resumen(hogares: pd.DataFrame) -> pd.DataFrame:
    """Tabla por año: hogares, cuántos se repiten por cada criterio y su coincidencia."""
    datos = hogares.copy()
    datos["pregunta_panel"] = datos["entrevistado_anio_anterior"].fillna(0).eq(1).astype(int)
    datos["ambos"] = (datos["pregunta_panel"] & datos["visto_anio_anterior"]).astype(int)
    tabla = datos.groupby("anio").agg(
        hogares=("id_hogar", "size"),
        pregunta_panel=("pregunta_panel", "sum"),
        llave_anio_anterior=("visto_anio_anterior", "sum"),
        llave_cualquier_anio=("visto_antes", "sum"),
        ambos_criterios=("ambos", "sum"),
        repetidos=("repetido", "sum"),
    ).reset_index()
    tabla["pct_repetidos"] = 100 * tabla["repetidos"] / tabla["hogares"]
    return tabla


def hogares_distintos(hogares: pd.DataFrame) -> int:
    """Número de hogares distintos según la llave (cota inferior si hay recodificaciones)."""
    return int(id_hogar(hogares).nunique())
