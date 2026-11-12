"""Actualiza los anexos 2 a 5 y 7 con los resultados y el código nuevos."""

from __future__ import annotations

import json

from docx.oxml.ns import qn

import constructor as c
from datos import RAIZ, f, miles

FIG = str(__import__("pathlib").Path(__file__).parent / "figuras") + "/"
REPOSITORIO = "https://github.com/aldozpuno/pobreza-ml-peru"  # enlace público del código (Anexo 7)


def _rango(kids, txt, titulo, siguiente_prefijo):
    i = next(k for k, e in enumerate(kids) if txt(e).strip().startswith(titulo) and k > 600)
    j = next(k for k in range(i + 1, len(kids)) if txt(kids[k]).strip().startswith(siguiente_prefijo))
    return i, j


def _reemplazar(body, txt, titulo, siguiente, nuevos):
    kids = list(body)
    i, j = _rango(kids, txt, titulo, siguiente)
    for e in kids[i + 1:j]:
        body.remove(e)
    for el in nuevos:
        kids[j].addprevious(el)


def _p(t):
    return c.parrafo(t, 2)


def actualizar(doc, body, R, txt, poner_texto):
    import yaml
    modelo = yaml.safe_load(open(RAIZ / "config/model.yaml", encoding="utf-8"))
    xgb = modelo["estimadores"]["hiperparametros"]["xgboost"] if "hiperparametros" in modelo["estimadores"] else None
    filas = [
        ["Años de la base", "2017–2024 (ENAHO, metodología actualizada)"],
        ["Validación", "Ventana expansiva: entrena con los años anteriores, calibra con el siguiente y evalúa con el posterior (2020–2023)"],
        ["Prueba final", "Entrena 2017–2022, calibra 2023, evalúa 2024"],
        ["Modelo principal", "XGBoost: 400 árboles, profundidad 5, tasa de aprendizaje 0.05, submuestreo 0.8, min_child_weight 10"],
        ["Modelos de referencia", "Bosque aleatorio, regresión logística, probit y KNN"],
        ["Calibración", "Regresión isotónica en el año de calibración"],
        ["Umbral", f"Maximiza el F1 en el año de calibración (prueba final: {R['umbral']})"],
        ["Pesos en el entrenamiento", "No (FACTOR07 solo en cifras poblacionales y métricas ponderadas)"],
        ["Tolerancia de la medición", "0.3 puntos porcentuales frente a la cifra oficial del INEI"],
        ["Valores SHAP", "Muestra de 5 000 hogares; periodos 2017–2019 y 2021–2024"],
        ["Variables excluidas por fuga de datos", ", ".join(R["fuga"].nombre.str.upper())],
        ["Variables excluidas por colinealidad exacta", "Brecha educativa e índice de privación"],
        ["Variable excluida por no ser comparable entre años",
         "Conexión a internet (P1144): desde 2023 incluye el internet móvil"],
    ]
    _reemplazar(body, txt, "Anexo 2.", "Anexo 3.", [
        _p("Parámetros del procedimiento, tal como se declaran en los archivos config/pipeline.yaml, "
           "config/model.yaml y config/features.yaml."),
        c.tabla(["Parámetro", "Valor"], filas, [4.5, 10.5], 2), c.nota("Elaboración propia.", 2)])

    a = R["anual"]
    _reemplazar(body, txt, "Anexo 3.", "Anexo 4.", [
        _p("Proporción de pobres por año según la unidad y la ponderación. La clase minoritaria (hogares pobres) "
           "representa entre 17 % y 22 % de la muestra, por lo que se usan métricas para clases desbalanceadas."),
        c.tabla(["Año", "Hogares", "Hogares pobres en la muestra (%)", "Hogares pobres ponderado (%)", "Personas pobres (%)"],
                [[str(r.anio), miles(r.hogares_muestra), f(r.tasa_muestral, 2), f(r.tasa_hogares, 2), f(r.tasa_personas, 2)]
                 for r in a.itertuples()], [1.6, 2.2, 3.8, 3.7, 3.7], 2, {1, 2, 3, 4}),
        c.nota("Ponderado: FACTOR07 para hogares y FACTOR07 × MIEPERHO para personas. Elaborado con la ENAHO.", 2)])

    import pandas as pd
    dep = pd.read_csv(RAIZ / "resultados/reportes/datos/incidencia_departamento.csv")
    from datos import D
    nombres = json.load(open(RAIZ / "web/public/data/territorio.json", encoding="utf-8"))["incidencia"]
    nom = {x["departamento"]: x["nombre"] for x in nombres}
    dep["departamento"] = dep["departamento"].astype(str).str.zfill(2)
    tabla = dep.pivot_table(index="departamento", columns="anio", values="tasa_personas")
    tabla = tabla.loc[tabla[2024].sort_values(ascending=False).index]
    filas = [[nom.get(k, k)] + [f(v, 1) for v in fila] for k, fila in tabla.iterrows()]
    _reemplazar(body, txt, "Anexo 4.", "Anexo 5.", [
        _p("Pobreza monetaria por departamento, en porcentaje de personas, 2017–2024, ordenada por la tasa de 2024."),
        c.tabla(["Departamento"] + [str(x) for x in tabla.columns], filas, [3.4] + [1.45] * 8, 2, set(range(1, 9))),
        c.nota("Ponderado por FACTOR07 × MIEPERHO. Las tasas departamentales anuales tienen mayor error muestral "
               "que la nacional. Elaborado con la ENAHO.", 2)])

    im = R["imp"]
    filas = []
    for r in im.itertuples():
        esp = r.signo_esperado or "±"
        coincide = "Sí" if esp in "+-" and esp == r.signo_observado else ("—" if esp not in "+-" else "No")
        filas.append([r.etiqueta, f(r.importancia, 3), esp, r.signo_observado, coincide])
    _reemplazar(body, txt, "Anexo 5.", "Anexo 6.", [
        _p(f"Las {len(im)} variables del modelo final ordenadas por su importancia SHAP en la ENAHO 2024, con el "
           "signo esperado según la teoría y el signo observado en el modelo."),
        c.tabla(["Variable", "Importancia SHAP", "Signo esperado", "Signo observado", "Coincide"], filas,
                [5.6, 2.6, 2.2, 2.4, 2.2], 2, {1}),
        c.nota("Importancia: media del valor SHAP absoluto (log-odds). Signo observado: correlación entre el valor de "
               "la variable y su valor SHAP; ± en variables por categorías o sin variación. Elaborado con la ENAHO.", 2)])

    # Anexo 7: texto y fragmentos de código nuevos
    kids = list(body)
    i, j = _rango(kids, txt, "Anexo 7.", "Anexo 8.")
    for e in kids[i + 1:j]:
        body.remove(e)
    nuevos = [
        _p("El código fuente de la investigación está organizado por capas (datos, procesamiento, medición, "
           "variables, modelos, evaluación y reportes), con pruebas automáticas, y se ejecuta con el comando "
           f"pobreza todo. Repositorio: {REPOSITORIO}"),
        _p("Base de datos procesada: datos/procesados/hogares.parquet, con 277 136 observaciones hogar-año de la "
           "ENAHO 2017–2024 y las llaves CONGLOME, VIVIENDA y HOGAR."),
        _p("Microdatos originales: Instituto Nacional de Estadística e Informática, Encuesta Nacional de Hogares "
           "2017–2024. https://proyectos.inei.gob.pe/microdatos/"),
        _p("Fragmentos del código:"),
    ]
    for etiqueta, archivo in CODIGO:
        nuevos += _imagen(doc, etiqueta, archivo)
    nuevos.append(_p(
        "Web de resultados. La web (carpeta web/ del repositorio) presenta los resultados en cinco páginas: "
        "Panorama, Territorio, Modelo, Variables y Método. No calcula nada: lee los datos que genera el mismo "
        "procedimiento, de modo que sus cifras son las de esta tesis (en la web los decimales van con coma). "
        "Las capturas siguientes muestran sus gráficos principales."))
    for etiqueta, archivo in WEB:
        nuevos += _imagen(doc, etiqueta, archivo)
    for el in nuevos:
        kids[j].addprevious(el)
    _titular(body, 7, TITULO_ANEXO_7)


