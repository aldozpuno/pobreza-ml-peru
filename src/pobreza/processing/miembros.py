"""Módulo 200 (Características de los miembros del hogar).

Residente habitual (definición del INEI):
    miembro del hogar presente (P204 = 1 y P205 = 2), o
    no miembro que está presente 30 días o más (P204 = 2 y P206 = 1).
P203 = 1 identifica al jefe o jefa; P207 = 2 es mujer; P208A es la edad en años.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from pobreza.processing.common import a_numero, edad_valida, por_hogar
from pobreza.processing.keys import LLAVE_ANIO_HOGAR


def residentes(miembros: pd.DataFrame) -> pd.DataFrame:
    """Filtra a los residentes habituales del hogar."""
    datos = a_numero(miembros, ["p203", "p204", "p205", "p206", "p207", "p208a"])
    presente = (datos["p204"] == 1) & (datos["p205"] == 2)
    no_miembro_presente = (datos["p204"] == 2) & (datos["p206"] == 1)
    datos = datos[presente | no_miembro_presente].copy()
    datos["edad"] = edad_valida(datos["p208a"])
    return datos


def procesar(miembros: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con su estructura demográfica y el perfil del jefe."""
    datos = residentes(miembros)
    edad = datos["edad"]
    datos["es_menor"] = (edad < 18).astype(int)
    datos["es_mayor"] = (edad >= 65).astype(int)
    datos["es_dependiente"] = ((edad < 15) | (edad >= 65)).astype(int)
    datos["es_edad_activa"] = edad.between(15, 64).astype(int)

    salida = por_hogar(datos, {
        "n_residentes": ("edad", "size"),
        "n_menores": ("es_menor", "sum"),
        "n_mayores": ("es_mayor", "sum"),
        "n_dependientes": ("es_dependiente", "sum"),
        "n_edad_activa": ("es_edad_activa", "sum"),
    })
    denominador = salida["n_edad_activa"].replace(0, 1)
    salida["ratio_dependencia"] = salida["n_dependientes"] / denominador

    jefes = datos[datos["p203"] == 1].drop_duplicates(LLAVE_ANIO_HOGAR)
    jefes = jefes.assign(edad_jefe=jefes["edad"],
                         jefe_mujer=np.where(jefes["p207"] == 2, 1.0, 0.0))
    salida = salida.merge(jefes[[*LLAVE_ANIO_HOGAR, "edad_jefe", "jefe_mujer"]],
                          on=LLAVE_ANIO_HOGAR, how="left")
    return salida.drop(columns=["n_dependientes", "n_edad_activa"])
