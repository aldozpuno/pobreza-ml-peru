"""Reúne los resultados del pipeline en un diccionario para redactar la tesis."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]  # raíz del proyecto pobreza-ml-peru
D = RAIZ / "resultados/reportes/datos"
FIG = RAIZ / "resultados/reportes/figuras"
WEB = RAIZ / "web/public/data"

NOMBRES = {"xgboost": "XGBoost", "random_forest": "Bosque aleatorio", "probit": "Probit",
           "logit": "Regresión logística", "knn": "KNN", "xgboost_sin_alquiler": "XGBoost sin P106"}


def f(v, d=4):
    texto = f"{v:.{d}f}"
    return texto[1:] if texto.startswith("-") and float(texto) == 0 else texto


def miles(v):
    return f"{int(round(v)):,}".replace(",", " ")


DOMINIOS = {1: "Costa Norte", 2: "Costa Centro", 3: "Costa Sur", 4: "Sierra Norte", 5: "Sierra Centro",
            6: "Sierra Sur", 7: "Selva", 8: "Lima Metropolitana"}
DESCRIPTIVAS = ["mieperho", "n_menores", "ratio_dependencia", "educ_prom", "tasa_analfabetismo", "tasa_ocupacion",
                "tasa_informalidad", "hacinamiento", "piso_tierra", "agua_red", "desague_red",
                "combustible_solido", "alquiler_imputado", "solo_sis", "juntos", "rural"]


def _internet_anual() -> dict[int, float]:
    """% de hogares con conexión a internet (P1144) por año, ponderado por FACTOR07.

    Documenta por qué la variable se excluye: desde 2023 la pregunta incluye el internet móvil.
    """
    h = pd.read_parquet(RAIZ / "datos/procesados/hogares.parquet", columns=["anio", "internet", "factor07"]).dropna()
    h["con"] = h["internet"] * h["factor07"]
    por_anio = h.groupby("anio")[["con", "factor07"]].sum()
    return {int(a): float(100 * r.con / r.factor07) for a, r in por_anio.iterrows()}


def _distintos() -> int:
    h = pd.read_parquet(RAIZ / "datos/procesados/hogares.parquet", columns=["conglome", "vivienda", "hogar"])
    return len(h.drop_duplicates())


def _por_area() -> pd.DataFrame:
    """Desempeño del modelo principal en la prueba por área y dominio geográfico."""
    import sys
    sys.path.insert(0, str(RAIZ / "src"))
    from pobreza.evaluation import metrics
    pred = pd.read_parquet(RAIZ / "resultados/modelos/predicciones.parquet")
    principal = json.load(open(WEB / "meta.json", encoding="utf-8"))["estimador"]
    t = pred[(pred.pliegue == "Prueba final") & (pred.estimador == principal)]
    grupos = [("Urbana", t[t.rural == 0]), ("Rural", t[t.rural == 1])]
    grupos += [(DOMINIOS[d], t[t.dominio == d]) for d in sorted(t.dominio.unique())]
    filas = []
    for nombre, g in grupos:
        m = metrics.metricas(g)
        filas.append([nombre, len(g), m["auc_roc"], m["recall"], m["precision"], m["tasa_real"], m["tasa_predicha"]])
    return pd.DataFrame(filas, columns=["grupo", "hogares", "auc", "recall", "prec", "real", "estim"])


def _descriptivo(anio: int) -> pd.DataFrame:
    """Promedios ponderados (FACTOR07) de variables clave para hogares pobres y no pobres."""
    import numpy as np
    h = pd.read_parquet(RAIZ / "datos/procesados/hogares.parquet")
    t = h[h.anio == anio]
    etiquetas = {x["Variable"]: x["Etiqueta"] for x in json.load(open(WEB / "metodologia.json", encoding="utf-8"))["variables"]}
    filas = []
    for v in DESCRIPTIVAS:
        def media(g):
            s = g[[v, "factor07"]].dropna()
            return np.average(s[v], weights=s["factor07"])
        filas.append([v, etiquetas.get(v, v), media(t[t.pobre == 1]), media(t[t.pobre == 0])])
    return pd.DataFrame(filas, columns=["v", "etiqueta", "pobres", "no_pobres"])


def cargar() -> dict:
    lee = lambda n: pd.read_csv(D / f"{n}.csv")
    anual = lee("incidencia_anual")
    meta = json.load(open(WEB / "meta.json", encoding="utf-8"))
    panel = pd.read_csv(RAIZ / "datos/procesados/resumen_panel.csv")
    expl = json.load(open(WEB / "explicabilidad.json", encoding="utf-8"))
    meto = json.load(open(WEB / "metodologia.json", encoding="utf-8"))
    resumen = json.load(open(D / "resumen_evaluacion.json", encoding="utf-8"))
    imp = pd.DataFrame(expl["importancia"])
    con = imp[imp["signo_esperado"].isin(["+", "-"])]
    pliegues = []
    for p in meto["pliegues"]:
        nombre = "Prueba final" if p["Pliegue"].startswith("Prueba") else p["Pliegue"]
        pliegues.append({"nombre": nombre, "entrena": p["Entrenamiento"], "calibra": p["Calibración"],
                         "evalua": p["Evaluación"]})
    R = {
        "obs": miles(panel["hogares"].sum()),
        "hog_min": miles(panel["hogares"].min()), "hog_max": miles(panel["hogares"].max()),
        "distintos": miles(_distintos()),
        "pct_rep": f(100 * panel["repetidos"].sum() / panel["hogares"].sum(), 1),
        "rep_min": f(panel.loc[panel.anio > 2017, "pct_repetidos"].min(), 1),
        "rep_max": f(panel["pct_repetidos"].max(), 1),
        "n_vars": len(resumen["predictores"]), "ocupinf": "93.6 % a 94.6 %",
        "internet_anual": _internet_anual(),
        "pliegues": pliegues, "umbral": f(meta["umbral"], 3),
        "anual": anual, "panel": panel, "imp": imp,
        "n_signo": len(con), "n_coincide": int((con["signo_esperado"] == con["signo_observado"]).sum()),
        "discordantes": con[con["signo_esperado"] != con["signo_observado"]],
        "puente": pd.DataFrame(meto["puente"]), "fuga": pd.DataFrame(meto["fuga"]),
        "variables": pd.DataFrame(meto["variables"]),
        "vif": lee("vif"), "comparacion": lee("comparacion_modelos"), "pliegues_m": lee("metricas_pliegues"),
        "prueba": lee("metricas_prueba"), "delong": lee("prueba_delong"),
        "sensibilidad": lee("sensibilidad_alquiler"), "confusion": lee("matriz_confusion"),
        "sesgo": lee("sesgo_departamental"), "periodos": lee("shap_periodos"),
        "area": lee("incidencia_area"), "res": resumen,
        "por_area": _por_area(), "descriptivo": _descriptivo(meta["anio_prueba"]),
    }
    m = resumen["metricas_prueba"]
    R["m"] = m
    s = resumen["sesgo_regional"]
    R["sesgo_res"] = s
    return R
