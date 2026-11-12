"""Figuras descriptivas: medición de la pobreza, hogares repetidos y diseño de validación."""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import pandas as pd

from pobreza.modeling.splits import Pliegue
from pobreza.reporting.style import (ACENTO, ACENTO_SUAVE, GRIS, GRIS_CLARO, coma_decimal,
                                     figura, guardar)


def incidencia_anual(tabla: pd.DataFrame, carpeta: Path) -> Path:
    """Tasa de personas reproducida, cifra oficial del INEI y tasa de hogares."""
    fig, ax = figura(8)
    ax.plot(tabla["anio"], tabla["tasa_oficial_inei"], color=GRIS, lw=1, ls="--",
            marker="s", ms=4, label="INEI (cifra oficial)")
    ax.plot(tabla["anio"], tabla["tasa_personas"], color=ACENTO, lw=2, marker="o", ms=5,
            label="Personas (FACTOR07 × MIEPERHO)")
    ax.plot(tabla["anio"], tabla["tasa_hogares"], color=ACENTO_SUAVE, lw=1.5, marker="o",
            ms=4, label="Hogares (FACTOR07)")
    for _, fila in tabla.iterrows():
        ax.annotate(coma_decimal(fila["tasa_personas"]), (fila["anio"], fila["tasa_personas"]),
                    textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
    ax.set_xlabel("Año")
    ax.set_ylabel("Pobreza monetaria (%)")
    ax.set_xticks(tabla["anio"])
    ax.set_ylim(0, max(tabla["tasa_personas"].max(), tabla["tasa_oficial_inei"].max()) * 1.2)
    ax.legend(loc="lower right", fontsize=8)
    return guardar(fig, carpeta, "fig_incidencia_anual")


def incidencia_area(tabla: pd.DataFrame, carpeta: Path) -> Path:
    """Tasa de pobreza (personas) urbana y rural por año."""
    fig, ax = figura(7)
    for rural, color, etiqueta in ((1, ACENTO, "Rural"), (0, GRIS, "Urbana")):
        datos = tabla[tabla["rural"] == rural]
        ax.plot(datos["anio"], datos["tasa_personas"], marker="o", color=color, lw=2,
                label=etiqueta)
    ax.set_xlabel("Año")
    ax.set_ylabel("Pobreza monetaria (%)")
    ax.set_xticks(sorted(tabla["anio"].unique()))
    ax.legend(fontsize=8)
    return guardar(fig, carpeta, "fig_incidencia_area")


def hogares_repetidos(resumen: pd.DataFrame, carpeta: Path) -> Path:
    """Hogares nuevos y repetidos por año en la base apilada."""
    fig, ax = figura(7)
    nuevos = resumen["hogares"] - resumen["repetidos"]
    ax.bar(resumen["anio"], nuevos, color=GRIS_CLARO, label="Primera vez en la base")
    ax.bar(resumen["anio"], resumen["repetidos"], bottom=nuevos, color=ACENTO,
           label="Entrevistado en un año anterior")
    for _, fila in resumen.iterrows():
        ax.annotate(f"{coma_decimal(fila['pct_repetidos'])} %",
                    (fila["anio"], fila["hogares"]), textcoords="offset points",
                    xytext=(0, 3), ha="center", fontsize=8)
    ax.set_xlabel("Año")
    ax.set_ylabel("Hogares en la muestra")
    ax.set_xticks(resumen["anio"])
    ax.legend(fontsize=8, ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2))
    ax.grid(axis="x", visible=False)
    return guardar(fig, carpeta, "fig_hogares_repetidos")


def esquema_validacion(pliegues: list[Pliegue], carpeta: Path) -> Path:
    """Diagrama de la validación temporal: entrenamiento, calibración y evaluación."""
    fig, ax = figura(6.5)
    colores = {"Entrenamiento": GRIS_CLARO, "Calibración": ACENTO_SUAVE, "Evaluación": ACENTO}
    for fila, pliegue in enumerate(reversed(pliegues)):
        bloques = [(a, "Entrenamiento") for a in pliegue.entrenamiento]
        bloques += [(pliegue.calibracion, "Calibración"), (pliegue.validacion, "Evaluación")]
        for anio, tipo in bloques:
            ax.barh(fila, 0.92, left=anio - 0.46, color=colores[tipo], edgecolor="white")
    ax.set_yticks(range(len(pliegues)))
    ax.set_yticklabels([p.nombre for p in reversed(pliegues)])
    anios = sorted({a for p in pliegues for a in (*p.entrenamiento, p.validacion)})
    ax.set_xticks(anios)
    ax.set_xlabel("Año de la ENAHO")
    ax.grid(False)
    ax.legend(handles=[mpatches.Patch(color=c, label=t) for t, c in colores.items()],
              ncol=3, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    return guardar(fig, carpeta, "fig_esquema_validacion")
