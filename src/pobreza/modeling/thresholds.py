"""Elección del umbral de decisión (probabilidad a partir de la cual un hogar se clasifica
como pobre). Siempre se elige con el año de calibración.

Criterios:
    f1            → maximiza el F1 (equilibrio entre precisión y exhaustividad)
    recall_minimo → el umbral más alto que todavía identifica al `recall_minimo` de los pobres
    tasa_oficial  → el umbral con el que la tasa predicha (personas) iguala a la observada
"""

from __future__ import annotations

import numpy as np
from sklearn.metrics import precision_recall_curve


def _por_f1(y: np.ndarray, prob: np.ndarray) -> float:
    precision, recall, umbrales = precision_recall_curve(y, prob)
    f1 = 2 * precision * recall / np.clip(precision + recall, 1e-12, None)
    return float(umbrales[int(np.argmax(f1[:-1]))])


def _por_recall(y: np.ndarray, prob: np.ndarray, minimo: float) -> float:
    _, recall, umbrales = precision_recall_curve(y, prob)
    validos = umbrales[recall[:-1] >= minimo]
    return float(validos.max()) if len(validos) else float(umbrales.min())


def _por_tasa(y: np.ndarray, prob: np.ndarray, peso: np.ndarray) -> float:
    tasa_real = np.average(y, weights=peso)
    orden = np.argsort(-prob)
    acumulada = np.cumsum(peso[orden]) / peso.sum()
    posicion = int(np.searchsorted(acumulada, tasa_real))
    return float(prob[orden][min(posicion, len(prob) - 1)])


def elegir(y: np.ndarray, prob: np.ndarray, criterio: str = "f1",
           recall_minimo: float = 0.8, peso: np.ndarray | None = None) -> float:
    """Devuelve el umbral según el criterio configurado."""
    y = np.asarray(y)
    prob = np.asarray(prob)
    if criterio == "f1":
        return _por_f1(y, prob)
    if criterio == "recall_minimo":
        return _por_recall(y, prob, recall_minimo)
    if criterio == "tasa_oficial":
        return _por_tasa(y, prob, np.ones_like(prob) if peso is None else np.asarray(peso))
    raise ValueError(f"Criterio de umbral desconocido: {criterio}")
