"""Bloques OOXML con el formato que ya usa el borrador (estilos Título 2–4, texto Normal,
rótulos de tabla/figura con marcadores _EpgTN/_EpgTT/_EpgFN/_EpgFT y campo TC oculto)."""

from __future__ import annotations

import copy
import re

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm

TW_CM = 567  # twips por cm
SANGRIA = {2: 0, 3: 720, 4: 1440}  # sangría del texto según el nivel del título (twips)
_bid = [9000]


def _nuevo_id() -> str:
    _bid[0] += 1
    return str(_bid[0])


def _run(texto: str, negrita=False, cursiva=False, tam=None) -> OxmlElement:
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    if negrita:
        rpr.append(OxmlElement("w:b"))
    if cursiva:
        rpr.append(OxmlElement("w:i"))
    color = OxmlElement("w:color"); color.set(qn("w:val"), "000000"); rpr.append(color)
    if tam:
        for tag in ("w:sz", "w:szCs"):
            s = OxmlElement(tag); s.set(qn("w:val"), str(tam * 2)); rpr.append(s)
    r.append(rpr)
    t = OxmlElement("w:t"); t.set(qn("xml:space"), "preserve"); t.text = texto
    r.append(t)
    return r


def _runs(p, texto: str, negrita=False, tam=None) -> None:
    """Texto con *cursiva* y **negrita** mínimas."""
    for trozo in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*)", texto):
        if not trozo:
            continue
        if trozo.startswith("**"):
            p.append(_run(trozo[2:-2], negrita=True, tam=tam))
        elif trozo.startswith("*"):
            p.append(_run(trozo[1:-1], negrita=negrita, cursiva=True, tam=tam))
        else:
            p.append(_run(trozo, negrita=negrita, tam=tam))


def _ppr(*hijos) -> OxmlElement:
    ppr = OxmlElement("w:pPr")
    for h in hijos:
        ppr.append(h)
    return ppr


def _el(tag: str, **attrs) -> OxmlElement:
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(f"w:{k}"), str(v))
    return e


def titulo(nivel: int, texto: str) -> OxmlElement:
    """Título N2–N4 con el estilo y la numeración multinivel (numId 9) del borrador."""
    estilo = {2: "Ttulo2", 3: "Ttulo3", 4: "Ttulo4"}[nivel]
    ind = {2: (720, 720), 3: (1440, 720), 4: (2160, 720)}[nivel]
    num = _el("w:numPr"); num.append(_el("w:ilvl", val=nivel - 1)); num.append(_el("w:numId", val=9))
    p = OxmlElement("w:p")
    p.append(_ppr(_el("w:pStyle", val=estilo), num, _el("w:ind", left=ind[0], hanging=ind[1])))
    bm = _nuevo_id()
    p.append(_el("w:bookmarkStart", id=bm, name=f"_Toc9{bm}"))
    p.append(_run(texto))
    p.append(_el("w:bookmarkEnd", id=bm))
    return p


def parrafo(texto: str, nivel: int = 2) -> OxmlElement:
    p = OxmlElement("w:p")
    if SANGRIA[nivel]:
        p.append(_ppr(_el("w:ind", left=SANGRIA[nivel])))
    _runs(p, texto)
    return p


def vinetas(items: list[str], nivel: int = 2) -> list[OxmlElement]:
    """Viñetas con la lista del borrador (numId 6), 0/0 y la última 0/10."""
    salida = []
    for i, texto in enumerate(items):
        num = _el("w:numPr"); num.append(_el("w:ilvl", val=0)); num.append(_el("w:numId", val=6))
        izq = SANGRIA[nivel] + 567
        hijos = [num]
        if i < len(items) - 1:
            hijos.append(_el("w:spacing", after=0))
        hijos.append(_el("w:ind", left=izq, hanging=567))
        p = OxmlElement("w:p"); p.append(_ppr(*hijos)); _runs(p, texto)
        salida.append(p)
    return salida


