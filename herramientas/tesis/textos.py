"""Textos preliminares, bibliografía, matriz de consistencia e índices."""

from __future__ import annotations

import copy
import re

from docx.oxml.ns import qn

import constructor as c
from datos import f

XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _resumen(R):
    m = R["m"]; pb = R["delong"][R["delong"].modelo_comparado == "probit"].iloc[0]
    es = (
        "La pobreza monetaria afecta a más de la cuarta parte de la población peruana y su identificación "
        "oportuna es clave para focalizar los programas sociales. El objetivo fue desarrollar y validar un modelo "
        "predictivo basado en aprendizaje automático y modelos econométricos para clasificar hogares en condición "
        "de pobreza monetaria en el Perú con información socioeconómica, demográfica y territorial de la Encuesta "
        "Nacional de Hogares (ENAHO). Con un diseño no experimental de cortes transversales agrupados se "
        f"analizaron {R['obs']} observaciones hogar-año de la ENAHO 2017–2024. La pobreza se midió como el INEI, con diferencias de 0.05 puntos o menos respecto de la "
        "cifra oficial; se identificaron los hogares entrevistados en más de un año y se usó el factor de expansión "
        "en las cifras poblacionales. Se compararon XGBoost, bosque aleatorio, regresión logística, probit y k "
        "vecinos más cercanos con validación temporal de ventana expansiva, calibración isotónica y una prueba "
        "fuera de muestra con la ENAHO 2024; las variables se interpretaron con valores SHAP. XGBoost obtuvo un "
        f"AUC-ROC de {f(m['auc_roc'])} y un AUC-PR de {f(m['auc_pr'])}, superó a todos los modelos de referencia "
        f"según la prueba de DeLong (p < 0.001), identificó al {f(100*m['recall'],1)} % de los hogares pobres y "
        f"estimó una pobreza de {f(m['tasa_predicha'],1)} % frente a {f(m['tasa_real'],1)} % observada. Se concluye "
        "que las características observables del hogar (vivienda, tamaño, empleo, educación y territorio) "
        "predicen la pobreza monetaria con precisión y estabilidad, y que el modelo es útil para focalizar.")
    en = (
        "Monetary poverty affects more than a quarter of Peru's population, and its timely identification is key "
        "to targeting social programs. The objective was to develop and validate a predictive model based on "
        "machine learning and econometric models to classify households in monetary poverty in Peru using "
        "socioeconomic, demographic, and territorial information from the National Household Survey (ENAHO). The "
        "study used a non-experimental pooled cross-section design with "
        f"{R['obs'].replace(' ', ',')} household-year observations from ENAHO 2017–2024. "
        "Poverty was measured as INEI does, with differences of 0.05 points or less from the official figure; "
        "households interviewed in more than one year were identified, and the expansion factor was used for "
        "population figures. XGBoost, random forest, logistic regression, probit, and k-nearest neighbors were "
        "compared using expanding-window temporal validation, isotonic calibration, and an out-of-sample test with "
        f"ENAHO 2024; variables were interpreted with SHAP values. XGBoost achieved an AUC-ROC of {f(m['auc_roc'])} "
        f"and an AUC-PR of {f(m['auc_pr'])}, outperformed all benchmark models according to the DeLong test "
        f"(p < 0.001), identified {f(100*m['recall'],1)}% of poor households, and estimated a poverty rate of "
        f"{f(m['tasa_predicha'],1)}% compared with the observed {f(m['tasa_real'],1)}%. It is concluded that "
        "observable household characteristics (housing, size, employment, education, and territory) predict "
        "monetary poverty accurately and consistently, and that the model is useful for targeting.")
    return es, en


