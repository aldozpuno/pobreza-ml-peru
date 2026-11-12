"""Pruebas de los procesadores de módulos con casos pequeños escritos a mano."""

import pandas as pd

from pobreza.features.derived import agregar_derivadas
from pobreza.processing import educacion, keys, miembros, panel, vivienda

LLAVE = {"anio": 2024, "conglome": "000001", "vivienda": "001", "hogar": "11"}


def test_llaves_se_rellenan_con_ceros():
    datos = pd.DataFrame({"conglome": [123.0], "vivienda": ["7"], "hogar": [11]})
    salida = keys.normalizar_llaves(datos)
    assert salida.loc[0, "conglome"] == "000123"
    assert salida.loc[0, "vivienda"] == "007"
    assert salida.loc[0, "hogar"] == "11"


def test_vivienda_usa_los_codigos_correctos():
    fila = {**LLAVE, "panel": 1, "p101": 1, "p102": 5, "p103": 6, "p104": 2, "p106": 120,
            "p110": 1, "p110a1": 1, "p111a": 6, "p1121": 1, "p1135": 0, "p1136": 1,
            "p1139": 0, "p1142": 1, "p1143": 2, "p1144": 2}
    salida = vivienda.procesar(pd.DataFrame([fila])).iloc[0]
    assert salida["piso_tierra"] == 1          # P103 = 6, no P102
    assert salida["pared_precaria"] == 1       # P102 = 5 (quincha)
    assert salida["desague_red"] == 0
    assert salida["combustible_solido"] == 1
    assert salida["entrevistado_anio_anterior"] == 1


def test_hacinamiento_divide_por_habitaciones():
    datos = pd.DataFrame([{"mieperho": 6, "habitaciones": 2, "agua_red": 1, "desague_red": 1,
                           "electricidad": 1, "piso_tierra": 1, "pared_precaria": 0,
                           "combustible_solido": 0}])
    salida = agregar_derivadas(datos).iloc[0]
    assert salida["hacinamiento"] == 3
    assert abs(salida["indice_privacion"] - 1 / 6) < 1e-9


def test_miembros_cuenta_solo_residentes_y_perfil_del_jefe():
    filas = [
        {**LLAVE, "codperso": "01", "p203": 1, "p204": 1, "p205": 2, "p206": None,
         "p207": 2, "p208a": 40},
        {**LLAVE, "codperso": "02", "p203": 3, "p204": 1, "p205": 2, "p206": None,
         "p207": 1, "p208a": 10},
        {**LLAVE, "codperso": "03", "p203": 3, "p204": 1, "p205": 1, "p206": None,
         "p207": 1, "p208a": 20},  # ausente 30 días o más: no es residente
    ]
    salida = miembros.procesar(pd.DataFrame(filas)).iloc[0]
    assert salida["n_residentes"] == 2
    assert salida["n_menores"] == 1
    assert salida["jefe_mujer"] == 1
    assert salida["edad_jefe"] == 40


def test_educacion_convierte_niveles_en_anios():
    filas = [{**LLAVE, "codperso": "01", "p208a": 40, "p301a": 6, "p302": 1, "p306": 2},
             {**LLAVE, "codperso": "02", "p208a": 30, "p301a": 10, "p302": 1, "p306": 2},
             {**LLAVE, "codperso": "03", "p208a": 9, "p301a": 3, "p302": 1, "p306": 1}]
    salida = educacion.procesar(pd.DataFrame(filas)).iloc[0]
    assert salida["educ_prom"] == (11 + 16) / 2   # solo mayores de 15
    assert salida["educ_max"] == 16
    assert salida["asistencia_menores"] == 1


def test_panel_detecta_hogares_repetidos():
    base = pd.DataFrame({"anio": [2023, 2024, 2024], "conglome": ["1", "1", "2"],
                         "vivienda": ["1", "1", "1"], "hogar": ["11", "11", "11"],
                         "entrevistado_anio_anterior": [0, 1, 0]})
    salida = panel.enlazar_entre_anios(base).sort_values(["anio", "conglome"])
    assert salida["repetido"].tolist() == [0, 1, 0]
    assert salida["visto_anio_anterior"].tolist() == [0, 1, 0]