def _rotulo(tipo: str, n: int, titulo_txt: str, nivel: int) -> list[OxmlElement]:
    letra = "T" if tipo == "Tabla" else "F"
    izq = SANGRIA[nivel]
    p1 = OxmlElement("w:p")
    p1.append(_ppr(_el("w:keepNext"), _el("w:spacing", after=0), _el("w:ind", left=izq, firstLine=0),
                   _el("w:jc", val="left")))
    p1.append(_run(f"{tipo} ", negrita=True))
    b = _nuevo_id()
    p1.append(_el("w:bookmarkStart", id=b, name=f"_Epg{letra}N{n}"))
    p1.append(_run(str(n), negrita=True))
    p1.append(_el("w:bookmarkEnd", id=b))
    for tipo_fld, instr in (("begin", None), (None, f' TC "{n}. {titulo_txt}" \\f {letra} \\l 5 '), ("end", None)):
        r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr"); rpr.append(OxmlElement("w:vanish")); r.append(rpr)
        if tipo_fld:
            r.append(_el("w:fldChar", fldCharType=tipo_fld))
        else:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr; r.append(it)
        p1.append(r)
    p2 = OxmlElement("w:p")
    p2.append(_ppr(_el("w:keepNext"), _el("w:spacing", after=0), _el("w:ind", left=izq, firstLine=0),
                   _el("w:jc", val="left")))
    b2 = _nuevo_id()
    p2.append(_el("w:bookmarkStart", id=b2, name=f"_Epg{letra}T{n}"))
    p2.append(_run(titulo_txt, cursiva=True))
    p2.append(_el("w:bookmarkEnd", id=b2))
    return [p1, p2]


def nota(texto: str, nivel: int = 2) -> OxmlElement:
    p = OxmlElement("w:p")
    p.append(_ppr(_el("w:spacing", after=300), _el("w:ind", left=SANGRIA[nivel], firstLine=0), _el("w:jc", val="left")))
    p.append(_run("Nota.", cursiva=True, tam=11))
    _runs(p, " " + texto, tam=11)
    return p


def _celda(texto: str, ancho: int, encabezado: bool, alineacion: str) -> OxmlElement:
    tc = OxmlElement("w:tc")
    tcpr = OxmlElement("w:tcPr")
    tcpr.append(_el("w:tcW", w=ancho, type="dxa"))
    if encabezado:
        bd = OxmlElement("w:tcBorders")
        for lado in ("top", "bottom"):
            bd.append(_el(f"w:{lado}", val="single", sz=4, space=0, color="000000"))
        tcpr.append(bd)
        tcpr.append(_el("w:shd", val="clear", color="BFBFBF", fill="BFBFBF"))
    mar = OxmlElement("w:tcMar")
    for lado, ancho in (("top", 40), ("left", 80), ("bottom", 40), ("right", 80)):
        mar.append(_el(f"w:{lado}", w=ancho, type="dxa"))
    tcpr.append(mar)
    tc.append(tcpr)
    p = OxmlElement("w:p")
    hijos = [_el("w:spacing", after=0, line=240 if not encabezado else 276, lineRule="auto"),
             _el("w:ind", firstLine=0), _el("w:jc", val="center" if encabezado else alineacion)]
    p.append(_ppr(*hijos))
    _runs(p, texto, negrita=encabezado, tam=11 if not encabezado else 11)
    tc.append(p)
    return tc


def tabla(encabezado: list[str], filas: list[list[str]], anchos_cm: list[float], nivel: int = 2,
          numericas: set[int] | None = None) -> OxmlElement:
    """Tabla APA/EPG: solo líneas horizontales, encabezado gris repetido."""
    numericas = numericas or set()
    total_cm = 15.0 - SANGRIA[nivel] / TW_CM
    escala = total_cm / sum(anchos_cm)
    anchos = [int(a * escala * TW_CM) for a in anchos_cm]
    tbl = OxmlElement("w:tbl")
    tpr = OxmlElement("w:tblPr")
    tpr.append(_el("w:tblW", w=sum(anchos), type="dxa"))
    tpr.append(_el("w:tblInd", w=SANGRIA[nivel], type="dxa"))
    bd = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if lado in ("top", "bottom"):
            bd.append(_el(f"w:{lado}", val="single", sz=4, space=0, color="000000"))
        else:
            bd.append(_el(f"w:{lado}", val="nil"))
    tpr.append(bd)
    tpr.append(_el("w:tblLayout", type="fixed"))
    tbl.append(tpr)
    grid = OxmlElement("w:tblGrid")
    for a in anchos:
        grid.append(_el("w:gridCol", w=a))
    tbl.append(grid)
    for i, fila in enumerate([encabezado] + filas):
        tr = OxmlElement("w:tr")
        trpr = OxmlElement("w:trPr"); trpr.append(OxmlElement("w:cantSplit"))
        if i == 0:
            trpr.append(OxmlElement("w:tblHeader"))
        tr.append(trpr)
        for j, (texto, ancho) in enumerate(zip(fila, anchos)):
            tr.append(_celda(str(texto), ancho, i == 0, "right" if j in numericas else "left"))
        tbl.append(tr)
    return tbl


