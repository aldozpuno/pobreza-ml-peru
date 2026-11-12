"""Anexo 1: matriz de consistencia y operacionalización de variables.

Los indicadores de la variable independiente salen del catálogo de variables del modelo
(`config/features.yaml`, leído desde `web/public/data/metodologia.json`), de modo que el anexo
lista exactamente los predictores del modelo final. Las dimensiones son las del capítulo II.
"""

from __future__ import annotations

import copy

from docx.oxml.ns import qn

ESPACIO = "{http://www.w3.org/XML/1998/namespace}space"

# Dimensión de la tesis → grupos del catálogo que la componen (en el orden del anexo).
DIMENSIONES = [
    ("Económica – laboral", ("trabajo",)),
    ("Social – capital humano", ("capital_humano",)),
    ("Social – salud y protección social", ("salud", "programas")),
    ("Social – vivienda y servicios básicos", ("vivienda", "servicios", "activos")),
    ("Demográfica", ("demografia",)),
    ("Geográfica", ("territorio",)),
]
INSTRUMENTO = {"sumaria": "Sumaria (Mód. 34)", "vivienda": "Mód. 100", "miembros": "Mód. 200",
               "educacion": "Mód. 300", "salud": "Mód. 400", "empleo": "Mód. 500", "programas": "Mód. 700"}

DICOTOMICA = "Nominal dicotómica (0/1)"
CONTEO = "Razón (conteo)"
PROPORCION = "Razón (proporción 0–1)"
ESCALA = {
    "dominio": "Nominal (8 categorías)", "estrato": "Ordinal (1–8)", "rural": DICOTOMICA,
    "departamento": "Nominal (25 categorías)", "covid": DICOTOMICA,
    "mieperho": CONTEO, "n_menores": CONTEO, "n_mayores": CONTEO, "ratio_dependencia": "Razón",
    "jefe_mujer": DICOTOMICA, "edad_jefe": "Razón (años)",
    "educ_prom": "Razón (años)", "educ_max": "Razón (años)", "tasa_analfabetismo": PROPORCION,
    "asistencia_menores": PROPORCION,
    "tiene_seguro": DICOTOMICA, "solo_sis": PROPORCION, "n_cronicos": CONTEO,
    "tasa_ocupacion": PROPORCION, "n_informales": CONTEO, "tasa_informalidad": PROPORCION,
    "jefe_independiente": DICOTOMICA,
    "tipo_vivienda": "Nominal (8 categorías)", "pared_precaria": DICOTOMICA, "piso_tierra": DICOTOMICA,
    "habitaciones": CONTEO, "hacinamiento": "Razón (personas por habitación)",
    "alquiler_imputado": "Razón (S/ al mes)", "agua_red": DICOTOMICA, "desague_red": DICOTOMICA,
    "electricidad": DICOTOMICA, "combustible_solido": DICOTOMICA, "celular": DICOTOMICA,
    "tv_cable": DICOTOMICA,
    "juntos": DICOTOMICA, "pension65": DICOTOMICA, "qali_warma": DICOTOMICA, "vaso_leche": DICOTOMICA,
}
NOTA = ("Fuente de todos los indicadores: microdatos de la Encuesta Nacional de Hogares (ENAHO) 2017–2024, "
        "INEI. Entre corchetes, el nombre de la variable en la base procesada; su definición está en el "
        "diccionario de variables del capítulo IV. No se incluyen la brecha educativa ni el índice de "
        "privación, que son combinación lineal exacta de otras variables, ni la conexión a internet (P1144), "
        "que desde 2023 cuenta el internet móvil y no es comparable entre años.")


def _texto(e) -> str:
    return "".join(t.text or "" for t in e.iter(qn("w:t")))


def _run_modelo(celda):
    """Copia de un run de la celda, solo con su formato y un texto."""
    r = copy.deepcopy(next(celda.iter(qn("w:r"))))
    for hijo in list(r):
        if hijo.tag not in (qn("w:rPr"), qn("w:t")):
            r.remove(hijo)
    for t in r.findall(qn("w:t"))[1:]:
        r.remove(t)
    return r


def _run(modelo, texto):
    r = copy.deepcopy(modelo)
    t = r.find(qn("w:t"))
    t.text = texto
    t.set(ESPACIO, "preserve")
    return r


