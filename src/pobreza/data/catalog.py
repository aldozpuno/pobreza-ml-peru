"""Catálogo de módulos ENAHO: qué número tiene cada módulo en el portal del INEI,
cómo se llama su archivo de datos y qué columnas se necesitan de él.

Los nombres de archivo varían entre años en mayúsculas y prefijos, por eso se
buscan con expresiones regulares sin distinguir mayúsculas.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Modulo:
    """Un módulo de la ENAHO tal como se publica en el portal de microdatos."""

    nombre: str          # nombre interno (vivienda, miembros, ...)
    numero_portal: str   # "01", "02", ... en la URL de descarga
    patron_archivo: str  # regex del archivo de datos dentro del zip
    columnas: tuple[str, ...]  # columnas (en minúscula) que se conservan

    def coincide(self, nombre_archivo: str) -> bool:
        return re.search(self.patron_archivo, nombre_archivo, flags=re.IGNORECASE) is not None


LLAVE_HOGAR = ("conglome", "vivienda", "hogar")
LLAVE_PERSONA = LLAVE_HOGAR + ("codperso",)

MODULOS: dict[str, Modulo] = {
    "sumaria": Modulo(
        "sumaria", "34", r"sumaria-\d{4}\.(dta|csv|sav)$",
        LLAVE_HOGAR + ("ubigeo", "dominio", "estrato", "pobreza", "mieperho", "totmieho",
                       "factor07", "linea", "linpe", "gashog2d"),
    ),
    "vivienda": Modulo(
        "vivienda", "01", r"enaho01-\d{4}-100\.(dta|csv|sav)$",
        LLAVE_HOGAR + ("result", "panel", "p101", "p102", "p103", "p104", "p106", "p110",
                       "p110a1", "p111a", "p1121", "p1135", "p1136", "p1139", "p1142",
                       "p1143", "p1144"),
    ),
    "miembros": Modulo(
        "miembros", "02", r"enaho01-\d{4}-200\.(dta|csv|sav)$",
        LLAVE_PERSONA + ("p203", "p204", "p205", "p206", "p207", "p208a"),
    ),
    "educacion": Modulo(
        "educacion", "03", r"enaho01a-\d{4}-300\.(dta|csv|sav)$",
        LLAVE_PERSONA + ("p208a", "p301a", "p302", "p306"),
    ),
    "salud": Modulo(
        "salud", "04", r"enaho01a-\d{4}-400\.(dta|csv|sav)$",
        LLAVE_PERSONA + ("p401", "p4191", "p4192", "p4193", "p4194", "p4195", "p4196",
                         "p4197", "p4198"),
    ),
    "empleo": Modulo(
        "empleo", "05", r"enaho01a-\d{4}-500\.(dta|csv|sav)$",
        LLAVE_PERSONA + ("p203", "p208a", "ocu500", "p507", "p510a1", "p558a5"),
    ),
    "programas": Modulo(
        "programas", "37", r"enaho01-\d{4}-700\.(dta|csv|sav)$",
        LLAVE_HOGAR + ("p701_01", "p701_03", "p701_04", "p710_04", "p710_05"),
    ),
}


def modulo(nombre: str) -> Modulo:
    """Devuelve el módulo por su nombre interno; falla con un mensaje claro si no existe."""
    try:
        return MODULOS[nombre]
    except KeyError as error:
        disponibles = ", ".join(MODULOS)
        raise KeyError(f"Módulo desconocido '{nombre}'. Disponibles: {disponibles}") from error


def url_descarga(url_base: str, formato: str, codigo_encuesta: int, numero_modulo: str) -> str:
    """URL del zip de un módulo, p. ej. .../descarga/STATA/966-Modulo01.zip (ENAHO 2024)."""
    return f"{url_base}/{formato}/{codigo_encuesta}-Modulo{numero_modulo}.zip"