GLOBALES = [
    ("(véase la Figura 6)", "(véase la sección 4.1.2)"),
    ("con 48 variables estructurales", "con 38 variables estructurales"),
    ("con 39 variables estructurales", "con 38 variables estructurales"),
    # internet se excluyó por no ser comparable entre años (cambio de cuestionario en 2023)
    ("alquiler estimado de la vivienda, internet, celular y TV por cable (−)",
     "alquiler estimado de la vivienda, celular y TV por cable (−)"),
    ("que obligaron a calibrar los umbrales de decisión por dominio geográfico",
     "que en esta tesis se atendieron midiendo el error de la pobreza estimada por departamento y dominio"),
    ("y una calibración regional en los modelos predictivos", "y evaluar el error del modelo por departamento"),
]


def preliminares(body, R, poner_texto, txt):
    hechos_g = 0
    for t in body.iter(qn("w:t")):
        for viejo, nuevo in GLOBALES:
            if t.text and viejo in t.text:
                t.text = t.text.replace(viejo, nuevo); hechos_g += 1
    print("reemplazos en capítulo I:", hechos_g, "(los ya aplicados en una pasada anterior no se repiten)")
    es, en = _resumen(R)
    kids = list(body)
    hechos = set()
    for e in kids:
        t = txt(e)
        if t.startswith("La pobreza monetaria afecta a ") and "res" not in hechos:
            poner_texto(e, es); hechos.add("res")
        elif t.startswith("Monetary poverty affects ") and "abs" not in hechos:
            poner_texto(e, en); hechos.add("abs")
        elif t.startswith("El estudio es cuantitativo y se basa en ") and "int" not in hechos:
            poner_texto(e, "El estudio es cuantitativo y se basa en los microdatos de la ENAHO 2017–2024. Se "
                        "compararon cinco algoritmos, con XGBoost como modelo principal y bosque aleatorio, regresión "
                        "logística, probit y k vecinos más cercanos (KNN) como referencia, para identificar qué "
                        "variables explican la condición de pobreza y cuál de los modelos predice con mayor acierto. "
                        "Antes de modelar se reprodujo la medición oficial de la pobreza, se identificaron los hogares "
                        "entrevistados en más de un año y se definió el uso del factor de expansión.")
            hechos.add("int")
        elif t.startswith("La regresión cuantil extiende") and "cua" not in hechos:
            if "no se usa como clasificador" not in t:
                poner_texto(e, t.rstrip() + " En esta investigación no se usa como clasificador porque la variable "
                            "dependiente es binaria; como referencia lineal se emplean la regresión logística y el probit.")
            hechos.add("cua")
    faltan = {"res", "abs", "int", "cua"} - hechos
    if faltan:
        print("AVISO: no se actualizaron", faltan)
    print("palabras resumen:", len(es.split()), "abstract:", len(en.split()))


REFERENCIAS = [
    ("Breiman", "Brown, C., Ravallion, M., & van de Walle, D. (2018). A poor means test? Econometric targeting in "
     "Africa. *Journal of Development Economics, 134*, 109–124. "
     "https://econpapers.repec.org/RePEc:eee:deveco:v:134:y:2018:i:c:p:109-124"),
    ("Del Canto", "DeLong, E. R., DeLong, D. M., & Clarke-Pearson, D. L. (1988). Comparing the areas under two or "
     "more correlated receiver operating characteristic curves: A nonparametric approach. *Biometrics, 44*(3), "
     "837–845. https://doi.org/10.2307/2531595"),
    ("Greene", "Grosh, M. E., & Baker, J. L. (1995). *Proxy means tests for targeting social programs: Simulations "
     "and speculation* (LSMS Working Paper N.° 118). World Bank. "
     "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/750401468776352539"),
    ("Koenker", "Lanjouw, P., & Ravallion, M. (1995). Poverty and household size. *The Economic Journal, "
     "105*(433), 1415–1434. https://doi.org/10.2307/2235108"),
    ("Solís-Salazar", "Solon, G., Haider, S. J., & Wooldridge, J. M. (2015). What are we weighting for? *Journal "
     "of Human Resources, 50*(2), 301–316. https://doi.org/10.3368/jhr.50.2.301"),
]


