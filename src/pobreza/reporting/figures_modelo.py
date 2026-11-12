"""Figuras del modelo: comparación, curvas, calibración, confusión, SHAP y sesgo regional."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from pobreza.modeling.estimators import NOMBRES
from pobreza.reporting.style import (ACENTO, BUENO, GRIS, GRIS_CLARO, MALO, coma_decimal,
                                     figura, guardar)


def comparacion_modelos(tabla: pd.DataFrame, principal: str, carpeta: Path) -> Path:
    """AUC-PR promedio de validación por estimador; el principal en color de acento."""
    datos = tabla.sort_values("auc_pr")
    fig, ax = figura(6.5)
    colores = [ACENTO if e == principal else GRIS_CLARO for e in datos["estimador"]]
    ax.barh([NOMBRES.get(e, e) for e in datos["estimador"]], datos["auc_pr"], color=colores)
    for i, valor in enumerate(datos["auc_pr"]):
        ax.text(valor + 0.005, i, coma_decimal(valor, 3), va="center", fontsize=8)
    ax.set_xlabel("AUC-PR promedio en los pliegues de validación")
    ax.set_xlim(0, min(1, datos["auc_pr"].max() * 1.15))
    ax.grid(axis="y", visible=False)
    return guardar(fig, carpeta, "fig_comparacion_modelos")


def curvas(roc: pd.DataFrame, pr: pd.DataFrame, tasa_base: float, carpeta: Path) -> Path:
    """Curva ROC y curva precisión-exhaustividad en el año de prueba."""
    fig, (izq, der) = figura(7, ncols=2)
    izq.plot(roc["fpr"], roc["tpr"], color=ACENTO, lw=2)
    izq.plot([0, 1], [0, 1], color=GRIS, ls="--", lw=1)
    izq.set_xlabel("Tasa de falsos positivos")
    izq.set_ylabel("Tasa de verdaderos positivos")
    der.plot(pr["recall"], pr["precision"], color=ACENTO, lw=2)
    der.axhline(tasa_base, color=GRIS, ls="--", lw=1)
    der.set_xlabel("Exhaustividad (recall)")
    der.set_ylabel("Precisión")
    for eje, letra in ((izq, "a"), (der, "b")):
        eje.set_xlim(0, 1)
        eje.set_ylim(0, 1.02)
        eje.text(0.02, 0.95, f"{letra})", transform=eje.transAxes, fontweight="bold")
    fig.tight_layout()
    return guardar(fig, carpeta, "fig_curvas_roc_pr")


def calibracion(tabla: pd.DataFrame, brier: float, carpeta: Path) -> Path:
    """Diagrama de confiabilidad: probabilidad predicha frente a proporción observada."""
    fig, ax = figura(8, ancho_cm=10)
    ax.plot([0, 1], [0, 1], color=GRIS, ls="--", lw=1, label="Calibración perfecta")
    ax.plot(tabla["prob_media"], tabla["observado"], color=ACENTO, marker="o", lw=2,
            label="Modelo calibrado")
    ax.set_xlabel("Probabilidad predicha (promedio por decil)")
    ax.set_ylabel("Proporción observada de pobres")
    ax.text(0.97, 0.05, f"Brier = {coma_decimal(brier, 4)}", transform=ax.transAxes,
            ha="right", fontsize=9)
    ax.legend(loc="upper left", fontsize=8)
    return guardar(fig, carpeta, "fig_calibracion")


def matriz_confusion(tabla: pd.DataFrame, carpeta: Path) -> Path:
    """Matriz de confusión del año de prueba en hogares."""
    h = tabla.set_index("Celda")["Hogares"]
    matriz = np.array([[h.iloc[3], h.iloc[2]], [h.iloc[1], h.iloc[0]]])
    fig, ax = figura(7.5, ancho_cm=9)
    ax.imshow(matriz, cmap="Blues")
    ax.grid(False)
    for (i, j), valor in np.ndenumerate(matriz):
        ax.text(j, i, f"{valor:,}".replace(",", " "), ha="center", va="center",
                color="white" if valor > matriz.max() / 2 else "black")
    ax.set_xticks([0, 1], ["No pobre", "Pobre"])
    ax.set_yticks([0, 1], ["No pobre", "Pobre"])
    ax.set_xlabel("Clasificación del modelo")
    ax.set_ylabel("Condición observada (INEI)")
    return guardar(fig, carpeta, "fig_matriz_confusion")


def importancia_shap(tabla: pd.DataFrame, etiquetas: dict[str, str], carpeta: Path,
                     n: int = 15) -> Path:
    """Media de |SHAP| de las variables más importantes, coloreada por la dirección."""
    datos = tabla.head(n).iloc[::-1]
    colores = [MALO if s == "+" else BUENO if s == "-" else GRIS
               for s in datos["signo_observado"]]
    fig, ax = figura(9)
    ax.barh(datos["variable"].map(etiquetas).fillna(datos["variable"]), datos["importancia"],
            color=colores)
    ax.set_xlabel("Media del valor SHAP absoluto (log-odds)")
    ax.grid(axis="y", visible=False)
    ax.text(1.0, -0.2, "Rojo: aumenta la probabilidad de pobreza · Verde: la reduce",
            transform=ax.transAxes, ha="right", va="top", fontsize=8, color=GRIS)
    return guardar(fig, carpeta, "fig_importancia_shap")


def shap_periodos(tabla: pd.DataFrame, etiquetas: dict[str, str], carpeta: Path,
                  n: int = 12) -> Path:
    """Importancia antes y después de la COVID-19 (gráfico de mancuernas)."""
    datos = tabla.head(n).iloc[::-1]
    fig, ax = figura(9)
    y = np.arange(len(datos))
    ax.hlines(y, datos["importancia_antes"], datos["importancia_despues"], color=GRIS_CLARO)
    ax.scatter(datos["importancia_antes"], y, color=GRIS, label="2017–2019", zorder=3)
    ax.scatter(datos["importancia_despues"], y, color=ACENTO, label="2021–2024", zorder=3)
    ax.set_yticks(y, datos["variable"].map(etiquetas).fillna(datos["variable"]))
    ax.set_xlabel("Media del valor SHAP absoluto (log-odds)")
    ax.legend(fontsize=8, loc="lower right")
    return guardar(fig, carpeta, "fig_shap_periodos")


def sesgo_regional(tabla: pd.DataFrame, carpeta: Path) -> Path:
    """Tasa observada frente a predicha por departamento (personas)."""
    datos = tabla.sort_values("tasa_observada")
    fig, ax = figura(12)
    y = np.arange(len(datos))
    ax.hlines(y, datos["tasa_observada"], datos["tasa_predicha"], color=GRIS_CLARO)
    ax.scatter(datos["tasa_observada"], y, color=GRIS, label="Observada (ENAHO)", zorder=3)
    ax.scatter(datos["tasa_predicha"], y, color=ACENTO, label="Estimada por el modelo", zorder=3)
    ax.set_yticks(y, datos["departamento"])
    ax.set_xlabel("Pobreza monetaria (% de personas)")
    ax.legend(fontsize=8, loc="lower right")
    return guardar(fig, carpeta, "fig_sesgo_regional")
