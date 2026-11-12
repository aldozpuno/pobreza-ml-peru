"""Pruebas de la medición de la pobreza, la validación temporal y el umbral."""

import numpy as np
import pandas as pd
import pytest

from pobreza.features import leakage
from pobreza.measurement import poverty
from pobreza.modeling import thresholds
from pobreza.modeling.splits import generar_pliegues


def test_incidencia_pondera_por_personas():
    datos = pd.DataFrame({"anio": [2024, 2024], "pobre": [1, 0], "peso_hogar": [100, 100],
                          "peso_personas": [600, 200]})
    fila = poverty.incidencia(datos).iloc[0]
    assert fila["tasa_personas"] == pytest.approx(75.0)   # 600 / 800
    assert fila["tasa_hogares"] == pytest.approx(50.0)
    assert fila["poblacion_expandida"] == 800


def test_validacion_detiene_si_no_reproduce_al_inei(proyecto):
    tabla = pd.DataFrame({"anio": [2024], "tasa_personas": [21.9]})
    with pytest.raises(poverty.ObjetivoInvalidoError):
        poverty.validar(proyecto, tabla, estricto=True)


def test_pliegues_no_mezclan_anios(proyecto):
    pliegues = generar_pliegues(proyecto)
    assert pliegues[0].entrenamiento == (2017, 2018)
    assert pliegues[0].calibracion == 2019 and pliegues[0].validacion == 2020
    final = pliegues[-1]
    assert final.es_prueba_final and final.validacion == 2024 and final.calibracion == 2023
    for p in pliegues:
        assert max(p.entrenamiento) < p.calibracion < p.validacion


def test_umbral_por_recall_cumple_el_minimo():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    prob = np.clip(y * 0.3 + rng.random(2000) * 0.7, 0, 1)
    umbral = thresholds.elegir(y, prob, "recall_minimo", 0.8)
    assert ((prob >= umbral) & (y == 1)).sum() / y.sum() >= 0.8


def test_fuga_de_datos_bloquea_el_gasto(proyecto):
    with pytest.raises(leakage.FugaDeDatosError):
        leakage.verificar(proyecto, ["educ_prom", "gashog2d"])


def test_delong_coincide_con_sklearn():
    import numpy as np
    from sklearn.metrics import roc_auc_score

    from pobreza.evaluation.inference import delong

    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 2000)
    a, b = y + rng.normal(0, 1, 2000), y + rng.normal(0, 1.5, 2000)
    resultado = delong(y, a, b)
    assert abs(resultado["auc_a"] - roc_auc_score(y, a)) < 1e-9
    assert abs(resultado["auc_b"] - roc_auc_score(y, b)) < 1e-9
    assert resultado["p_valor"] < 0.05
