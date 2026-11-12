"""Módulo 37 (Programas sociales), archivo ENAHO01-AAAA-700, una fila por hogar.

    P701_01 Vaso de Leche · P701_03 / P701_04 desayunos o almuerzos escolares (Qali Warma)
    P710_04 JUNTOS · P710_05 Pensión 65   (1 = recibió, 0 = pase)

Estas variables se asocian a la pobreza porque los programas se asignan a hogares
pobres; en la interpretación no deben leerse como efecto causal del programa.
"""

from __future__ import annotations

import pandas as pd

from pobreza.processing.common import a_numero, por_hogar

PROGRAMAS = {
    "vaso_leche": ["p701_01"],
    "qali_warma": ["p701_03", "p701_04"],
    "juntos": ["p710_04"],
    "pension65": ["p710_05"],
}


def procesar(programas: pd.DataFrame) -> pd.DataFrame:
    """Una fila por hogar con indicadores 0/1 de cada programa."""
    columnas = [c for grupo in PROGRAMAS.values() for c in grupo]
    datos = a_numero(programas, columnas)
    for nombre, origen in PROGRAMAS.items():
        datos[nombre] = datos[origen].eq(1).any(axis=1).astype(int)
    return por_hogar(datos, {nombre: (nombre, "max") for nombre in PROGRAMAS})