TITULO_ANEXO_7 = "Base de datos, scripts de procesamiento y web de resultados"
CODIGO = [
    ("a) Medición de la incidencia de la pobreza con el factor de expansión", "codigo_medicion.png"),
    ("b) Reconstrucción del empleo informal con el criterio de la OIT", "codigo_informalidad.png"),
    ("c) Prueba de DeLong para comparar el AUC de dos modelos", "codigo_delong.png"),
]
WEB = [  # capturas de herramientas/tesis/capturas_web.py
    ("d) Panorama: pobreza monetaria en el Perú, 2017–2024", "web_panorama.png"),
    ("e) Panorama: qué tan bien identifica el modelo a los hogares pobres", "web_lecturas.png"),
    ("f) Panorama: pobreza monetaria por área de residencia", "web_area.png"),
    ("g) Territorio: pobreza observada y estimada por departamento", "web_sesgo.png"),
    ("h) Modelo: desempeño de XGBoost por año de evaluación", "web_por_anio.png"),
    ("i) Modelo: matriz de confusión en la ENAHO 2024", "web_matriz.png"),
    ("j) Modelo: curva ROC y curva de precisión y exhaustividad", "web_curvas.png"),
    ("k) Modelo: calibración de las probabilidades", "web_calibracion.png"),
    ("l) Variables: importancia de las variables según los valores SHAP", "web_variables.png"),
    ("m) Variables: importancia antes y después de la pandemia", "web_periodos.png"),
]
ANCHO_CM, ALTO_MAX_CM = 15.0, 19.0  # ancho del texto y alto máximo para que quepa con su rótulo


