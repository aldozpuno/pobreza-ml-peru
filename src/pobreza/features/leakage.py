"""Control de fuga de datos: ninguna variable que defina la pobreza entra al modelo."""

from __future__ import annotations

from pobreza.config import Config


class FugaDeDatosError(ValueError):
    """Se intentó usar como predictor una variable que contiene la respuesta."""


def prohibidas(config: Config) -> set[str]:
    return {item["nombre"] for item in config.fuga_de_datos}


def verificar(config: Config, predictores: list[str]) -> None:
    """Detiene el pipeline si algún predictor está en la lista de fuga de datos."""
    conflicto = sorted(set(predictores) & prohibidas(config))
    if conflicto:
        raise FugaDeDatosError(
            f"Variables con fuga de datos entre los predictores: {conflicto}. "
            "Quítelas de config/features.yaml.")