def bibliografia(body, txt):
    kids = list(body)
    i_bib = next(i for i, e in enumerate(kids) if txt(e).strip() == "BIBLIOGRAFÍA" and i > 300)
    i_anx = next(i for i, e in enumerate(kids) if txt(e).strip() == "ANEXOS" and i > i_bib)
    refs = kids[i_bib + 1:i_anx]
    for despues_de, texto in REFERENCIAS:
        clave = texto.split(",")[0]
        if any(txt(e).startswith(clave + ",") for e in refs):
            continue
        ancla = next(e for e in refs if txt(e).startswith(despues_de))
        nuevo = copy.deepcopy(ancla)
        for hijo in list(nuevo):
            if hijo.tag != qn("w:pPr"):
                nuevo.remove(hijo)
        c._runs(nuevo, texto)
        ancla.addnext(nuevo)


MATRIZ = [
    ("Regresión Probit, regresión por cuantiles y KNN (referencia)",
     "bosque aleatorio, regresión logística, regresión probit y KNN (referencia)"),
    ("XGBoost, Probit, regresión por cuantiles, KNN", "XGBoost, bosque aleatorio, logística, probit, KNN"),
    ("277 136 hogares de la ENAHO 2017–2024 (≈ 34 642 hogares por año).",
     "277 136 observaciones hogar-año de la ENAHO 2017–2024 (207 037 hogares distintos)."),
    ("Brecha educativa intrahogar", "Brecha educativa intrahogar (excluida por colinealidad exacta)"),
    ("Índice de privación material", "Índice de privación material (excluido por colinealidad exacta)"),
    ("calibración isotónica y umbral óptimo", "calibración isotónica, umbral elegido en el año de calibración y prueba de DeLong"),
    ("Conexión a Internet", "Conexión a Internet (excluida por no ser comparable entre años)"),
]


def matriz(body, txt):
    hechos = 0
    for t in body.iter(qn("w:t")):
        for viejo, nuevo in MATRIZ:
            if t.text and viejo in t.text and nuevo not in t.text:
                t.text = t.text.replace(viejo, nuevo); hechos += 1
    print("matriz: reemplazos", hechos)


# ----------------------------------------------------------------- índices
def _entrada(plantilla, letra, n, titulo, pagina):
    e = copy.deepcopy(plantilla)
    for it in e.iter(qn("w:instrText")):
        it.text = re.sub(r"_Epg(\w)([NT])\d+", lambda m: f"_Epg{letra}{m.group(2)}{n}", it.text)
    ts = [t for t in e.iter(qn("w:t"))]
    ts[0].text = str(n); ts[2].text = titulo; ts[3].text = str(pagina)
    return e


def indices(body, ctx, txt, estilo, paginas):
    kids = list(body)
    rotulos = {"T": [], "F": []}
    for it in body.iter(qn("w:instrText")):
        m = re.match(r' TC "(\d+)\. (.*)" \\f ([TF]) ', it.text or "")
        if m:
            rotulos[m.group(3)].append((int(m.group(1)), m.group(2)))
    for letra, titulo_indice in (("T", "ÍNDICE DE TABLAS"), ("F", "ÍNDICE DE FIGURAS")):
        kids = list(body)
        i0 = next(i for i, e in enumerate(kids) if txt(e).strip() == titulo_indice)
        entradas = []
        j = i0 + 2
        while estilo(kids[j]) == "TDC5":
            entradas.append(kids[j]); j += 1
        plantilla = copy.deepcopy(entradas[0])
        for e in entradas[1:]:
            body.remove(e)
        ancla = entradas[0]
        for n, titulo in sorted(rotulos[letra]):
            ancla.addprevious(_entrada(plantilla, letra, n, titulo, paginas.get(f"{letra}{n}", "")))
        body.remove(ancla)
    print("índices:", len(rotulos["T"]), "tablas,", len(rotulos["F"]), "figuras")


