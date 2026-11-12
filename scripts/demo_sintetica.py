"""Corre el pipeline completo con datos sintéticos, sin conexión al INEI.

Sirve para revisar el código y las figuras sin los microdatos. Todo queda en `demo/`;
la web (`web/public/data/`) conserva los resultados reales.

    python scripts/demo_sintetica.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tests"))

import synthetic  # noqa: E402

from pobreza.cli import ejecutar  # noqa: E402
from pobreza.config import cargar_config  # noqa: E402


def main() -> None:
    demo = RAIZ / "demo"
    if demo.exists():
        shutil.rmtree(demo)
    shutil.copytree(RAIZ / "config", demo / "config")
    config = cargar_config(demo)
    synthetic.generar(config.rutas.crudos, config.anios, hogares_por_anio=1500)
    ejecutar("todo", str(demo), estricto=False, origen="sintetico")
    # No se copian a web/public/data para no reemplazar los resultados reales.
    print(f"Listo. Resultados en {demo}; JSON de ejemplo en {config.rutas.dashboard}")


if __name__ == "__main__":
    main()