def _poner(celda, textos, modelo) -> None:
    """Deja en la celda un párrafo por texto (uno vacío si la lista está vacía)."""
    parrafos = celda.findall(qn("w:p"))
    base = copy.deepcopy(parrafos[0])
    for hijo in list(base):
        if hijo.tag != qn("w:pPr"):
            base.remove(hijo)
    for p in parrafos:
        celda.remove(p)
    for texto in (textos or [""]):
        p = copy.deepcopy(base)
        if texto:
            p.append(_run(modelo, texto))
        celda.append(p)


def _combinar(celda, inicia: bool) -> None:
    """Marca la celda como inicio o continuación de una combinación vertical."""
    pr = celda.find(qn("w:tcPr"))
    vm = pr.find(qn("w:vMerge"))
    if vm is None:
        vm = pr.makeelement(qn("w:vMerge"), {})
        pr.append(vm)
    if inicia:
        vm.set(qn("w:val"), "restart")
    elif qn("w:val") in vm.attrib:
        del vm.attrib[qn("w:val")]


def _por_dimension(variables):
    """[(dimensión, [fila del catálogo, …]), …] con las variables activas del modelo."""
    filas = variables.to_dict("records")
    salida = [(dim, [v for v in filas if v["Grupo"] in grupos]) for dim, grupos in DIMENSIONES]
    usadas = sum(len(vs) for _, vs in salida)
    if usadas != len(filas):
        print("AVISO: hay variables del catálogo sin dimensión en el Anexo 1:",
              sorted({v["Grupo"] for v in filas} - {g for _, gs in DIMENSIONES for g in gs}))
    return salida


def _tabla(body, primera_celda: str, segunda_celda: str):
    for t in body.iter(qn("w:tbl")):
        celdas = t.find(qn("w:tr")).findall(qn("w:tc"))
        if len(celdas) > 1 and _texto(celdas[0]).strip() == primera_celda and _texto(celdas[1]).strip() == segunda_celda:
            return t
    raise ValueError(f"no se encontró la tabla que empieza con {primera_celda}")


def _matriz(body, dimensiones) -> None:
    tabla = _tabla(body, "PROBLEMA GENERAL", "OBJETIVO GENERAL")
    for t in tabla.iter(qn("w:t")):  # el código no calcula el PSI
        if t.text and "VIF y PSI" in t.text:
            t.text = t.text.replace("VIF y PSI", "VIF")
    filas = tabla.findall(qn("w:tr"))
    por_nombre = dict(dimensiones)
    hechas = 0
    for fila in filas:
        celdas = fila.findall(qn("w:tc"))
        if len(celdas) < 6:
            continue
        nombre = _texto(celdas[4]).strip()
        if nombre in por_nombre:
            _poner(celdas[5], [v["Etiqueta"] for v in por_nombre[nombre]], _run_modelo(celdas[5]))
            hechas += 1
    if hechas != len(dimensiones):
        print(f"AVISO: matriz de consistencia: se actualizaron {hechas} de {len(dimensiones)} dimensiones")


def _operacionalizacion(body, dimensiones) -> int:
    tabla = _tabla(body, "VARIABLE", "DEFINICIÓN")
    filas = tabla.findall(qn("w:tr"))
    primera, continua = copy.deepcopy(filas[2]), copy.deepcopy(filas[3])
    modelo = _run_modelo(filas[3].findall(qn("w:tc"))[3])
    for fila in filas[2:]:
        tabla.remove(fila)
    n = 0
    for dimension, variables in dimensiones:
        for k, v in enumerate(variables):
            n += 1
            fila = copy.deepcopy(primera if n == 1 else continua)
            celdas = fila.findall(qn("w:tc"))
            _combinar(celdas[2], inicia=k == 0)
            _poner(celdas[2], [dimension] if k == 0 else [], modelo)
            _poner(celdas[3], [f"X{n}: {v['Etiqueta']} [{v['Variable']}]"], modelo)
            _poner(celdas[4], [ESCALA[v["Variable"]]], modelo)
            _poner(celdas[5], ["Ficha de registro de datos – ENAHO, " + INSTRUMENTO[v["Módulo ENAHO"]]], modelo)
            tabla.append(fila)
    return n


def actualizar(body, R) -> None:
    dimensiones = _por_dimension(R["variables"])
    _matriz(body, dimensiones)
    n = _operacionalizacion(body, dimensiones)
    for p in body.iter(qn("w:p")):
        if _texto(p).startswith("Nota. Fuente de todos los indicadores"):
            ts = list(p.iter(qn("w:t")))
            ts[1].text = NOTA
            for t in ts[2:]:
                t.text = ""
    print(f"anexo 1: {n} indicadores en la operacionalización, {len(dimensiones)} dimensiones")
