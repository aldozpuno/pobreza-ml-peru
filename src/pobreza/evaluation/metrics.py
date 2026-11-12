"""Métricas de clasificación sobre una tabla de predicciones (`modeling.training.predecir`).

Con `ponderar=True` cada hogar pesa su FACTOR07, de modo que las métricas representan a
la población de hogares y no a la muestra. Las tasas de pobreza siempre son de personas
(FACTOR07 × MIEPERHO), comparables con la cifra oficial del INEI:
    tasa_predicha     → promedio de probabilidades calibradas (estima la incidencia)
    tasa_clasificados → proporción sobre el umbral (mayor, porque el umbral prioriza no
                        excluir a hogares pobres; es la cifra relevante para focalizar)
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             f1_score, precision_score, recall_score, roc_auc_score)


def metricas(pred: pd.DataFrame, ponderar: bool = False) -> dict[str, float]:
    """Diccionario con AUC-ROC, AUC-PR, Brier, F1, precisión, exhaustividad y tasas."""
    y, prob, yhat = pred["pobre"], pred["prob"], pred["pred"]
    peso = pred["peso_hogar"] if ponderar else None
    personas = pred["peso_personas"]
    return {
        "hogares": len(pred),
        "auc_roc": roc_auc_score(y, prob, sample_weight=peso),
        "auc_pr": average_precision_score(y, prob, sample_weight=peso),
        "brier": brier_score_loss(y, prob, sample_weight=peso),
        "f1": f1_score(y, yhat, sample_weight=peso, zero_division=0),
        "precision": precision_score(y, yhat, sample_weight=peso, zero_division=0),
        "recall": recall_score(y, yhat, sample_weight=peso, zero_division=0),
        "exactitud": accuracy_score(y, yhat, sample_weight=peso),
        "tasa_real": 100 * np.average(y, weights=personas),
        # Estimación de la incidencia: promedio de probabilidades calibradas (personas).
        "tasa_predicha": 100 * np.average(prob, weights=personas),
        # Proporción clasificada como pobre con el umbral (uso en focalización).
        "tasa_clasificados": 100 * np.average(yhat, weights=personas),
        "falsos_negativos": int(((y == 1) & (yhat == 0)).sum()),
        "falsos_positivos": int(((y == 0) & (yhat == 1)).sum()),
    }


def tabla(predicciones: pd.DataFrame, por: list[str], ponderar: bool = False) -> pd.DataFrame:
    """Métricas por grupo (por ejemplo, por estimador y pliegue)."""
    filas = [{**dict(zip(por, clave if isinstance(clave, tuple) else (clave,))),
              **metricas(grupo, ponderar)}
             for clave, grupo in predicciones.groupby(por, sort=False)]
    return pd.DataFrame(filas)


def matriz_confusion(pred: pd.DataFrame) -> pd.DataFrame:
    """Conteo de hogares y personas expandidas en cada celda de la matriz de confusión."""
    celdas = {
        "Verdadero positivo": (pred["pobre"] == 1) & (pred["pred"] == 1),
        "Falso negativo (exclusión)": (pred["pobre"] == 1) & (pred["pred"] == 0),
        "Falso positivo (filtración)": (pred["pobre"] == 0) & (pred["pred"] == 1),
        "Verdadero negativo": (pred["pobre"] == 0) & (pred["pred"] == 0),
    }
    return pd.DataFrame([{"Celda": nombre, "Hogares": int(m.sum()),
                          "Personas expandidas": float(pred.loc[m, "peso_personas"].sum())}
                         for nombre, m in celdas.items()])


def curva_calibracion(pred: pd.DataFrame, grupos: int = 10) -> pd.DataFrame:
    """Probabilidad media predicha frente a proporción observada de pobres, por decil."""
    datos = pred.assign(grupo=pd.qcut(pred["prob"].rank(method="first"), grupos, labels=False))
    return (datos.groupby("grupo")
            .agg(prob_media=("prob", "mean"), observado=("pobre", "mean"),
                 hogares=("pobre", "size"))
            .reset_index())


def curvas(pred: pd.DataFrame, puntos: int = 100) -> dict[str, pd.DataFrame]:
    """Curvas ROC y precisión-exhaustividad reducidas a `puntos` para graficar."""
    from sklearn.metrics import precision_recall_curve, roc_curve
    fpr, tpr, _ = roc_curve(pred["pobre"], pred["prob"])
    precision, recall, _ = precision_recall_curve(pred["pobre"], pred["prob"])
    idx_roc = np.linspace(0, len(fpr) - 1, min(puntos, len(fpr))).astype(int)
    idx_pr = np.linspace(0, len(recall) - 1, min(puntos, len(recall))).astype(int)
    return {
        "roc": pd.DataFrame({"fpr": fpr[idx_roc], "tpr": tpr[idx_roc]}),
        "pr": pd.DataFrame({"recall": recall[idx_pr], "precision": precision[idx_pr]}),
    }