def _encabezados(body, txt, estilo, cap, siguiente):
    kids = list(body)
    i = next(k for k, e in enumerate(kids) if txt(e).strip() == cap and not estilo(e).startswith("TDC"))
    salida, n2, n3 = [], 0, 0
    numero = {"CAPÍTULO I": 1, "CAPÍTULO III": 3, "CAPÍTULO IV": 4}[cap]
    for e in kids[i + 1:]:
        if txt(e).strip() == siguiente:
            break
        s = estilo(e)
        if s in ("Ttulo2", "Ttulo3"):
            if s == "Ttulo2":
                n2 += 1; n3 = 0; num = f"{numero}.{n2}"
            else:
                n3 += 1; num = f"{numero}.{n2}.{n3}"
            marca = next((b.get(qn("w:name")) for b in e.iter(qn("w:bookmarkStart"))
                          if b.get(qn("w:name")).startswith("_Toc")), None)
            salida.append((s, num, txt(e).strip(), marca))
    return salida


def _rellenar(entrada, num, titulo, marca, pagina):
    hl = entrada.find(qn("w:hyperlink"))
    hl.set(qn("w:anchor"), marca)
    ts = [t for t in hl.iter(qn("w:t"))]
    ts[0].text = num; ts[1].text = titulo; ts[2].text = str(pagina)
    for it in hl.iter(qn("w:instrText")):
        it.text = f" PAGEREF {marca} \\h "


def toc(body, txt, estilo, paginas):
    for cap, titulo_cap, siguiente in (("CAPÍTULO I", "REVISIÓN DE LITERATURA", "CAPÍTULO II"),
                                        ("CAPÍTULO III", "MATERIALES Y MÉTODOS", "CAPÍTULO IV"),
                                        ("CAPÍTULO IV", "RESULTADOS Y DISCUSIÓN", "CONCLUSIONES")):
        heads = _encabezados(body, txt, estilo, cap, siguiente)
        kids = list(body)
        i0 = next(k for k, e in enumerate(kids) if estilo(e) == "TDC4" and txt(e).strip() == titulo_cap)
        entradas = []
        j = i0 + 1
        while estilo(kids[j]) in ("TDC2", "TDC3"):
            entradas.append(kids[j]); j += 1
        plant = {s: copy.deepcopy(next(e for e in entradas[1:] + entradas if estilo(e) == s
                                       and e.find(".//" + qn("w:instrText")) is not None
                                       and "TOC" not in "".join(x.text for x in e.iter(qn("w:instrText")))))
                 for s in ("TDC2", "TDC3") if any(estilo(e) == s for e in entradas)}
        if "TDC3" not in plant:
            plant["TDC3"] = copy.deepcopy(plant["TDC2"])
            plant["TDC3"].find(qn("w:pPr")).find(qn("w:pStyle")).set(qn("w:val"), "TDC3")
        primera = entradas[0]
        for e in entradas[1:]:
            body.remove(e)
        s, num, tit, marca = heads[0]
        _rellenar(primera, num, tit, marca, paginas.get(marca, ""))
        ancla = primera
        for s, num, tit, marca in heads[1:]:
            nueva = copy.deepcopy(plant["TDC2" if s == "Ttulo2" else "TDC3"])
            _rellenar(nueva, num, tit, marca, paginas.get(marca, ""))
            ancla.addnext(nueva); ancla = nueva
    print("índice general actualizado")


def fijar_pageref(body, paginas):
    """Escribe el número de página en caché de cada campo PAGEREF cuyo marcador se conoce."""
    hechos = 0
    for p in body.iter(qn("w:p")):
        pendiente, separado = None, False
        for el in p.iter(qn("w:instrText"), qn("w:fldChar"), qn("w:t")):
            if el.tag == qn("w:instrText"):
                m = re.match(r"\s*PAGEREF (\S+)", el.text or "")
                pendiente, separado = (m.group(1), False) if m else (None, False)
            elif el.tag == qn("w:fldChar"):
                tipo = el.get(qn("w:fldCharType"))
                if tipo == "separate" and pendiente:
                    separado = True
                elif tipo == "end":
                    pendiente, separado = None, False
            elif separado and pendiente in paginas and paginas[pendiente] != "":
                el.text = str(paginas[pendiente]); hechos += 1
                pendiente, separado = None, False
    print("PAGEREF actualizados:", hechos)


