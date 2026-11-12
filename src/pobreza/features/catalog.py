"""Catálogo de variables (config/features.yaml) como tablas para la tesis.

De aquí salen:
    - la lista de predictores que usa el modelo,
    - el diccionario de variables (Tabla 1 de la tesis),
    - la tabla puente teoría → variables (observación del asesor sobre el marco teórico).
"""

from __future__ import annotations

import pandas as pd

from pobreza.config import Config
from pobreza.features.leakage import verificar


def predictores(config: Config, excluir: tuple[str, ...] = ()) -> list[str]:
    """Variables activas del catálogo, menos las excluidas, ya verificadas contra fuga."""
    lista = [v for v in config.variables_activas() if v not in excluir]
    verificar(config, lista)
    return lista


def categoricas(config: Config) -> list[str]:
    """Variables codificadas cuyo número no tiene orden (se tratan como categorías)."""
    return [n for n in ("dominio", "departamento", "tipo_vivienda")
            if n in config.variables_activas()]


def etiquetas(config: Config) -> dict[str, str]:
    """Nombre en código → etiqueta legible en español (para figuras y dashboard)."""
    return {v["nombre"]: v.get("etiqueta", v["nombre"]) for v in config.variables}


def diccionario(config: Config) -> pd.DataFrame:
    """Tabla de variables: nombre, módulo, grupo, definición, teoría y signo esperado."""
    filas = [{
        "Variable": v["nombre"],
        "Etiqueta": v.get("etiqueta", v["nombre"]),
        "Módulo ENAHO": v["modulo"],
        "Grupo": v["grupo"],
        "Definición": v["definicion"],
        "Teoría": config.teorias.get(v["teoria"], v["teoria"]),
        "Signo esperado": v["signo"],
    } for v in config.variables if v.get("activa", True)]
    return pd.DataFrame(filas)


def tabla_puente(config: Config) -> pd.DataFrame:
    """Teoría → variables que la operacionalizan (una fila por teoría)."""
    dic = diccionario(config)
    return (dic.groupby("Teoría", sort=False)
            .agg(Variables=("Etiqueta", lambda s: ", ".join(s)),
                 Cantidad=("Variable", "size"))
            .reset_index())
