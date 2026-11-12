"""Tablas para la tesis: columnas en español, cuatro decimales y métricas en filas.

Cada función devuelve una `TablaTesis` con su título y nota, lista para escribirse en
Word con `docx_tables.escribir`. Las métricas por pliegue se presentan con las métricas
en filas y los años en columnas, para que la tabla quepa en el ancho de la página.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pobreza.modeling.estimators import NOMBRES

ETIQUETAS_METRICAS = {
    "auc_roc": "AUC-ROC", "auc_pr": "AUC-PR", "brier": "Brier", "f1": "F1",
    "precision": "Precisión", "recall": "Exhaustividad (recall)", "exactitud": "Exactitud",
    "tasa_real": "Pobreza observada (%)", "tasa_predicha": "Pobreza estimada (%)",
    "tasa_clasificados": "Clasificados como pobres (%)",
}
NOTA_ENAHO = "Elaboración propia con microdatos de la ENAHO (INEI)."


@dataclass
class TablaTesis:
    titulo: str
    datos: pd.DataFrame
    nota: str = NOTA_ENAHO


def _fmt(tabla: pd.DataFrame, decimales: int = 4) -> pd.DataFrame:
    salida = tabla.copy()
    for columna in salida.select_dtypes("number").columns:
        if pd.api.types.is_integer_dtype(salida[columna]):
            salida[columna] = salida[columna].map(lambda v: f"{v:,}".replace(",", " "))
        else:
            salida[columna] = salida[columna].map(lambda v: "" if pd.isna(v) else f"{v:.{decimales}f}")
    return salida


def incidencia(anual: pd.DataFrame) -> TablaTesis:
    datos = anual[["anio", "hogares_muestra", "tasa_personas", "tasa_hogares",
                   "tasa_oficial_inei", "diferencia_pp"]].rename(columns={
        "anio": "Año", "hogares_muestra": "Hogares", "tasa_personas": "Personas (%)",
        "tasa_hogares": "Hogares (%)", "tasa_oficial_inei": "INEI (%)",
        "diferencia_pp": "Diferencia (pp)"})
    return TablaTesis("Incidencia de la pobreza monetaria reproducida y cifra oficial del INEI",
                      _fmt(datos, 2), "Personas: ponderado por FACTOR07 × MIEPERHO; hogares: "
                      "por FACTOR07. " + NOTA_ENAHO)


def panel(resumen: pd.DataFrame) -> TablaTesis:
    datos = resumen[["anio", "hogares", "pregunta_panel", "llave_anio_anterior",
                     "repetidos", "pct_repetidos"]].rename(columns={
        "anio": "Año", "hogares": "Hogares", "pregunta_panel": "Pregunta PANEL = Sí",
        "llave_anio_anterior": "Misma llave el año anterior", "repetidos": "Repetidos",
        "pct_repetidos": "Repetidos (%)"})
    return TablaTesis("Hogares entrevistados en más de un año en la base apilada",
                      _fmt(datos, 1), "Repetido: pregunta PANEL del módulo 100 = Sí, o la llave "
                      "CONGLOME-VIVIENDA-HOGAR aparece en un año anterior. " + NOTA_ENAHO)


def metricas_por_pliegue(tabla: pd.DataFrame, estimador: str) -> TablaTesis:
    datos = tabla[tabla["estimador"] == estimador].set_index("pliegue")
    filas = [c for c in ETIQUETAS_METRICAS if c in datos.columns]
    traspuesta = datos[filas].T.rename(index=ETIQUETAS_METRICAS).reset_index()
    traspuesta = traspuesta.rename(columns={"index": "Métrica"})
    return TablaTesis(f"Desempeño de {NOMBRES.get(estimador, estimador)} por pliegue de "
                      "validación temporal", _fmt(traspuesta))


def comparacion(tabla: pd.DataFrame) -> TablaTesis:
    columnas = ["estimador", "auc_roc", "auc_pr", "brier", "f1", "precision", "recall"]
    datos = tabla[columnas].assign(estimador=lambda d: d["estimador"].map(NOMBRES))
    datos = datos.rename(columns={"estimador": "Modelo", **ETIQUETAS_METRICAS})
    return TablaTesis("Comparación de modelos: promedio de los pliegues de validación",
                      _fmt(datos))


def prueba(tabla: pd.DataFrame) -> TablaTesis:
    columnas = ["Variante", "hogares", "auc_roc", "auc_pr", "f1", "precision", "recall"]
    datos = tabla[columnas].rename(columns={"hogares": "Hogares", **ETIQUETAS_METRICAS})
    return TablaTesis("Desempeño en el conjunto de prueba (ENAHO 2024) según los hogares "
                      "evaluados", _fmt(datos))


def generico(tabla: pd.DataFrame, titulo: str, nota: str = NOTA_ENAHO,
             decimales: int = 2) -> TablaTesis:
    return TablaTesis(titulo, _fmt(tabla, decimales), nota)
