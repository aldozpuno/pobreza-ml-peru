"""Módulo 500 (Empleo e ingresos), personas de 14 años o más.

Solo se usan variables de condición laboral, nunca montos de ingreso (fuga de datos).
    OCU500 = 1 ocupado · P507 categoría ocupacional (2 independiente, 5 familiar no remunerado)

Informalidad. La ENAHO 2024 no publica OCUPINF, así que el empleo informal se reconstruye
con el mismo criterio (OIT) en todos los años, para que la variable signifique lo mismo:
    - empleador o independiente (P507 = 1, 2): negocio no registrado en la SUNAT (P510A1 = 3)
    - asalariado (P507 = 3, 4, 6): no afiliado a un sistema de pensiones (P558A5 = 5)
    - trabajador familiar no remunerado u otro (P507 = 5, 7): siempre informal
Contrastada con OCUPINF en 2017–2023, la regla coincide en el 93,6–94,6 % de los ocupados
y da una tasa unos 5 puntos menor (no capta asalariados con pensión pero sin seguro de
salud pagado por el empleador).
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero, cociente, edad_valida, por_hogar
from pobreza.processing.keys import LLAVE_ANIO_HOGAR

CATEGORIAS_INDEPENDIENTES = {2, 5}
EMPLEADOR_O_INDEPENDIENTE = {1, 2}
ASALARIADO = {3, 4, 6}
SIEMPRE_INFORMAL = {5, 7}


def informal(datos: pd.DataFrame) -> pd.Series:
    """1 si el ocupado tiene empleo informal según la regla descrita arriba."""
    categoria = datos["p507"]
    sin_registro = categoria.isin(EMPLEADOR_O_INDEPENDIENTE) & (datos["p510a1"] == 3)
    sin_pension = categoria.isin(ASALARIADO) & (datos["p558a5"] == 5)
    regla = categoria.isin(SIEMPRE_INFORMAL) | sin_registro | sin_pension
    return (datos["ocupado"].eq(1) & regla).astype(int)


def procesar(empleo: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con ocupación, informalidad y tipo de empleo del jefe."""
    datos = a_numero(empleo, ["p203", "p208a", "ocu500", "p507", "p510a1", "p558a5"])
    datos = datos[edad_valida(datos["p208a"]) >= 14].copy()
    datos["ocupado"] = (datos["ocu500"] == 1).astype(int)
    datos["informal"] = informal(datos)
    datos["persona"] = 1

    salida = por_hogar(datos, {
        "n_ocupados": ("ocupado", "sum"),
        "n_informales": ("informal", "sum"),
        "personas_14_mas": ("persona", "sum"),
    })
    salida["tasa_ocupacion"] = cociente(salida["n_ocupados"], salida["personas_14_mas"])
    salida["tasa_informalidad"] = cociente(salida["n_informales"],
                                           salida["n_ocupados"]).fillna(0.0)

    jefe = datos[datos["p203"] == 1].drop_duplicates(LLAVE_ANIO_HOGAR)
    jefe = jefe.assign(jefe_independiente=jefe["p507"].isin(CATEGORIAS_INDEPENDIENTES)
                       .astype(float))
    salida = salida.merge(jefe[[*LLAVE_ANIO_HOGAR, "jefe_independiente"]],
                          on=LLAVE_ANIO_HOGAR, how="left")
    salida["jefe_independiente"] = salida["jefe_independiente"].fillna(0.0)
    return salida.drop(columns=["personas_14_mas"])
