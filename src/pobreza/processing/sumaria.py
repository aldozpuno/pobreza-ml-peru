"""Módulo 34 (Sumaria): variable objetivo, pesos y ubicación del hogar.

La Sumaria trae la clasificación oficial de pobreza del INEI:
    POBREZA = 1 pobre extremo, 2 pobre no extremo, 3 no pobre.
La variable objetivo es `pobre` = 1 si POBREZA es 1 o 2 (igual que el Taller 6 del asesor).

Pesos:
    peso_hogar    = FACTOR07              → representa hogares
    peso_personas = FACTOR07 × MIEPERHO   → representa personas (incidencia oficial)
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero
from pobreza.processing.keys import LLAVE_ANIO_HOGAR, verificar_unicidad

ESTRATOS_RURALES = {6, 7, 8}


def procesar(sumaria: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con objetivo, pesos y variables territoriales."""
    datos = a_numero(sumaria, ["pobreza", "mieperho", "totmieho", "factor07", "dominio",
                               "estrato", "linea", "linpe", "gashog2d"])
    datos = datos[datos["pobreza"].isin([1, 2, 3]) & (datos["mieperho"] > 0)
                  & (datos["factor07"] > 0)].copy()

    datos["pobre"] = datos["pobreza"].isin([1, 2]).astype(int)
    datos["pobre_extremo"] = (datos["pobreza"] == 1).astype(int)
    datos["peso_hogar"] = datos["factor07"]
    datos["peso_personas"] = datos["factor07"] * datos["mieperho"]
    datos["departamento"] = datos["ubigeo"].str[:2]
    datos["rural"] = datos["estrato"].isin(ESTRATOS_RURALES).astype(int)
    datos["covid"] = (datos["anio"] == 2020).astype(int)

    columnas = [*LLAVE_ANIO_HOGAR, "ubigeo", "departamento", "dominio", "estrato", "rural",
                "covid", "mieperho", "pobreza", "pobre", "pobre_extremo", "factor07",
                "peso_hogar", "peso_personas", "linea", "gashog2d"]
    return verificar_unicidad(datos[columnas], LLAVE_ANIO_HOGAR, "sumaria")