PUENTE_MT = [
    "Capacidades (Sen, 1995): la falta de educación y de salud limita lo que el hogar puede lograr. Variables: años "
    "de estudio promedio y máximos (−), analfabetismo (+), asistencia escolar (−), seguro de salud y enfermedad crónica (+).",
    "Enfoque multidimensional (Alkire y Foster, 2011): la pobreza se manifiesta en privaciones de la vivienda y de los "
    "servicios. Variables: piso de tierra, paredes precarias, hacinamiento y cocina con leña o carbón (+); agua y "
    "desagüe de red pública y electricidad (−).",
    "Círculo de la pobreza (Myrdal, 1957): el empleo precario reproduce la pobreza. Variables: tasa de ocupación (−), "
    "tasa de informalidad y ocupados informales (+).",
    "Tamaño y composición del hogar (Lanjouw y Ravallion, 1995): más miembros y más dependientes reducen el gasto per "
    "cápita. Variables: miembros del hogar, menores de 18 años y razón de dependencia (+).",
    "Estructuralismo (Sosa Escudero, 2023): la pobreza depende del territorio y de la estructura productiva. "
    "Variables: dominio geográfico, estrato, área rural y departamento.",
    "Focalización por proxy (Grosh y Baker, 1995; Brown et al., 2018): los activos y la calidad de la vivienda indican "
    "el bienestar cuando no se observa el gasto. Variables: alquiler estimado de la vivienda, celular y TV por cable (−).",
    "Protección social focalizada: los programas se asignan a los hogares pobres. Variables: JUNTOS, Pensión 65, Qali "
    "Warma, Vaso de Leche y afiliación solo al SIS (+, por focalización y no como efecto del programa).",
    "Dinámica y choques (Cantó et al., 2012): los choques generan pobreza transitoria. Variable: año de la COVID-19 (+).",
]


def marco_teorico(body, txt, estilo):
    """Añade 1.1.9: la relación teoría → variable → signo esperado (observación del asesor)."""
    if any(txt(e).strip() == "De las teorías a las variables del modelo" for e in body):
        return
    kids = list(body)
    i_cap1 = next(k for k, e in enumerate(kids) if txt(e).strip() == "CAPÍTULO I" and not estilo(e).startswith("TDC"))
    i_ant = next(k for k in range(i_cap1, len(kids)) if estilo(kids[k]) == "Ttulo2" and txt(kids[k]).strip() == "Antecedentes")
    n_tabla = next(re.match(r' TC "(\d+)\.', it.text).group(1) for it in body.iter(qn("w:instrText"))
                   if (it.text or "").startswith(' TC "') and "Relación entre las teorías" in it.text)
    nuevos = [c.titulo(3, "De las teorías a las variables del modelo"),
              c.parrafo("Las teorías revisadas cumplen una función concreta en esta investigación: cada una propone un "
                        "mecanismo por el que un hogar es pobre, y ese mecanismo se traduce en variables observables de la "
                        "ENAHO con un signo esperado. Así, el modelo no elige sus predictores solo por su capacidad "
                        "predictiva, sino a partir de la teoría, y su resultado puede contrastarse con ella:", 3)]
    nuevos += c.vinetas(PUENTE_MT, 3)
    nuevos.append(c.parrafo(f"En el capítulo IV (Tabla {n_tabla}) se resume esta correspondencia y se compara el signo "
                            "esperado de cada variable con el efecto que aprendió el modelo, medido con valores SHAP. Las "
                            "variables que definen la pobreza o se calculan con el gasto o el ingreso no se incluyen, "
                            "porque el objetivo es predecir la pobreza a partir de características que se observan sin "
                            "medir el gasto.", 3))
    for el in nuevos:
        kids[i_ant].addprevious(el)
