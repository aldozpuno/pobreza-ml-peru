"""Escritura de tablas en Word con el formato de la Guía EPG UNA Puno (APA 7).

    Rótulo "Tabla N" en negrita · título en cursiva en la línea siguiente
    Encabezado sombreado (#BFBFBF), en negrita, centrado y repetido en cada página
    Solo líneas horizontales: arriba, bajo el encabezado y al final
    Times New Roman 12 (11 o 10 si la tabla es ancha), interlineado sencillo
    "Nota." en cursiva, a 11 pt, bajo la tabla
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

from pobreza.reporting.tables import TablaTesis

GRIS_ENCABEZADO = "BFBFBF"


def _tamano(columnas: int) -> int:
    return 12 if columnas <= 5 else 11 if columnas <= 7 else 10


def _bordes(tabla) -> None:
    propiedades = tabla._tbl.tblPr
    bordes = OxmlElement("w:tblBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        elemento = OxmlElement(f"w:{lado}")
        visible = lado in ("top", "bottom")
        elemento.set(qn("w:val"), "single" if visible else "nil")
        if visible:
            elemento.set(qn("w:sz"), "8")
            elemento.set(qn("w:color"), "000000")
        bordes.append(elemento)
    propiedades.append(bordes)


def _celda(celda, texto: str, tamano: int, negrita: bool = False, gris: bool = False,
           centrar: bool = False) -> None:
    celda.text = ""
    parrafo = celda.paragraphs[0]
    parrafo.paragraph_format.space_before = Pt(0)
    parrafo.paragraph_format.space_after = Pt(0)
    parrafo.paragraph_format.line_spacing = 1.0
    if centrar:
        parrafo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    corrida = parrafo.add_run(str(texto))
    corrida.bold = negrita
    corrida.font.size = Pt(tamano)
    corrida.font.name = "Times New Roman"
    if gris:
        sombra = OxmlElement("w:shd")
        sombra.set(qn("w:val"), "clear")
        sombra.set(qn("w:fill"), GRIS_ENCABEZADO)
        celda._tc.get_or_add_tcPr().append(sombra)


def _linea_bajo_encabezado(fila) -> None:
    for celda in fila.cells:
        bordes = OxmlElement("w:tcBorders")
        abajo = OxmlElement("w:bottom")
        abajo.set(qn("w:val"), "single")
        abajo.set(qn("w:sz"), "8")
        bordes.append(abajo)
        celda._tc.get_or_add_tcPr().append(bordes)


def _repetir_encabezado(fila) -> None:
    marca = OxmlElement("w:tblHeader")
    marca.set(qn("w:val"), "true")
    fila._tr.get_or_add_trPr().append(marca)


def agregar(documento, numero: int, tabla: TablaTesis) -> None:
    """Agrega una tabla completa (rótulo, título, cuerpo y nota) al documento."""
    rotulo = documento.add_paragraph()
    rotulo.add_run(f"Tabla {numero}").bold = True
    documento.add_paragraph().add_run(tabla.titulo).italic = True

    datos = tabla.datos
    tamano = _tamano(datos.shape[1])
    cuerpo = documento.add_table(rows=1, cols=datos.shape[1])
    cuerpo.alignment = WD_TABLE_ALIGNMENT.LEFT
    _bordes(cuerpo)
    for celda, nombre in zip(cuerpo.rows[0].cells, datos.columns):
        _celda(celda, nombre, tamano, negrita=True, gris=True, centrar=True)
    _linea_bajo_encabezado(cuerpo.rows[0])
    _repetir_encabezado(cuerpo.rows[0])
    for _, fila in datos.iterrows():
        celdas = cuerpo.add_row().cells
        for i, valor in enumerate(fila):
            _celda(celdas[i], valor, tamano, centrar=i > 0)

    nota = documento.add_paragraph()
    nota.paragraph_format.space_before = Pt(0)
    nota.paragraph_format.space_after = Pt(15)
    marca = nota.add_run("Nota. ")
    marca.italic = True
    marca.font.size = Pt(11)
    nota.add_run(tabla.nota).font.size = Pt(11)


def escribir(tablas: list[TablaTesis], ruta: Path) -> Path:
    """Crea un .docx con todas las tablas, numeradas en el orden recibido."""
    documento = Document()
    estilo = documento.styles["Normal"]
    estilo.font.name = "Times New Roman"
    estilo.font.size = Pt(12)
    for numero, tabla in enumerate(tablas, start=1):
        agregar(documento, numero, tabla)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    documento.save(ruta)
    return ruta
