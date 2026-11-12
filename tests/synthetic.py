"""Generador de microdatos sintéticos con la estructura de la ENAHO.

Produce, para cada año, los mismos archivos Stata que publica el INEI (Sumaria y módulos
100, 200, 300, 400, 500 y 700) dentro de zips, con los nombres de columna en mayúscula
como en los originales. La pobreza depende de las características del hogar, y una parte
de los hogares se repite de un año al siguiente con PANEL = 1, para probar su detección.

Los datos son inventados: sirven solo para probar el código.
"""

from __future__ import annotations

import io
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ARCHIVOS = {
    "sumaria": "Sumaria-{a}.dta", "vivienda": "Enaho01-{a}-100.dta",
    "miembros": "Enaho01-{a}-200.dta", "educacion": "Enaho01A-{a}-300.dta",
    "salud": "Enaho01A-{a}-400.dta", "empleo": "Enaho01A-{a}-500.dta",
    "programas": "Enaho01-{a}-700.dta",
}


def _hogares(rng, n: int, anio: int, previos: pd.DataFrame | None) -> pd.DataFrame:
    """Hogares del año; ~30 % repite la llave del año anterior (submuestra panel)."""
    nuevos = pd.DataFrame({
        "CONGLOME": rng.integers(1, 9999, n).astype(str),
        "VIVIENDA": rng.integers(1, 200, n).astype(str),
        "HOGAR": "11",
        "rural": rng.random(n) < 0.3,
        "educ": rng.integers(0, 17, n),
        "mieperho": rng.integers(1, 9, n),
        "dep": rng.integers(1, 26, n),
    })
    nuevos["PANEL"] = 2
    if previos is not None:
        repetidos = previos.sample(frac=0.3, random_state=anio).assign(PANEL=1)
        nuevos = pd.concat([repetidos, nuevos.iloc[len(repetidos):]], ignore_index=True)
    nuevos = nuevos.drop_duplicates(["CONGLOME", "VIVIENDA", "HOGAR"]).reset_index(drop=True)
    latente = (-0.5 + 1.4 * nuevos["rural"] - 0.18 * nuevos["educ"] + 0.35 * nuevos["mieperho"]
               + (0.6 if anio == 2020 else 0) + rng.normal(0, 1.4, len(nuevos)))
    nuevos["pobre"] = latente > 0.4
    return nuevos


def _modulos(rng, h: pd.DataFrame, anio: int) -> dict[str, pd.DataFrame]:
    n = len(h)
    llave = h[["CONGLOME", "VIVIENDA", "HOGAR"]]
    pobre, rural = h["pobre"].to_numpy(), h["rural"].to_numpy()
    estrato = np.where(rural, rng.integers(6, 9, n), rng.integers(1, 6, n))
    sumaria = llave.assign(
        UBIGEO=[f"{d:02d}0101" for d in h["dep"]], DOMINIO=rng.integers(1, 9, n),
        ESTRATO=estrato, POBREZA=np.where(pobre, rng.choice([1, 2], n, p=[.2, .8]), 3),
        MIEPERHO=h["mieperho"], TOTMIEHO=h["mieperho"], FACTOR07=rng.uniform(50, 400, n),
        LINEA=400.0, LINPE=200.0, GASHOG2D=np.where(pobre, 8000.0, 30000.0))
    def bin_(p):  # 1/2 con probabilidad p de "1"
        return np.where(rng.random(n) < p, 1, 2)
    vivienda = llave.assign(
        RESULT=1, PANEL=h["PANEL"], P101=rng.integers(1, 8, n),
        P102=np.where(rng.random(n) < 0.2 + 0.15 * pobre, 5, 1),
        P103=np.where(rng.random(n) < 0.2 + 0.2 * pobre, 6, 2), P104=rng.integers(1, 5, n),
        P106=np.round(np.exp(rng.normal(6.0 - 0.5 * pobre, 0.7, n))),
        P110=np.where(rng.random(n) < 0.8 - 0.4 * rural, 1, 6), P110A1=bin_(0.7),
        P111A=np.where(rng.random(n) < 0.7 - 0.4 * rural, 1, 6), P1121=bin_(0.9),
        P1135=0, P1136=np.where(rng.random(n) < 0.6 * rural, 1, 0), P1139=0,
        P1142=bin_(0.9), P1143=bin_(0.3 - 0.1 * pobre), P1144=bin_(0.5 - 0.15 * pobre))
    personas = h.loc[h.index.repeat(h["mieperho"])].reset_index(drop=True)
    personas["CODPERSO"] = personas.groupby(["CONGLOME", "VIVIENDA", "HOGAR"]).cumcount() + 1
    m = len(personas)
    edad = np.where(personas["CODPERSO"] == 1, rng.integers(25, 80, m), rng.integers(0, 80, m))
    base = personas[["CONGLOME", "VIVIENDA", "HOGAR", "CODPERSO"]].assign(P208A=edad)
    jefe = np.where(personas["CODPERSO"] == 1, 1, 3)
    miembros = base.assign(P203=jefe, P204=1, P205=2, P206=np.nan, P207=rng.integers(1, 3, m))
    nivel = np.clip(personas["educ"].to_numpy() // 2 + rng.integers(-1, 2, m), 1, 11)
    educacion = base.assign(P301A=nivel, P302=np.where(nivel <= 2, 2, 1),
                            P306=np.where(rng.random(m) < 0.9, 1, 2))
    seguros = {f"P419{i}": np.where(rng.random(m) < (0.6 if i == 5 else 0.1), 1, 0)
               for i in range(1, 9)}
    salud = base.assign(P401=np.where(rng.random(m) < 0.3, 1, 2), **seguros)
    adultos = base[edad >= 14].copy()
    k = len(adultos)
    empleo = adultos.assign(P203=jefe[edad >= 14], OCU500=np.where(rng.random(k) < .7, 1, 4),
                            P507=rng.integers(1, 7, k), P510A1=rng.choice([1, 2, 3], k),
                            P558A5=rng.choice([0, 5], k))
    programas = llave.assign(P701_01=np.where(rng.random(n) < .2 + .3 * pobre, 1, 0),
                             P701_03=0, P701_04=np.where(rng.random(n) < .3, 1, 0),
                             P710_04=np.where(rng.random(n) < .05 + .15 * pobre, 1, 0),
                             P710_05=np.where(rng.random(n) < .1, 1, 0))
    return {"sumaria": sumaria, "vivienda": vivienda, "miembros": miembros,
            "educacion": educacion, "salud": salud, "empleo": empleo, "programas": programas}


def _a_zip(datos: pd.DataFrame, nombre: str, destino: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        ruta = Path(tmp) / nombre
        pyreadstat.write_dta(datos, str(ruta))
        destino.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(destino, "w") as archivo:
            archivo.write(ruta, f"carpeta/{nombre}")
            archivo.writestr("carpeta/Diccionario.pdf", io.BytesIO(b"pdf").getvalue())


def generar(carpeta_crudos: Path, anios: list[int], hogares_por_anio: int = 800,
            semilla: int = 7) -> None:
    """Escribe `<carpeta_crudos>/<año>/<módulo>.zip` para cada año y módulo."""
    rng = np.random.default_rng(semilla)
    previos = None
    for anio in anios:
        h = _hogares(rng, hogares_por_anio, anio, previos)
        for modulo, datos in _modulos(rng, h, anio).items():
            _a_zip(datos, ARCHIVOS[modulo].format(a=anio), carpeta_crudos / str(anio)
                   / f"{modulo}.zip")
        previos = h.drop(columns="PANEL")
