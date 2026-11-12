"""Incidencia de la pobreza monetaria (método del Taller 6 del asesor y del INEI).

    Tasa (%) = 100 × Σ (pobre_i × MIEPERHO_i × FACTOR07_i) / Σ (MIEPERHO_i × FACTOR07_i)

Se calcula también la tasa de hogares (peso FACTOR07) y la muestral (sin pesos) para
mostrar por qué no son equivalentes: los hogares pobres tienen más miembros, así que la
proporción de hogares pobres es menor que la de personas pobres.
"""

from __future__ import annotations

import pandas as pd

from pobreza.config import Config
from pobreza.logging_utils import obtener

log = obtener("measurement.poverty")


class ObjetivoInvalidoError(ValueError):
    """La variable objetivo no reproduce la incidencia oficial del INEI."""


def _tasa(grupo: pd.DataFrame, columna: str, peso: str | None) -> float:
    if peso is None:
        return 100 * grupo[columna].mean()
    return 100 * (grupo[columna] * grupo[peso]).sum() / grupo[peso].sum()


def incidencia(hogares: pd.DataFrame, por: list[str] | None = None,
               columna: str = "pobre") -> pd.DataFrame:
    """Tasas por grupo: personas (oficial), hogares y muestral; y población expandida."""
    por = por or ["anio"]
    filas = []
    for clave, grupo in hogares.groupby(por):
        clave = clave if isinstance(clave, tuple) else (clave,)
        filas.append({
            **dict(zip(por, clave)),
            "hogares_muestra": len(grupo),
            "poblacion_expandida": grupo["peso_personas"].sum(),
            "pobres_expandidos": (grupo[columna] * grupo["peso_personas"]).sum(),
            "tasa_personas": _tasa(grupo, columna, "peso_personas"),
            "tasa_hogares": _tasa(grupo, columna, "peso_hogar"),
            "tasa_muestral": _tasa(grupo, columna, None),
        })
    return pd.DataFrame(filas)


def comparar_con_oficial(config: Config, tabla: pd.DataFrame) -> pd.DataFrame:
    """Agrega la cifra oficial del INEI y la diferencia en puntos porcentuales."""
    oficial = config.medicion["incidencia_oficial"]
    tabla = tabla.copy()
    tabla["tasa_oficial_inei"] = tabla["anio"].map(oficial)
    tabla["diferencia_pp"] = tabla["tasa_personas"] - tabla["tasa_oficial_inei"]
    return tabla


def validar(config: Config, tabla: pd.DataFrame, estricto: bool = True) -> pd.DataFrame:
    """Compara con el INEI; si alguna diferencia supera la tolerancia, detiene el pipeline."""
    tabla = comparar_con_oficial(config, tabla)
    tolerancia = float(config.medicion["tolerancia_pp"])
    fuera = tabla[tabla["diferencia_pp"].abs() > tolerancia]
    for _, fila in tabla.iterrows():
        log.info("%d | tasa personas %.2f %% | INEI %.1f %% | diferencia %+.2f pp",
                 fila["anio"], fila["tasa_personas"], fila["tasa_oficial_inei"],
                 fila["diferencia_pp"])
    if not fuera.empty:
        mensaje = (f"La variable objetivo no reproduce al INEI en {fuera['anio'].tolist()} "
                   f"(tolerancia {tolerancia} pp). Revise la Sumaria antes de entrenar.")
        if estricto:
            raise ObjetivoInvalidoError(mensaje)
        log.warning(mensaje)
    return tabla
