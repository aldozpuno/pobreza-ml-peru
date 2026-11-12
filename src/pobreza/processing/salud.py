"""Módulo 400 (Salud).

P4191–P4198: afiliación a EsSalud, seguro privado, EPS, FF. AA./Policía, SIS,
universitario, escolar privado y otro (1 = Sí, 2 = No).
P401 = 1: padece alguna enfermedad o malestar crónico.
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero, cociente, por_hogar

SEGUROS = ["p4191", "p4192", "p4193", "p4194", "p4195", "p4196", "p4197", "p4198"]
SIS = "p4195"


def procesar(salud: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con afiliación a seguros y enfermedades crónicas."""
    datos = a_numero(salud, [*SEGUROS, "p401"])
    afiliado = datos[SEGUROS].eq(1)
    datos["con_seguro"] = afiliado.any(axis=1).astype(int)
    otros = [c for c in SEGUROS if c != SIS]
    datos["solo_sis"] = (afiliado[SIS] & ~afiliado[otros].any(axis=1)).astype(int)
    datos["cronico"] = (datos["p401"] == 1).astype(int)
    datos["persona"] = 1

    salida = por_hogar(datos, {
        "tiene_seguro": ("con_seguro", "max"),
        "n_solo_sis": ("solo_sis", "sum"),
        "n_cronicos": ("cronico", "sum"),
        "personas": ("persona", "sum"),
    })
    salida["solo_sis"] = cociente(salida["n_solo_sis"], salida["personas"])
    return salida.drop(columns=["n_solo_sis", "personas"])
