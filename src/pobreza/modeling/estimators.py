"""Fábrica de estimadores con su preprocesamiento.

Cada estimador es un `Pipeline` de scikit-learn: preprocesamiento + clasificador.
    - Árboles (XGBoost, bosque aleatorio): variables tal cual, categorías en one-hot.
    - Lineales y KNN (probit, logit, knn): imputación por mediana, sin columnas constantes
      (p. ej. `covid` en años previos a 2020) y estandarización.
XGBoost maneja los faltantes de forma nativa, por eso no se imputa para él.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.optimize import minimize
from scipy.stats import norm
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBClassifier

NOMBRES = {
    "xgboost": "XGBoost",
    "random_forest": "Bosque aleatorio",
    "probit": "Probit",
    "logit": "Regresión logística",
    "knn": "KNN",
}


class Probit(BaseEstimator, ClassifierMixin):
    """Probit por máxima verosimilitud con una penalización L2 mínima (`alpha`).

    La penalización solo estabiliza la estimación cuando hay columnas colineales
    (por ejemplo, departamento y dominio); con `alpha` pequeño los coeficientes
    coinciden en la práctica con los de un probit clásico.
    """

    def __init__(self, alpha: float = 1e-4, max_iter: int = 500):
        self.alpha = alpha
        self.max_iter = max_iter

    def _objetivo(self, beta, X, y, w):
        z = X @ beta
        signo = 2 * y - 1
        log_p = norm.logcdf(signo * z)
        razon = np.exp(norm.logpdf(z) - log_p) * signo
        perdida = -(w * log_p).sum() / w.sum() + self.alpha * (beta[1:] @ beta[1:])
        gradiente = -(X.T @ (w * razon)) / w.sum()
        gradiente[1:] += 2 * self.alpha * beta[1:]
        return perdida, gradiente

    def fit(self, X, y, sample_weight=None):
        X = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)])
        y = np.asarray(y, dtype=float)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, dtype=float)
        inicio = np.zeros(X.shape[1])
        resultado = minimize(self._objetivo, inicio, args=(X, y, w), jac=True,
                             method="L-BFGS-B", options={"maxiter": self.max_iter})
        self.coef_ = resultado.x
        self.convergio_ = bool(resultado.success)
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, X):
        z = np.column_stack([np.ones(len(X)), np.asarray(X, dtype=float)]) @ self.coef_
        p = norm.cdf(z)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)


def _clasificador(nombre: str, parametros: dict[str, Any], semilla: int):
    if nombre == "xgboost":
        return XGBClassifier(objective="binary:logistic", random_state=semilla, n_jobs=-1,
                             **parametros)
    if nombre == "random_forest":
        return RandomForestClassifier(random_state=semilla, **parametros)
    if nombre == "logit":
        return LogisticRegression(**parametros)
    if nombre == "knn":
        return KNeighborsClassifier(**parametros)
    if nombre == "probit":
        return Probit()
    raise ValueError(f"Estimador desconocido: {nombre}. Opciones: {list(NOMBRES)}")


def _preprocesador(nombre: str, numericas: list[str], categoricas: list[str]):
    one_hot = OneHotEncoder(handle_unknown="ignore", min_frequency=20, sparse_output=False)
    if nombre == "xgboost":
        numerico = "passthrough"
    elif nombre == "random_forest":
        numerico = SimpleImputer(strategy="median")
    else:
        numerico = Pipeline([("imputar", SimpleImputer(strategy="median")),
                             ("sin_constantes", VarianceThreshold(0.0)),
                             ("escalar", StandardScaler())])
        # Se omite la primera categoría para evitar la trampa de las variables ficticias.
        sin_referencia = OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20,
                                       drop="first", sparse_output=False)
        one_hot = Pipeline([("imputar", SimpleImputer(strategy="most_frequent")),
                            ("one_hot", sin_referencia)])
    return ColumnTransformer([("num", numerico, numericas), ("cat", one_hot, categoricas)],
                             verbose_feature_names_out=False)


def construir(nombre: str, parametros: dict[str, Any], numericas: list[str],
              categoricas: list[str], semilla: int) -> Pipeline:
    """Pipeline completo (preprocesamiento + clasificador) listo para `fit`."""
    return Pipeline([
        ("preprocesar", _preprocesador(nombre, numericas, categoricas)),
        ("modelo", _clasificador(nombre, parametros or {}, semilla)),
    ])
