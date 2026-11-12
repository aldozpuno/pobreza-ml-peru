"""Fixtures compartidas: un proyecto temporal con la configuración real y datos sintéticos."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "tests"))

from pobreza.config import cargar_config  # noqa: E402
import synthetic  # noqa: E402


@pytest.fixture(scope="session")
def proyecto(tmp_path_factory):
    """Carpeta de proyecto con `config/` copiada y zips sintéticos 2017–2024."""
    raiz = tmp_path_factory.mktemp("proyecto")
    shutil.copytree(RAIZ / "config", raiz / "config")
    config = cargar_config(raiz)
    synthetic.generar(config.rutas.crudos, config.anios)
    return config
