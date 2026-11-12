"""Aplica las correcciones al borrador: reescribe los capítulos III y IV, conclusiones,
recomendaciones, resumen, abstract, introducción, anexos e índices de tablas y figuras.

Uso: python armar.py base.docx salida.docx [paginas.json]
"""

from __future__ import annotations

import copy
import json
import re
import sys

from docx import Document
from docx.oxml.ns import qn

import acronimos
import anexo1
import anexos
import cap3
import cap4
import cierre
import constructor as c
import datos
import textos

M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
FIGS = __import__("pathlib").Path(__file__).parent / "figuras"


def txt(e) -> str:
    return "".join(t.text or "" for t in e.iter(qn("w:t")))


def estilo(e) -> str:
    ppr = e.find(qn("w:pPr"))
    if ppr is None or ppr.find(qn("w:pStyle")) is None:
        return ""
    return ppr.find(qn("w:pStyle")).get(qn("w:val"))


class Ctx(dict):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.nt = 0
        self.nf = 0
        self["tab"] = self._tab
        self["fig"] = self._fig

    def _tab(self):
        self.nt += 1
        return self.nt

    def _fig(self):
        self.nf += 1
        return self.nf

    def __getitem__(self, k):
        if k == "tab_siguiente":
            return self.nt + 1
        if k == "fig_siguiente":
            return self.nf + 1
        return super().__getitem__(k)


def buscar(kids, desde, cond):
    for i in range(desde, len(kids)):
        if cond(kids[i]):
            return i
    raise ValueError("no encontrado")


