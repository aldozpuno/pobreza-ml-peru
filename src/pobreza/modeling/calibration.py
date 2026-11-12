"""Calibración de probabilidades con regresión isotónica.

Se ajusta con el año de calibración (datos que el clasificador no vio al entrenar),
para que una probabilidad de 0,30 signifique que cerca del 30 % de esos hogares es pobre.
"""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression


class Calibrador:
    """Isotónica (`metodo='isotonica'`) o identidad (`metodo='ninguna'`)."""

    def __init__(self, metodo: str = "isotonica"):
        if metodo not in {"isotonica", "ninguna"}:
            raise ValueError("calibracion debe ser 'isotonica' o 'ninguna'")
        self.metodo = metodo
        self._isotonica: IsotonicRegression | None = None

    def ajustar(self, prob: np.ndarray, y: np.ndarray,
                peso: np.ndarray | None = None) -> "Calibrador":
        if self.metodo == "isotonica":
            self._isotonica = IsotonicRegression(y_min=0.0, y_max=1.0, out_of_bounds="clip")
            self._isotonica.fit(prob, y, sample_weight=peso)
        return self

    def transformar(self, prob: np.ndarray) -> np.ndarray:
        """Probabilidades calibradas en float64 y acotadas a [0, 1]."""
        prob = np.asarray(prob, dtype=float)
        if self._isotonica is not None:
            prob = self._isotonica.predict(prob)
        return np.clip(prob, 0.0, 1.0)
