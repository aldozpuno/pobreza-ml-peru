"""Inferencia sobre el desempeño: ¿la diferencia de AUC entre dos modelos es significativa?

Se usa la prueba de DeLong para curvas ROC correlacionadas (DeLong, DeLong y
Clarke-Pearson, 1988), en la implementación rápida de Sun y Xu (2014): ambos modelos se
evalúan sobre los mismos hogares, así que la varianza de la diferencia considera la
covarianza entre sus AUC. Responde a la hipótesis específica 3 (XGBoost supera a los
modelos de referencia fuera de muestra).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def _rangos_medios(x: np.ndarray) -> np.ndarray:
    """Rangos con empates promediados (como en la prueba de Mann-Whitney)."""
    return stats.rankdata(x, method="average")


def _componentes(puntajes: np.ndarray, m: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """AUC y componentes estructurales de DeLong; las primeras `m` filas son positivos."""
    k, total = puntajes.shape
    n = total - m
    tx = np.array([_rangos_medios(p[:m]) for p in puntajes])
    ty = np.array([_rangos_medios(p[m:]) for p in puntajes])
    tz = np.array([_rangos_medios(p) for p in puntajes])
    auc = (tz[:, :m].sum(axis=1) / m - (m + 1) / 2) / n
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    return auc, v01, v10


def delong(y: np.ndarray, prob_a: np.ndarray, prob_b: np.ndarray) -> dict[str, float]:
    """Compara dos AUC sobre las mismas observaciones. Devuelve AUC, diferencia, z y p."""
    y = np.asarray(y).astype(int)
    orden = np.argsort(-y, kind="mergesort")       # positivos primero
    m = int(y.sum())
    puntajes = np.vstack([np.asarray(prob_a)[orden], np.asarray(prob_b)[orden]])
    auc, v01, v10 = _componentes(puntajes, m)
    sx, sy = np.cov(v01), np.cov(v10)
    cov = sx / m + sy / (len(y) - m)
    var = cov[0, 0] + cov[1, 1] - 2 * cov[0, 1]
    dif = auc[0] - auc[1]
    z = dif / np.sqrt(var) if var > 0 else np.inf
    p = 2 * stats.norm.sf(abs(z))
    margen = stats.norm.ppf(0.975) * np.sqrt(var)
    return {"auc_a": float(auc[0]), "auc_b": float(auc[1]), "diferencia": float(dif),
            "ic95_inferior": float(dif - margen), "ic95_superior": float(dif + margen),
            "z": float(z), "p_valor": float(p)}


def comparar_con_principal(prueba: pd.DataFrame, principal: str) -> pd.DataFrame:
    """DeLong del modelo principal frente a cada otro modelo, en el mismo año de prueba."""
    llave = ["anio", "conglome", "vivienda", "hogar"]
    base = prueba[prueba["estimador"] == principal][llave + ["pobre", "prob"]]
    filas = []
    for otro in sorted(set(prueba["estimador"]) - {principal}):
        datos = base.merge(prueba[prueba["estimador"] == otro][llave + ["prob"]],
                           on=llave, suffixes=("", "_otro"))
        resultado = delong(datos["pobre"].to_numpy(), datos["prob"].to_numpy(),
                           datos["prob_otro"].to_numpy())
        filas.append({"modelo_principal": principal, "modelo_comparado": otro,
                      "hogares": len(datos), **resultado})
    return pd.DataFrame(filas)