def bloque_tabla(n: int, titulo_txt: str, encabezado, filas, anchos_cm, nivel=2, numericas=None,
                 nota_txt: str | None = None) -> list[OxmlElement]:
    salida = _rotulo("Tabla", n, titulo_txt, nivel)
    salida.append(tabla(encabezado, filas, anchos_cm, nivel, numericas))
    salida.append(nota(nota_txt, nivel) if nota_txt else _vacio())
    return salida


def _vacio() -> OxmlElement:
    p = OxmlElement("w:p"); p.append(_ppr(_el("w:spacing", after=0, line=240, lineRule="auto")))
    return p


def bloque_figura(doc, n: int, titulo_txt: str, ruta: str, ancho_cm: float, nivel=2,
                  nota_txt: str | None = None) -> list[OxmlElement]:
    salida = _rotulo("Figura", n, titulo_txt, nivel)
    p = doc.add_paragraph()
    p.add_run().add_picture(ruta, width=Cm(min(ancho_cm, 15.0 - SANGRIA[nivel] / TW_CM)))
    el = p._p
    el.getparent().remove(el)
    ppr = el.get_or_add_pPr()
    for hijo in list(ppr):
        ppr.remove(hijo)
    ppr.append(_el("w:spacing", after=0 if nota_txt else 200, line=240, lineRule="auto"))
    ppr.append(_el("w:ind", left=SANGRIA[nivel], firstLine=0))
    ppr.append(_el("w:jc", val="left"))
    salida.append(el)
    if nota_txt:
        salida.append(nota(nota_txt, nivel))
    return salida


def conclusion(ordinal: str, texto: str) -> OxmlElement:
    p = OxmlElement("w:p")
    p.append(_ppr(_el("w:ind", left=1440, hanging=1440)))
    p.append(_run(f"{ordinal}:", negrita=True))
    r = OxmlElement("w:r"); r.append(OxmlElement("w:tab")); p.append(r)
    _runs(p, texto)
    return p


def clonar(el):
    return copy.deepcopy(el)


_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def _mr(texto: str, normal: bool = False) -> str:
    sty = '<m:rPr><m:sty m:val="p"/></m:rPr>' if normal else ""
    fuente = '<w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>'
    return f'<m:r>{sty}{fuente}<m:t xml:space="preserve">{texto}</m:t></m:r>'


def _sub(base: str, indice: str) -> str:
    return f"<m:sSub><m:e>{_mr(base)}</m:e><m:sub>{_mr(indice)}</m:sub></m:sSub>"


def ecuacion(omml_interior: str) -> OxmlElement:
    """Párrafo centrado con una ecuación del editor de ecuaciones (OMML)."""
    from lxml import etree
    xml = (f'<w:p xmlns:w="{_W}" xmlns:m="{_M}"><w:pPr><w:ind w:firstLine="0"/><w:jc w:val="center"/></w:pPr>'
           f'<m:oMathPara><m:oMath>{omml_interior}</m:oMath></m:oMathPara></w:p>')
    return etree.fromstring(xml)


def ecuacion_pobreza() -> OxmlElement:
    fila1 = _mr("1,   si el gasto per cápita del hogar es menor que la línea de pobreza", True)
    fila2 = _mr("0,  en otro caso", True)
    interior = (_sub("Y", "i") + _mr("=") +
                '<m:d><m:dPr><m:begChr m:val="{"/><m:endChr m:val=""/></m:dPr><m:e>'
                f'<m:eqArr><m:e>{fila1}</m:e><m:e>{fila2}</m:e></m:eqArr></m:e></m:d>')
    return ecuacion(interior)


def ecuacion_incidencia() -> OxmlElement:
    def suma(cuerpo):
        return ('<m:nary><m:naryPr><m:chr m:val="∑"/><m:supHide m:val="1"/></m:naryPr>'
                f'<m:sub>{_mr("i")}</m:sub><m:sup></m:sup><m:e>{cuerpo}</m:e></m:nary>')
    num = suma(_sub("Y", "i") + _mr("·") + _sub("MIEPERHO", "i") + _mr("·") + _sub("FACTOR07", "i"))
    den = suma(_sub("MIEPERHO", "i") + _mr("·") + _sub("FACTOR07", "i"))
    interior = _mr("Tasa de pobreza", True) + _mr("=") + f"<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>" + _mr("×100")
    return ecuacion(interior)
