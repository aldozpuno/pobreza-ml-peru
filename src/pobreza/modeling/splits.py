"""Validación temporal con ventana expansiva (walk-forward).

Cada pliegue tiene tres partes que nunca se mezclan:
    entrenamiento → todos los años anteriores al de calibración
    calibración   → un año: ajusta probabilidades (isotónica) y elige el umbral
    validación    → el año siguiente, que el modelo nunca vio

Con 2017–2024 y primer año de validación 2020:
    Pliegue 1: entrena 2017–2018, calibra 2019, valida 2020
    ...
    Prueba final: entrena 2017–2022, calibra 2023, prueba 2024
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from pobreza.config import Config


@dataclass(frozen=True)
class Pliegue:
    nombre: str
    entrenamiento: tuple[int, ...]
    calibracion: int
    validacion: int
    es_prueba_final: bool = False

    def describir(self) -> str:
        return (f"{self.nombre}: entrena {self.entrenamiento[0]}–{self.entrenamiento[-1]}, "
                f"calibra {self.calibracion}, evalúa {self.validacion}")


def generar_pliegues(config: Config) -> list[Pliegue]:
    """Lista de pliegues; el último es la prueba final con el año de prueba."""
    anios = sorted(config.anios)
    primero = int(config.modelo["validacion"]["primer_anio_validacion"])
    prueba = config.anio_prueba
    pliegues = []
    for numero, anio_val in enumerate(range(primero, prueba + 1), start=1):
        entrenamiento = tuple(a for a in anios if a < anio_val - 1)
        if not entrenamiento:
            raise ValueError(f"No hay años de entrenamiento para validar {anio_val}")
        final = anio_val == prueba
        pliegues.append(Pliegue(
            nombre="Prueba final" if final else f"Pliegue {numero}",
            entrenamiento=entrenamiento,
            calibracion=anio_val - 1,
            validacion=anio_val,
            es_prueba_final=final,
        ))
    return pliegues


def particionar(hogares: pd.DataFrame, pliegue: Pliegue
                ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Devuelve (entrenamiento, calibración, validación) para un pliegue."""
    entrenamiento = hogares[hogares["anio"].isin(pliegue.entrenamiento)]
    calibracion = hogares[hogares["anio"] == pliegue.calibracion]
    validacion = hogares[hogares["anio"] == pliegue.validacion]
    return entrenamiento, calibracion, validacion


def tabla_pliegues(pliegues: list[Pliegue]) -> pd.DataFrame:
    """Tabla del diseño de validación para la tesis."""
    return pd.DataFrame([{
        "Pliegue": p.nombre,
        "Entrenamiento": f"{p.entrenamiento[0]}–{p.entrenamiento[-1]}",
        "Calibración": p.calibracion,
        "Evaluación": p.validacion,
    } for p in pliegues])
