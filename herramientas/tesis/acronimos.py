"""Lista de acrónimos: deja solo los que el texto usa y añade los que faltan.

Una sigla se considera usada si aparece fuera de la propia lista y de los índices. Las siglas
nuevas solo se añaden si el texto las usa, de modo que la lista sigue al documento.
"""

from __future__ import annotations

import copy
import re

from docx.oxml.ns import qn

NUEVOS = {
    "AUC-PR": "Área bajo la curva de precisión y exhaustividad",
    "AUC-ROC": "Área bajo la curva característica operativa del receptor",
    "CEPLAN": "Centro Nacional de Planeamiento Estratégico",
    "COVID-19": "Enfermedad por coronavirus de 2019",
    "OIT": "Organización Internacional del Trabajo",
    "SIS": "Seguro Integral de Salud",
    "SUNAT": "Superintendencia Nacional de Aduanas y de Administración Tributaria",
    "VIF": "Factor de inflación de la varianza",
}
LETRA = "A-Za-zÁÉÍÓÚÑáéíóúñ"


def _texto(e) -> str:
    return "".join(t.text or "" for t in e.iter(qn("w:t")))


def _usos(sigla: str, texto: str) -> int:
    # Las siglas cortas (IA, SIS) se buscan tal cual; las demás, sin distinguir mayúsculas
    # (la lista dice XGBOOST y el texto XGBoost).
    banderas = 0 if len(sigla) <= 3 else re.I
    return len(re.findall(rf"(?<![{LETRA}]){re.escape(sigla)}(?![{LETRA}])", texto, banderas))


def actualizar(body) -> None:
    kids = list(body)
    i = next(k for k, e in enumerate(kids) if _texto(e).strip() == "ACRÓNIMOS" and e.tag == qn("w:p"))
    tabla = next(e for e in kids[i + 1:] if e.tag == qn("w:tbl"))
    fuera = "\n".join(_texto(e) for e in kids if e is not tabla and not (
        e.tag == qn("w:p") and e.find(qn("w:pPr")) is not None
        and e.find(qn("w:pPr")).find(qn("w:pStyle")) is not None
        and e.find(qn("w:pPr")).find(qn("w:pStyle")).get(qn("w:val")).startswith("TDC")))

    filas = tabla.findall(qn("w:tr"))
    modelo = copy.deepcopy(filas[0])
    actuales = {_texto(f.findall(qn("w:tc"))[0]).strip(): f for f in filas}
    quitadas = [s for s in actuales if _usos(s, fuera) == 0]
    agregadas = [s for s in NUEVOS if s not in actuales and _usos(s, fuera) > 0]
    for sigla in quitadas:
        tabla.remove(actuales.pop(sigla))
    for sigla in agregadas:
        fila = copy.deepcopy(modelo)
        celdas = fila.findall(qn("w:tc"))
        for celda, valor in ((celdas[0], sigla), (celdas[2], NUEVOS[sigla])):
            ts = list(celda.iter(qn("w:t")))
            ts[0].text = valor
            for t in ts[1:]:
                t.text = ""
        actuales[sigla] = fila
    for fila in tabla.findall(qn("w:tr")):
        tabla.remove(fila)
    for sigla in sorted(actuales, key=str.upper):
        tabla.append(actuales[sigla])
    print(f"acrónimos: {len(actuales)} en la lista; retirados {quitadas or 'ninguno'}; añadidos {agregadas or 'ninguno'}")
