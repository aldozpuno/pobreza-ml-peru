"""Pobreza observada frente a predicha por departamento (sesgo territorial).

La tasa predicha es el promedio de probabilidades calibradas ponderado por personas;
así se estima la incidencia de un territorio sin depender del umbral de clasificación.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

DEPARTAMENTOS = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}


def _promedio(valores: pd.Series, pesos: pd.Series) -> float:
    return float(100 * np.average(valores, weights=pesos))


def sesgo_por_departamento(pred: pd.DataFrame) -> pd.DataFrame:
    """Tasa observada, tasa predicha y diferencia (pp) por departamento, en personas."""
    filas = []
    for codigo, grupo in pred.groupby("departamento"):
        observada = _promedio(grupo["pobre"], grupo["peso_personas"])
        predicha = _promedio(grupo["prob"], grupo["peso_personas"])
        filas.append({
            "codigo": codigo,
            "departamento": DEPARTAMENTOS.get(str(codigo), str(codigo)),
            "hogares": len(grupo),
            "tasa_observada": observada,
            "tasa_predicha": predicha,
            "tasa_clasificados": _promedio(grupo["pred"], grupo["peso_personas"]),
            "sesgo_pp": predicha - observada,
        })
    return pd.DataFrame(filas).sort_values("tasa_observada", ascending=False)


def resumen_sesgo(tabla: pd.DataFrame) -> dict[str, float]:
    """Error absoluto medio y máximo entre departamentos, en puntos porcentuales."""
    return {
        "error_absoluto_medio_pp": float(tabla["sesgo_pp"].abs().mean()),
        "error_absoluto_maximo_pp": float(tabla["sesgo_pp"].abs().max()),
        "correlacion_observada_predicha": float(
            tabla[["tasa_observada", "tasa_predicha"]].corr().iloc[0, 1]),
    }