def poner_texto(p, texto: str) -> None:
    """Reemplaza el texto de un párrafo conservando el formato del primer run."""
    runs = p.findall(qn("w:r"))
    for r in runs[1:]:
        p.remove(r)
    r = runs[0]
    ts = r.findall(qn("w:t"))
    for t in ts[1:]:
        r.remove(t)
    ts[0].text = texto
    ts[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def reemplazar_region(body, inicio, fin, nuevos, anclaje):
    """Borra kids[inicio:fin], inserta `nuevos` antes de `anclaje` y conserva los
    bookmarkEnd de marcadores que empiezan fuera de la región (p. ej., _EpgCap3)."""
    kids = list(body)
    region = kids[inicio:fin]
    ids_region = {b.get(qn("w:id")) for e in region for b in e.iter(qn("w:bookmarkStart"))}
    huerfanos = [b for e in region for b in e.iter(qn("w:bookmarkEnd")) if b.get(qn("w:id")) not in ids_region]
    for e in region:
        body.remove(e)
    for el in nuevos:
        anclaje.addprevious(el)
    ultimo = [e for e in nuevos if e.tag == qn("w:p")][-1]
    for b in huerfanos:
        b.getparent().remove(b)
        ultimo.append(b)
    return len(huerfanos)


def podar_imagenes(doc) -> int:
    """Quita las relaciones a imágenes que el cuerpo ya no usa.

    Al reemplazar una figura, la imagen anterior queda enlazada al documento aunque nada la
    muestre, y el archivo crece en cada pasada. Solo se tocan las relaciones de tipo imagen de
    la parte principal cuyo identificador no aparece en el XML del cuerpo.
    """
    parte = doc.part
    usados = set(re.findall(r'"(rId\d+)"', doc.element.xml))
    sobran = [rid for rid, rel in parte.rels.items()
              if rel.reltype.endswith("/image") and rid not in usados]
    for rid in sobran:
        del parte.rels[rid]
    return len(sobran)


def main(entrada, salida, paginas=None):
    doc = Document(entrada)
    body = doc.element.body
    R = datos.cargar()
    ids = [int(b.get(qn("w:id"))) for b in body.iter(qn("w:bookmarkStart")) if b.get(qn("w:id")).isdigit()]
    c._bid[0] = max(ids + [9000]) + 1000  # marcadores nuevos sin chocar con los existentes
    kids = list(body)

    i_cap3 = buscar(kids, 300, lambda e: txt(e).strip() == "CAPÍTULO III" and not estilo(e).startswith("TDC"))
    i_cap4 = buscar(kids, i_cap3, lambda e: txt(e).strip() == "CAPÍTULO IV")
    i_muestra = buscar(kids, i_cap3, lambda e: estilo(e) == "Ttulo2" and txt(e).strip() == "Muestra")
    i_met = buscar(kids, i_cap3, lambda e: estilo(e) == "Ttulo2" and txt(e).startswith("Método de investigación"))
    i_desc = buscar(kids, i_met, lambda e: estilo(e) == "Ttulo2")
    ctx = Ctx(
        metodo=[copy.deepcopy(e) for e in kids[i_met + 1:i_desc]],
        ecuaciones=[copy.deepcopy(e) for e in kids[i_cap3:i_cap4] if e.find(".//" + M + "oMath") is not None],
        shap=[copy.deepcopy(e) for e in kids[i_cap3:i_cap4]
              if txt(e).startswith(("Dada la complejidad", "La lógica de SHAP"))],
        ruta_arquitectura=str(FIGS / "fig_arquitectura.png"),
        ruta_flujo=str(FIGS / "fig_flujograma.png"), ruta_web=str(FIGS / "fig_web.png"),
    )
    # Lugar de estudio en pasado
    for e in kids[i_cap3:i_muestra]:
        if "se llevará a cabo" in txt(e):
            poner_texto(e, txt(e).replace("se llevará a cabo", "se llevó a cabo"))

    nuevos3 = cap3.construir(doc, R, ctx)
    n3 = reemplazar_region(body, i_muestra, i_cap4, nuevos3, kids[i_cap4])

    kids = list(body)
    i_cap4 = buscar(kids, 300, lambda e: txt(e).strip() == "CAPÍTULO IV" and not estilo(e).startswith("TDC"))
    i_res = buscar(kids, i_cap4, lambda e: estilo(e) == "Ttulo2" and txt(e).strip() == "Resultados")
    i_con = buscar(kids, i_res, lambda e: txt(e).strip() == "CONCLUSIONES")
    nuevos4 = cap4.construir(doc, R, ctx)
    n4 = reemplazar_region(body, i_res, i_con, nuevos4, kids[i_con])

    kids = list(body)
    i_con = buscar(kids, 300, lambda e: txt(e).strip() == "CONCLUSIONES" and not estilo(e).startswith("TDC"))
    i_rec = buscar(kids, i_con, lambda e: txt(e).strip() == "RECOMENDACIONES")
    reemplazar_region(body, i_con + 1, i_rec, cierre.conclusiones(R), kids[i_rec])
    kids = list(body)
    i_rec = buscar(kids, 300, lambda e: txt(e).strip() == "RECOMENDACIONES" and not estilo(e).startswith("TDC"))
    i_bib = buscar(kids, i_rec, lambda e: txt(e).strip() == "BIBLIOGRAFÍA")
    reemplazar_region(body, i_rec + 1, i_bib, cierre.recomendaciones(), kids[i_bib])

    textos.preliminares(body, R, poner_texto, txt)
    textos.marco_teorico(body, txt, estilo)
    textos.bibliografia(body, txt)
    textos.matriz(body, txt)
    anexo1.actualizar(body, R)
    anexos.actualizar(doc, body, R, txt, poner_texto)
    acronimos.actualizar(body)
    textos.indices(body, ctx, txt, estilo, paginas or {})
    if paginas:
        textos.toc(body, txt, estilo, paginas)
        textos.fijar_pageref(body, paginas)
    podadas = podar_imagenes(doc)
    doc.save(salida)
    print(f"tablas {ctx.nt}, figuras {ctx.nf}, marcadores conservados III={n3} IV={n4}, "
          f"imágenes sin uso retiradas {podadas}")


if __name__ == "__main__":
    pag = json.load(open(sys.argv[3], encoding="utf-8")) if len(sys.argv) > 3 else None
    main(sys.argv[1], sys.argv[2], pag)
