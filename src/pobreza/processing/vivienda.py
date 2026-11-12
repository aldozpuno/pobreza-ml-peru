"""Módulo 100 (Características de la vivienda y del hogar).

Códigos según el diccionario ENAHO del INEI:
    P101 tipo de vivienda · P102 material de paredes · P103 material de pisos (6 = tierra)
    P104 habitaciones · P106 alquiler mensual estimado (S/) · P110 procedencia del agua
    P111A desagüe · P1121 alumbrado eléctrico · P1135/P1136/P1139 carbón, leña, bosta
    P1142 celular · P1143 TV cable · P1144 internet
    PANEL "¿El hogar fue entrevistado el año pasado?" (1 Sí, 2 No)
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero, indicador, sin_faltantes
from pobreza.processing.keys import LLAVE_ANIO_HOGAR, verificar_unicidad

PAREDES_PRECARIAS = {5, 6, 7, 8, 9}   # quincha, piedra con barro, madera, triplay/estera, otro
AGUA_RED = {1, 2}                      # red pública dentro o fuera de la vivienda
DESAGUE_RED = {1, 2}


def procesar(vivienda: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con las características de la vivienda y sus servicios."""
    datos = a_numero(vivienda, [c for c in vivienda.columns if c.startswith("p") or c == "panel"])
    salida = datos[LLAVE_ANIO_HOGAR].copy()

    salida["tipo_vivienda"] = datos["p101"]
    salida["pared_precaria"] = indicador(datos["p102"].isin(PAREDES_PRECARIAS), datos["p102"])
    salida["piso_tierra"] = indicador(datos["p103"] == 6, datos["p103"])
    habitaciones = sin_faltantes(datos["p104"])
    salida["habitaciones"] = habitaciones.where(habitaciones > 0)
    salida["alquiler_imputado"] = sin_faltantes(datos["p106"])

    salida["agua_red"] = indicador(datos["p110"].isin(AGUA_RED), datos["p110"])
    salida["desague_red"] = indicador(datos["p111a"].isin(DESAGUE_RED), datos["p111a"])
    salida["electricidad"] = indicador(datos["p1121"] == 1, datos["p1121"])
    solido = datos[["p1135", "p1136", "p1139"]].eq(1).any(axis=1)
    salida["combustible_solido"] = indicador(solido, datos["p1136"])
    salida["celular"] = indicador(datos["p1142"] == 1, datos["p1142"])
    salida["tv_cable"] = indicador(datos["p1143"] == 1, datos["p1143"])
    salida["internet"] = indicador(datos["p1144"] == 1, datos["p1144"])

    salida["entrevistado_anio_anterior"] = indicador(datos["panel"] == 1, datos["panel"])
    return verificar_unicidad(salida, LLAVE_ANIO_HOGAR, "vivienda")
