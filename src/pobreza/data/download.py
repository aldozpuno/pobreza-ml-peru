"""Descarga de los zips de la ENAHO desde el portal de microdatos del INEI.

Cada módulo de cada año se guarda en `datos/crudos/<año>/<módulo>.zip`.
Si el archivo ya existe y es un zip válido, no se vuelve a descargar.
Si el portal no responde, se pueden copiar los zips a mano en esa misma carpeta.
"""

from __future__ import annotations

import time
import zipfile
from pathlib import Path

import requests

from pobreza.config import Config
from pobreza.data.catalog import MODULOS, url_descarga
from pobreza.logging_utils import obtener

log = obtener("data.download")


def ruta_zip(config: Config, anio: int, nombre_modulo: str) -> Path:
    return config.rutas.crudos / str(anio) / f"{nombre_modulo}.zip"


def _es_zip_valido(ruta: Path) -> bool:
    return ruta.exists() and ruta.stat().st_size > 0 and zipfile.is_zipfile(ruta)


def _bajar(url: str, destino: Path, reintentos: int, timeout: int) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = destino.with_suffix(".part")
    for intento in range(1, reintentos + 1):
        try:
            with requests.get(url, stream=True, timeout=timeout) as respuesta:
                respuesta.raise_for_status()
                with open(temporal, "wb") as archivo:
                    for bloque in respuesta.iter_content(chunk_size=1 << 20):
                        archivo.write(bloque)
            if not zipfile.is_zipfile(temporal):
                raise ValueError("el servidor no devolvió un zip")
            temporal.replace(destino)
            return
        except (requests.RequestException, ValueError) as error:
            log.warning("Intento %d/%d falló para %s: %s", intento, reintentos, url, error)
            time.sleep(5 * intento)
    raise RuntimeError(f"No se pudo descargar {url}. Copie el zip a mano en {destino}.")


def descargar_modulo(config: Config, anio: int, nombre_modulo: str) -> Path:
    """Descarga un módulo de un año (si hace falta) y devuelve la ruta del zip."""
    destino = ruta_zip(config, anio, nombre_modulo)
    if _es_zip_valido(destino):
        log.info("%s %s ya descargado", anio, nombre_modulo)
        return destino
    info = config.descarga
    url = url_descarga(info["url_base"], info["formato"], config.codigo_inei(anio),
                       MODULOS[nombre_modulo].numero_portal)
    log.info("Descargando %s %s desde %s", anio, nombre_modulo, url)
    _bajar(url, destino, int(info.get("reintentos", 3)), int(info.get("timeout_seg", 600)))
    return destino


def descargar_todo(config: Config, modulos: list[str] | None = None) -> list[Path]:
    """Descarga todos los módulos de todos los años configurados."""
    modulos = modulos or list(MODULOS)
    rutas = []
    for anio in config.anios:
        for nombre in modulos:
            rutas.append(descargar_modulo(config, anio, nombre))
    return rutas
