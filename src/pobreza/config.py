"""Carga de la configuración del proyecto.

Lee los tres archivos YAML de `config/` y los expone como un objeto `Config`.
Todas las rutas se resuelven respecto a la raíz del proyecto, de modo que el
pipeline funciona igual en una computadora local y en Google Colab.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

RAIZ_POR_DEFECTO = Path(__file__).resolve().parents[2]


def _leer_yaml(ruta: Path) -> dict[str, Any]:
    with open(ruta, encoding="utf-8") as archivo:
        return yaml.safe_load(archivo) or {}


@dataclass
class Rutas:
    """Carpetas de trabajo; se crean al usarlas."""

    raiz: Path
    crudos: Path
    intermedios: Path
    procesados: Path
    modelos: Path
    reportes: Path
    dashboard: Path

    @classmethod
    def desde_dict(cls, raiz: Path, datos: dict[str, str]) -> "Rutas":
        return cls(raiz=raiz, **{clave: raiz / valor for clave, valor in datos.items()})

    def asegurar(self) -> None:
        for ruta in (self.crudos, self.intermedios, self.procesados,
                     self.modelos, self.reportes, self.dashboard):
            ruta.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Configuración completa del pipeline."""

    raiz: Path
    anios: list[int]
    rutas: Rutas
    descarga: dict[str, Any]
    medicion: dict[str, Any]
    panel: dict[str, Any]
    semilla: int
    modelo: dict[str, Any]
    variables: list[dict[str, Any]]
    teorias: dict[str, str]
    fuga_de_datos: list[dict[str, str]]
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def anio_prueba(self) -> int:
        return int(self.modelo["anio_prueba"])

    def codigo_inei(self, anio: int) -> int:
        return int(self.descarga["codigos_inei"][anio])

    def variables_activas(self) -> list[str]:
        return [v["nombre"] for v in self.variables if v.get("activa", True)]


def cargar_config(raiz: str | Path | None = None) -> Config:
    """Lee `config/pipeline.yaml`, `config/model.yaml` y `config/features.yaml`."""
    raiz = Path(raiz) if raiz else RAIZ_POR_DEFECTO
    carpeta = raiz / "config"
    pipeline = _leer_yaml(carpeta / "pipeline.yaml")
    modelo = _leer_yaml(carpeta / "model.yaml")
    catalogo = _leer_yaml(carpeta / "features.yaml")

    descarga = pipeline["descarga"]
    descarga["codigos_inei"] = {int(k): int(v) for k, v in descarga["codigos_inei"].items()}
    medicion = pipeline["medicion"]
    medicion["incidencia_oficial"] = {
        int(k): float(v) for k, v in medicion["incidencia_oficial"].items()
    }

    return Config(
        raiz=raiz,
        anios=[int(a) for a in pipeline["anios"]],
        rutas=Rutas.desde_dict(raiz, pipeline["rutas"]),
        descarga=descarga,
        medicion=medicion,
        panel=pipeline["panel"],
        semilla=int(pipeline.get("semilla", 42)),
        modelo=modelo,
        variables=catalogo["variables"],
        teorias=catalogo["teorias"],
        fuga_de_datos=catalogo["fuga_de_datos"],
    )
