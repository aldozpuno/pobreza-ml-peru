"""Variables que se construyen combinando módulos (requieren la base ya unida).

    hacinamiento     = MIEPERHO / habitaciones, recortado en 10 personas por habitación
    indice_privacion = promedio de seis carencias de la vivienda (0 = ninguna, 1 = todas)

Corrige el código original de la tesis, que dividía por P103 (material del piso) en
lugar de P104 (habitaciones) y usaba P102 y P101 para piso y paredes.
"""

from __future__ import annotations

import pandas as pd

TOPE_HACINAMIENTO = 10.0

CARENCIAS = {
    "sin_agua_red": ("agua_red", 0),
    "sin_desague_red": ("desague_red", 0),
    "sin_electricidad": ("electricidad", 0),
    "piso_tierra": ("piso_tierra", 1),
    "pared_precaria": ("pared_precaria", 1),
    "combustible_solido": ("combustible_solido", 1),
}


def hacinamiento(datos: pd.DataFrame) -> pd.Series:
    return (datos["mieperho"] / datos["habitaciones"]).clip(upper=TOPE_HACINAMIENTO)


def indice_privacion(datos: pd.DataFrame) -> pd.Series:
    """Proporción de carencias presentes entre las que tienen dato."""
    carencias = pd.DataFrame({
        nombre: (datos[columna] == valor_carencia).astype(float).where(datos[columna].notna())
        for nombre, (columna, valor_carencia) in CARENCIAS.items()
    })
    return carencias.mean(axis=1, skipna=True)


def agregar_derivadas(datos: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una copia con las variables derivadas agregadas."""
    datos = datos.copy()
    datos["hacinamiento"] = hacinamiento(datos)
    datos["indice_privacion"] = indice_privacion(datos)
    return datos
