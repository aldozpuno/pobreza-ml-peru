"""Calcula el número de página impreso de títulos, tablas y figuras a partir del PDF.

Uso: python paginas.py documento.docx documento.pdf salida.json
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

from docx import Document
from docx.oxml.ns import qn


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def paginas_pdf(pdf: str) -> list[str]:
    texto = subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", pdf, "-"], capture_output=True,
                           text=True, encoding="utf-8", errors="replace").stdout
    paginas = []
    LINEAS.clear()
    for p in texto.split("\f"):
        lineas = [re.sub(r"^\s*\d+\s+", "", l) for l in p.splitlines()]
        paginas.append(norm(" ".join(l for l in lineas if not re.fullmatch(r"\s*\d*\s*", l))))
        LINEAS.append({norm(l) for l in lineas})
    return paginas


LINEAS: list[set[str]] = []  # líneas de cada página, para buscar un título que ocupa una línea sola


def main(docx, pdf, salida):
    pags = paginas_pdf(pdf)
    # página física del RESUMEN en el cuerpo (= página impresa 1)
    inicio_resumen = next(i for i, p in enumerate(pags) if p.startswith("resumen ") and "palabras clave" in p)
    inicio_cap3 = next(i for i, p in enumerate(pags) if i > inicio_resumen and p.startswith("capítulo iii") and "materiales y métodos" in p)

    inicio_cap1 = next(i for i, p in enumerate(pags) if i > inicio_resumen and p.startswith("capítulo i ") and "revisión de literatura" in p[:60])
    cursor = {"h": inicio_cap1, "T": inicio_cap3, "F": inicio_cap3}

    def pagina(texto, tipo):
        for largo in (60, 30):
            clave = norm(texto)[:largo]
            for i in range(cursor[tipo], len(pags)):
                if clave in pags[i]:
                    cursor[tipo] = i
                    return i - inicio_resumen + 1
        if tipo == "h":
            # En el PDF de Word el número de un título puede quedar en otra línea que su texto
            # («Resultados» y, aparte, «4.1»): se busca el título solo, como línea completa.
            solo = norm(re.sub(r"^\d+(\.\d+)*\s+", "", texto))
            for i in range(cursor[tipo], len(pags)):
                if solo in LINEAS[i]:
                    cursor[tipo] = i
                    return i - inicio_resumen + 1
        return ""

    doc = Document(docx)
    resultado = {}
    body = doc.element.body
    hijos = list(body)
    posicion = {id(e): k for k, e in enumerate(hijos)}
    body_index = lambda p: posicion.get(id(p), -1)
    idx_cap1 = next(k for k, e in enumerate(hijos) if "".join(t.text or "" for t in e.iter(qn("w:t"))).strip() == "CAPÍTULO I"
                    and (e.find(qn("w:pPr")) is None or e.find(qn("w:pPr")).find(qn("w:pStyle")) is None))
    idx_cap3 = next(k for k, e in enumerate(hijos) if "".join(t.text or "" for t in e.iter(qn("w:t"))).strip() == "CAPÍTULO III"
                    and (e.find(qn("w:pPr")) is None or e.find(qn("w:pPr")).find(qn("w:pStyle")) is None))
    cap, n2, n3 = 0, 0, 0
    romanos = {"CAPÍTULO I": 1, "CAPÍTULO II": 2, "CAPÍTULO III": 3, "CAPÍTULO IV": 4}
    for k, p in enumerate(hijos):
        if p.tag != qn("w:p"):
            continue
        texto_p = "".join(t.text or "" for t in p.iter(qn("w:t"))).strip()
        if k >= idx_cap1 and texto_p in romanos:
            cap, n2, n3 = romanos[texto_p], 0, 0
        ppr = p.find(qn("w:pPr"))
        estilo = ppr.find(qn("w:pStyle")).get(qn("w:val")) if ppr is not None and ppr.find(qn("w:pStyle")) is not None else ""
        if estilo in ("Ttulo2", "Ttulo3"):
            marca = next((b.get(qn("w:name")) for b in p.iter(qn("w:bookmarkStart"))
                          if b.get(qn("w:name")).startswith("_Toc")), None)
            if marca:
                texto = "".join(t.text or "" for t in p.iter(qn("w:t")))
                if k > idx_cap1 and cap:
                    if estilo == "Ttulo2":
                        n2 += 1; n3 = 0; num = f"{cap}.{n2}"
                    else:
                        n3 += 1; num = f"{cap}.{n2}.{n3}"
                    resultado[marca] = pagina(f"{num} {texto}", "h")
    for it in body.iter(qn("w:instrText")):
        m = re.match(r' TC "(\d+)\. (.*)" \\f ([TF]) ', it.text or "")
        if m:
            resultado[f"{m.group(3)}{m.group(1)}"] = pagina(
                ("tabla " if m.group(3) == "T" else "figura ") + m.group(1) + " " + m.group(2), m.group(3))
    def primera(cond, desde=inicio_cap3):
        return next((i - inicio_resumen + 1 for i in range(desde, len(pags)) if cond(pags[i])), "")
    resultado["_EpgCON"] = primera(lambda x: x.startswith("conclusiones primero"))
    resultado["_EpgREC"] = primera(lambda x: x.startswith("recomendaciones primero"))
    resultado["_EpgBIB"] = primera(lambda x: x.startswith("bibliografía"))
    i_anx = next(i for i in range(inicio_cap3, len(pags)) if pags[i].startswith("anexos") and i > inicio_cap3 + 10)
    resultado["_EpgANX"] = i_anx - inicio_resumen + 1
    for n in range(1, 10):
        resultado[f"_EpgAT{n}"] = primera(lambda x, n=n: f"anexo {n}. " in x, i_anx)
    vacios = [k for k, v in resultado.items() if v == ""]
    print("páginas calculadas:", len(resultado), "sin encontrar:", vacios[:10])
    json.dump(resultado, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(*sys.argv[1:4])
