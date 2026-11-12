"""Módulo 300 (Educación), personas de 3 años o más.

P301A (último nivel aprobado) se convierte en años de estudio aproximados:
    1 sin nivel = 0 · 2 inicial = 0 · 3 primaria incompleta = 3 · 4 primaria completa = 6
    5 secundaria incompleta = 8 · 6 secundaria completa = 11
    7 superior no universitaria incompleta = 12 · 8 completa = 14
    9 universitaria incompleta = 13 · 10 completa = 16 · 11 posgrado = 18
    12 básica especial = sin equivalencia (NaN)
P302 = 2 no sabe leer ni escribir (solo se pregunta con P301A ≤ 3 o = 12; el resto sabe)
P306 = 1 matriculado este año.
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero, cociente, edad_valida, por_hogar

ANIOS_POR_NIVEL = {1: 0, 2: 0, 3: 3, 4: 6, 5: 8, 6: 11, 7: 12, 8: 14, 9: 13, 10: 16, 11: 18}


def procesar(educacion: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con su capital humano."""
    datos = a_numero(educacion, ["p208a", "p301a", "p302", "p306"])
    datos["edad"] = edad_valida(datos["p208a"])
    datos["anios_estudio"] = datos["p301a"].map(ANIOS_POR_NIVEL)

    adulto = datos["edad"] >= 15
    datos["anios_adulto"] = datos["anios_estudio"].where(adulto)
    # P302 solo se pregunta a quien no tiene nivel o tiene primaria incompleta;
    # quien no responde P302 alcanzó un nivel mayor y sabe leer y escribir.
    datos["adulto_con_dato"] = adulto.astype(int)
    datos["adulto_analfabeto"] = (adulto & (datos["p302"] == 2)).astype(int)

    escolar = datos["edad"].between(6, 17)
    datos["escolar"] = escolar.astype(int)
    datos["escolar_matriculado"] = (escolar & (datos["p306"] == 1)).astype(int)

    salida = por_hogar(datos, {
        "educ_prom": ("anios_adulto", "mean"),
        "educ_max": ("anios_adulto", "max"),
        "adultos": ("adulto_con_dato", "sum"),
        "analfabetos": ("adulto_analfabeto", "sum"),
        "escolares": ("escolar", "sum"),
        "matriculados": ("escolar_matriculado", "sum"),
    })
    salida["brecha_educ"] = salida["educ_max"] - salida["educ_prom"]
    salida["tasa_analfabetismo"] = cociente(salida["analfabetos"], salida["adultos"])
    # Hogares sin menores en edad escolar: no hay inasistencia que medir → 1.
    salida["asistencia_menores"] = cociente(salida["matriculados"],
                                            salida["escolares"]).fillna(1.0)
    return salida.drop(columns=["adultos", "analfabetos", "escolares", "matriculados"])