def _imagen(doc, etiqueta: str, archivo: str) -> list:
    """Rótulo y, pegada a él, la imagen completa: tan ancha como el texto salvo que por su alto
    no quepa en la página, en cuyo caso se reduce sin recortarla."""
    from docx.shared import Cm
    from PIL import Image
    with Image.open(FIG + archivo) as im:
        proporcion = im.width / im.height
    ancho = min(ANCHO_CM, ALTO_MAX_CM * proporcion)
    rotulo = _p(etiqueta)
    ppr = rotulo.get_or_add_pPr()
    # el rótulo no se separa de su imagen; sin la sangría de primera línea del documento (1.27 cm),
    # que empujaría una imagen de 15 cm fuera del margen derecho
    for hijo in (c._el("w:keepNext"), c._el("w:spacing", after=60), c._el("w:ind", firstLine=0),
                 c._el("w:jc", val="left")):
        ppr.append(hijo)
    pp = doc.add_paragraph()
    pp.add_run().add_picture(FIG + archivo, width=Cm(ancho))
    el = pp._p
    el.getparent().remove(el)
    ppr = el.get_or_add_pPr()
    for hijo in (c._el("w:spacing", after=200, line=240, lineRule="auto"), c._el("w:ind", firstLine=0),
                 c._el("w:jc", val="left")):
        ppr.append(hijo)
    return [rotulo, el]


def _titular(body, n: int, titulo: str) -> None:
    """Cambia el título del anexo `n` en su encabezado, en su campo TC y en el índice de anexos."""
    marca = f"_EpgAT{n}"
    for p in body.iter(qn("w:p")):
        hijos = list(p)
        for k, h in enumerate(hijos):
            if h.tag == qn("w:bookmarkStart") and h.get(qn("w:name")) == marca:
                siguiente = next((x for x in hijos[k + 1:] if x.tag == qn("w:r")), None)
                if siguiente is not None and siguiente.find(qn("w:t")) is not None:
                    siguiente.find(qn("w:t")).text = titulo
        estado = None  # recorre los campos del párrafo: REF _EpgATn → texto en caché
        for el in p.iter(qn("w:instrText"), qn("w:fldChar"), qn("w:t")):
            if el.tag == qn("w:instrText"):
                # solo el campo TC de anexos (\f A): las tablas y figuras tienen su propio «n.»
                if (el.text or "").startswith(f' TC "{n}. ') and " \\f A " in el.text:
                    el.text = f' TC "{n}. {titulo}" \\f A \\l 5 '
                estado = "ref" if f"REF {marca} " in (el.text or "") else None
            elif el.tag == qn("w:fldChar"):
                tipo = el.get(qn("w:fldCharType"))
                if tipo == "separate" and estado == "ref":
                    estado = "texto"
                elif tipo == "end":
                    estado = None
            elif estado == "texto":
                el.text = titulo
                estado = None
