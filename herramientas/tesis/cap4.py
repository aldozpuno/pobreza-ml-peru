"""Contenido del Capítulo IV: resultados por objetivo específico y discusión."""

from __future__ import annotations

import cierre
import constructor as c
from datos import FIG, NOMBRES, f, miles

OE1 = ("Identificar variables relevantes para construir un modelo predictivo efectivo, en función a un "
       "análisis exhaustivo de los factores económicos, sociales y demográficos que pueden desempeñar un "
       "papel crucial en la determinación de la pobreza")
OE2 = ("Aplicar técnicas de aprendizaje automático (Machine Learning), como algoritmos de inteligencia "
       "artificial, para entrenar y ajustar de manera efectiva el modelo predictivo")
OE3 = ("Evaluar la precisión y el rendimiento del modelo predictivo desarrollado utilizando métricas de "
       "evaluación como la precisión, el sesgo y la sensibilidad")

FUENTE = "Elaborado con los microdatos de la ENAHO 2017–2024 del INEI."
ABREV = "Exh.: exhaustividad (recall); Prec.: precisión. "
CODIGOS = {"sumaria": "34", "vivienda": "01", "miembros": "02", "educacion": "03", "salud": "04",
           "empleo": "05", "programas": "37"}


def construir(doc, R, ctx) -> list:
    E = []
    add = E.extend
    N = 4  # nivel de sangría del contenido (bajo títulos N4)
    p = lambda t, n=N: E.append(c.parrafo(t, n))
    h = lambda n, t: E.append(c.titulo(n, t))
    tabla = lambda titulo, enc, filas, anchos, num=None, nota=None: add(
        c.bloque_tabla(ctx["tab"](), titulo, enc, filas, anchos, N, num, nota))
    figura = lambda titulo, archivo, ancho=12.4, nota=None: add(
        c.bloque_figura(doc, ctx["fig"](), titulo, str(archivo), ancho, N, nota))
    T = lambda: ctx["tab_siguiente"]
    F = lambda: ctx["fig_siguiente"]
    m = R["m"]

    h(2, "Resultados")
    # ------------------------------------------------------------------ OE1
    h(3, OE1)
    p("Esta sección presenta la construcción de la base de datos, la medición de la pobreza que sirve de "
      "variable dependiente, el tratamiento de los hogares que se repiten entre años y la selección de las "
      "variables predictoras a partir de la teoría.", 3)

    h(4, "Módulos de la ENAHO utilizados")
    p(f"La base se construyó con siete módulos de la ENAHO para cada año de 2017 a 2024 (Tabla {T()}). La "
      "Sumaria es la tabla base: cada hogar con encuesta completa aporta una fila, y los demás módulos se "
      "unen a ella por la llave del hogar.")
    tabla("Módulos de la ENAHO 2017–2024 utilizados en el modelo predictivo",
          ["Módulo", "Contenido", "Uso en el estudio"], [
              ["01 (100)", "Características de la vivienda y del hogar", "Vivienda, servicios, activos y variable PANEL"],
              ["02 (200)", "Características de los miembros del hogar", "Composición del hogar y jefatura"],
              ["03 (300)", "Educación", "Años de estudio, analfabetismo y asistencia escolar"],
              ["04 (400)", "Salud", "Seguro de salud y enfermedad crónica"],
              ["05 (500)", "Empleo e ingresos", "Ocupación e informalidad"],
              ["37 (700)", "Programas sociales", "JUNTOS, Pensión 65, Qali Warma y Vaso de Leche"],
              ["34", "Sumaria", "Pobreza, factor de expansión, miembros y territorio"],
          ], [2.3, 5.5, 6.2], nota=FUENTE)

    h(4, "Medición de la pobreza monetaria")
    a = R["anual"]
    p(f"Antes de entrenar los modelos se reprodujo la incidencia oficial de la pobreza con la fórmula del INEI. "
      f"En los ocho años la tasa calculada difiere de la cifra oficial en 0.05 puntos porcentuales o menos "
      f"(Tabla {T()}), lo que confirma que la variable dependiente está bien construida. La pobreza bajó de "
      f"{f(a.tasa_personas.iloc[0],1)} % en 2017 a {f(a.tasa_personas.iloc[2],1)} % en 2019, subió a "
      f"{f(a.tasa_personas.iloc[3],1)} % en 2020 por la pandemia y se ubicó en {f(a.tasa_personas.iloc[-1],1)} % en 2024.")
    filas = [[str(r.anio), miles(r.hogares_muestra), f(r.tasa_personas, 2), f(r.tasa_hogares, 2),
              f(r.tasa_oficial_inei, 1), f(r.diferencia_pp, 2)] for r in a.itertuples()]
    tabla("Incidencia de la pobreza monetaria reproducida y cifra oficial del INEI, 2017–2024",
          ["Año", "Hogares", "Personas (%)", "Hogares (%)", "INEI (%)", "Diferencia (pp)"], filas,
          [1.6, 2.4, 2.6, 2.6, 2.2, 2.8], {1, 2, 3, 4, 5},
          "Personas: ponderado por FACTOR07 × MIEPERHO; hogares: ponderado por FACTOR07. " + FUENTE)
    p("La tasa de hogares es menor que la de personas porque los hogares pobres tienen más miembros. Esta "
      "distinción explica la diferencia con la versión anterior del estudio, que informaba tasas de hogares "
      f"(Figura {F()}).")
    figura("Pobreza monetaria en personas y hogares, y cifra oficial del INEI, 2017–2024",
           FIG / "fig_incidencia_anual.png", 12.4)
    ar = R["area"]
    rural = ar[(ar.anio == 2024) & (ar.rural == 1)].tasa_personas.iloc[0]
    urbana = ar[(ar.anio == 2024) & (ar.rural == 0)].tasa_personas.iloc[0]
    urb17 = ar[(ar.anio == 2017) & (ar.rural == 0)].tasa_personas.iloc[0]
    p(f"Por área de residencia, la pobreza rural ({f(rural,1)} % en 2024) sigue siendo mucho mayor que la "
      f"urbana ({f(urbana,1)} %), aunque la brecha se redujo porque la pobreza urbana subió desde "
      f"{f(urb17,1)} % en 2017 (Figura {F()}).")
    figura("Pobreza monetaria por área de residencia, 2017–2024", FIG / "fig_incidencia_area.png", 12.4)

    h(4, "Características de los hogares pobres y no pobres")
    de = R["descriptivo"]
    medias = {"mieperho", "n_menores", "ratio_dependencia", "educ_prom", "hacinamiento", "alquiler_imputado"}
    unidad = {"mieperho": "personas", "n_menores": "personas", "ratio_dependencia": "razón", "educ_prom": "años",
              "hacinamiento": "personas por habitación", "alquiler_imputado": "S/ al mes"}
    # proporciones calculadas sobre miembros u ocupados del hogar, no sobre hogares
    proporcion = {"tasa_analfabetismo": "% de miembros", "tasa_ocupacion": "% de miembros",
                  "solo_sis": "% de miembros", "tasa_informalidad": "% de ocupados"}
    filas = []
    for r in de.itertuples():
        if r.v in medias:
            filas.append([r.etiqueta, unidad[r.v], f(r.pobres, 2), f(r.no_pobres, 2)])
        else:
            filas.append([r.etiqueta, proporcion.get(r.v, "% de hogares"), f(100 * r.pobres, 1), f(100 * r.no_pobres, 1)])
    alq = de[de.v == "alquiler_imputado"].iloc[0]; mie = de[de.v == "mieperho"].iloc[0]
    edu = de[de.v == "educ_prom"].iloc[0]; inf = de[de.v == "tasa_informalidad"].iloc[0]
    p(f"Los hogares pobres difieren de los no pobres en casi todas las características observadas (Tabla {T()}). "
      f"En 2024 tenían en promedio {f(mie.pobres,1)} miembros frente a {f(mie.no_pobres,1)}, {f(edu.pobres,1)} años de "
      f"estudio promedio frente a {f(edu.no_pobres,1)}, una tasa de informalidad de {f(100*inf.pobres,0)} % frente a "
      f"{f(100*inf.no_pobres,0)} % y un alquiler estimado de su vivienda de S/ {f(alq.pobres,0)} frente a "
      f"S/ {f(alq.no_pobres,0)} al mes. También vivían con más hacinamiento, con más frecuencia en viviendas con "
      "piso de tierra y sin desagüe de red pública, y recibían más programas sociales.")
    tabla("Características de los hogares pobres y no pobres, ENAHO 2024",
          ["Variable", "Unidad", "Pobres", "No pobres"], filas, [5.4, 4.2, 2.7, 2.7], {2, 3},
          "Promedios y porcentajes ponderados por FACTOR07. " + FUENTE)
    p("Estas diferencias son coherentes con el signo esperado de cada variable y anticipan qué información usará "
      "el modelo para distinguir a los hogares pobres.")

    h(4, "Hogares entrevistados en más de un año")
    pn = R["panel"]
    p(f"La base apilada tiene {R['obs']} observaciones hogar-año y {R['distintos']} hogares distintos. Cada "
      f"año, entre {R['rep_min']} % y {R['rep_max']} % de los hogares ya habían sido entrevistados "
      f"(Tabla {T()}). La pregunta PANEL y la llave del año anterior identifican casi a los mismos hogares, "
      "lo que confirma que la marca de repetidos es consistente.")
    filas = [[str(r.anio), miles(r.hogares), miles(r.pregunta_panel), miles(r.llave_anio_anterior),
              miles(r.repetidos), f(r.pct_repetidos, 1)] for r in pn.itertuples()]
    tabla("Hogares entrevistados en más de un año en la base apilada, ENAHO 2017–2024",
          ["Año", "Hogares", "PANEL = Sí", "Misma llave el año anterior", "Repetidos", "Repetidos (%)"], filas,
          [1.5, 2.2, 2.4, 3.6, 2.3, 2.4], {1, 2, 3, 4, 5},
          "Repetido: la pregunta PANEL del módulo 100 es Sí, o la llave CONGLOME–VIVIENDA–HOGAR aparece en un "
          "año anterior. En 2017 no hay año anterior en la base. " + FUENTE)
    p(f"Como un mismo hogar puede estar en el entrenamiento y en la prueba, la evaluación final se repitió "
      f"solo con los hogares nunca vistos; los resultados se presentan en la sección del tercer objetivo "
      f"(Figura {F()}).")
    figura("Proporción de hogares repetidos por año según el criterio de identificación",
           FIG / "fig_hogares_repetidos.png", 12.4)

    h(4, "Variables excluidas por fuga de datos")
    p(f"Se excluyeron las variables que definen la pobreza o que se calculan con el gasto o el ingreso "
      f"(Tabla {T()}). Con ellas el modelo reproduciría la regla del INEI en lugar de predecir la pobreza a "
      "partir de características observables del hogar.")
    tabla("Variables de la Sumaria excluidas del modelo por fuga de datos",
          ["Variable", "Motivo de exclusión"],
          [[r.nombre.upper(), r.motivo.replace("`covid`", "la indicadora COVID-19")] for r in R["fuga"].itertuples()],
          [3.2, 11.8], nota=FUENTE)

    h(4, "Variable excluida por no ser comparable entre años")
    ia = R["internet_anual"]
    p("La conexión a internet del hogar (P1144) se excluyó por una razón distinta: su definición cambió dentro "
      "del periodo. Hasta 2022 el porcentaje de hogares con conexión creció de forma gradual, de "
      f"{f(ia[2017],1)} % en 2017 a {f(ia[2022],1)} % en 2022. En 2023, cuando el cuestionario añadió las "
      "preguntas sobre el tipo de conexión (fija, móvil pospago y móvil prepago) y P1144 empezó a contar el "
      f"internet móvil, subió a {f(ia[2023],1)} %, y en 2024 fue {f(ia[2024],1)} %. Un salto de esa magnitud "
      "en un año no refleja un cambio en los hogares sino en la pregunta. Mantenerla habría hecho que el modelo "
      "aprendiera con una definición (2017–2022) y se evaluara con otra (2023–2024); por eso se retiró, igual "
      "que se reconstruyó la informalidad para que significara lo mismo en todos los años.")

    h(4, "Diagnóstico de multicolinealidad")
    v = R["vif"]
    p("El diagnóstico con el factor de inflación de la varianza (VIF) detectó dos variables que eran "
      "combinación lineal exacta de otras: la brecha educativa (años de estudio máximos menos el promedio) y el "
      "índice de privación (suma de seis privaciones de la vivienda que ya entran por separado). Ambas se "
      f"retiraron. Con las variables restantes, el VIF máximo es {f(v.VIF.max(),2)}, por debajo del límite de "
      f"10 (Tabla {T()}).")
    etq = dict(zip(R["imp"].variable, R["imp"].etiqueta))
    filas = [[etq.get(r.Variable, r.Variable), f(r.VIF, 2), r.Diagnóstico] for r in v.head(12).itertuples()]
    tabla("Factor de inflación de la varianza de los predictores numéricos del modelo final",
          ["Variable", "VIF", "Diagnóstico"], filas, [6, 3, 6], {1},
          "Se muestran las doce variables con mayor VIF. " + FUENTE)
    p("Los años de estudio promedio y máximos tienen una colinealidad moderada, esperable porque ambos "
      "resumen la educación del hogar. Se mantienen porque miden aspectos distintos: el nivel general y el "
      "miembro más educado. Esta colinealidad no afecta a XGBoost y en los modelos lineales solo amplía la "
      "varianza de esos dos coeficientes.")

    h(4, "Variables predictoras y teorías de la pobreza")
    p(f"Las {R['n_vars']} variables del modelo final se agrupan según la teoría de la pobreza que justifica su "
      f"inclusión (Tabla {T()}). Cada variable tiene un signo esperado; en el segundo objetivo ese signo se "
      "compara con el efecto que aprendió el modelo.")
    pu = R["puente"]
    tabla("Relación entre las teorías de la pobreza y las variables del modelo",
          ["Teoría", "Variables del modelo", "N.°"],
          [[r.Teoría, r.Variables, str(r.Cantidad)] for r in pu.itertuples()], [4.6, 9.2, 1.2], {2},
          FUENTE)
    p(f"El detalle de cada variable, con su módulo de origen, su definición y su signo esperado, se presenta "
      f"en la Tabla {T()}.")
    va = R["variables"]
    tabla("Diccionario de las variables predictoras del modelo final",
          ["Variable", "Definición", "Módulo", "Signo"],
          [[r.Etiqueta, r.Definición, CODIGOS.get(r._3, r._3), r._7] for r in va.itertuples()], [3.0, 6.6, 1.5, 1.3], {2, 3},
          "Módulo: código del módulo de la ENAHO. Signo esperado: + aumenta la probabilidad de pobreza; − la reduce; ± depende de la categoría. " + FUENTE)

    # ------------------------------------------------------------------ OE2
    h(3, OE2)
    h(4, "Comparación de algoritmos")
    cm = R["comparacion"].sort_values("auc_roc", ascending=False)
    mejor, seg = cm.iloc[0], cm.iloc[1]
    p(f"Los cinco algoritmos se entrenaron con los mismos datos y pliegues. En el promedio de los cuatro "
      f"pliegues de validación, XGBoost obtuvo el mayor AUC-ROC ({f(mejor.auc_roc)}) y el mayor AUC-PR "
      f"({f(mejor.auc_pr)}), seguido del probit ({f(seg.auc_roc)}) y la regresión logística "
      f"(Tabla {T()}). KNN fue el de peor desempeño.")
    filas = [[NOMBRES[r.estimador], f(r.auc_roc), f(r.auc_pr), f(r.brier), f(r.recall), f(r.precision), f(r.f1)]
             for r in cm.itertuples()]
    tabla("Desempeño de los algoritmos en la validación temporal, promedio de los pliegues 2020–2023",
          ["Modelo", "AUC-ROC", "AUC-PR", "Brier", "Exh.", "Prec.", "F1"], filas,
          [3.2, 1.6, 1.6, 1.5, 1.5, 1.5, 1.5], {1, 2, 3, 4, 5, 6}, ABREV + FUENTE)
    p(f"La ventaja de XGBoost sobre los modelos econométricos es moderada en AUC-ROC (alrededor de "
      f"{f(mejor.auc_roc - seg.auc_roc, 3)}), "
      "pero se mantiene en todas las métricas de discriminación y en el Brier, que mide la calidad de las "
      f"probabilidades. La Figura {F()} compara el AUC-PR, la métrica más exigente cuando los hogares pobres "
      "son minoría. En el tercer objetivo se contrasta si esta diferencia es estadísticamente significativa.")
    figura("Comparación de los algoritmos en la validación temporal según el AUC-PR",
           FIG / "fig_comparacion_modelos.png", 12.4)
    pv = R["pliegues_m"][R["pliegues_m"].estimador.isin(list(cm.estimador))]
    piv = pv.pivot_table(index="estimador", columns="pliegue", values="auc_roc").loc[list(cm.estimador)]
    anios_ev = {pl["nombre"]: str(pl["evalua"]) for pl in R["pliegues"]}
    p(f"El orden de los modelos se mantiene año a año: XGBoost obtuvo el mayor AUC-ROC en cada uno de los cinco "
      f"años evaluados, incluido 2020, y KNN el menor (Tabla {T()}). La regresión logística y el probit tienen un "
      "desempeño casi idéntico, como es de esperar en dos modelos lineales que solo difieren en la función de enlace.")
    tabla("AUC-ROC de los algoritmos por año de evaluación",
          ["Modelo"] + [anios_ev.get(c_, c_) for c_ in piv.columns],
          [[NOMBRES[k]] + [f(v) for v in fila] for k, fila in piv.iterrows()],
          [3.8] + [2.24] * len(piv.columns), set(range(1, len(piv.columns) + 1)),
          "2020–2023: pliegues de validación; 2024: prueba final. " + FUENTE)

    h(4, "Entrenamiento temporal, calibración y umbral")
    p(f"El esquema de validación aplicado se muestra en la Figura {F()}. En cada pliegue el modelo aprende "
      "con los años anteriores, calibra sus probabilidades y elige el umbral con el año siguiente, y se "
      "evalúa con el año posterior.")
    figura("Esquema de la validación temporal con ventana expansiva, ENAHO 2017–2024",
           FIG / "fig_esquema_validacion.png", 12.4)
    pm = R["pliegues_m"]; x = pm[pm.estimador == "xgboost"]
    anios = {pl["nombre"]: str(pl["evalua"]) for pl in R["pliegues"]}
    filas = [[anios.get(r.pliegue, r.pliegue), f(r.auc_roc), f(r.auc_pr), f(r.brier), f(r.recall),
              f(r.precision), f(r.f1)] for r in x.itertuples()]
    p(f"El desempeño de XGBoost fue estable en los cinco años de evaluación (Tabla {T()}): el AUC-ROC se "
      f"mantuvo entre {f(x.auc_roc.min(),3)} y {f(x.auc_roc.max(),3)}. En 2020, año de la pandemia, la "
      f"exhaustividad bajó a {f(x.recall.iloc[0],3)}: muchos hogares cayeron en pobreza por la pérdida de "
      "ingresos sin cambiar todavía su vivienda ni su educación, que son las características que el modelo "
      "observa. Al incluir 2020 en el entrenamiento, la exhaustividad se recuperó desde 2021.")
    tabla("Desempeño de XGBoost por año de evaluación",
          ["Año evaluado", "AUC-ROC", "AUC-PR", "Brier", "Exh.", "Prec.", "F1"], filas,
          [1.8, 1.8, 1.8, 1.75, 1.75, 1.75, 1.75], {1, 2, 3, 4, 5, 6},
          "2020–2023: pliegues de validación; 2024: prueba final. " + ABREV + FUENTE)
    p(f"Las probabilidades se calibraron con regresión isotónica y el umbral que maximiza el F1 se eligió en "
      f"el año de calibración. Para la prueba final el umbral fue {R['umbral']}, elegido con la ENAHO 2023: "
      f"un hogar se clasifica como pobre si su probabilidad calibrada supera ese valor.")

    h(4, "Interpretación del modelo con valores SHAP")
    im = R["imp"]
    top = im.head(7)
    propios = ("Qali Warma", "Pensión 65", "Vaso de Leche")  # nombres propios: conservan la mayúscula
    minus = lambda e: e if e[1:2].isupper() or e.startswith(propios) else e[0].lower() + e[1:]
    lista = lambda s: ", ".join(s[:-1]) + (" y " if len(s) > 1 else "") + s[-1]
    siguientes = [f"{minus(r.etiqueta)} ({f(r.importancia, 2)})" for r in top.iloc[1:].itertuples()]
    p(f"La Figura {F()} ordena las variables por su importancia media. El alquiler estimado de la vivienda "
      f"(P106) es la más importante ({f(top.importancia.iloc[0],2)}). Le siguen, en este orden: "
      f"{lista(siguientes)}. El valor de la vivienda, la ocupación y la educación reducen la probabilidad de "
      "pobreza; el tamaño del hogar, el hacinamiento, la informalidad y el piso de tierra la aumentan.")
    figura("Importancia de las variables según la media del valor SHAP absoluto, ENAHO 2024",
           FIG / "fig_importancia_shap.png", 12.4,
           "Verde: la variable reduce la probabilidad de pobreza; rojo: la aumenta; gris: variables por "
           "categorías, sin una dirección única. " + FUENTE)
    d = R["discordantes"]
    contrarios = d[d.signo_observado.isin(["+", "-"])].sort_values("importancia", ascending=False)
    sin_dir = d[~d.signo_observado.isin(["+", "-"])]
    # variables con signo esperado, de mayor a menor importancia: cuántas coinciden antes de la primera que no
    con_signo = im[im.signo_esperado.isin(["+", "-"])]
    primeras = int((con_signo.signo_esperado != con_signo.signo_observado).to_numpy().argmax())
    mayor = contrarios.iloc[0]
    texto_sin_dir = ""
    if len(sin_dir):
        nombres = lista([minus(e).replace(" (2020)", "") for e in sin_dir.etiqueta])
        texto_sin_dir = (f"{len(sin_dir)} no {'muestra' if len(sin_dir) == 1 else 'muestran'} una dirección "
                         f"definida ({nombres}: la indicadora vale cero en todos los hogares de 2024) y ")
    p(f"En {R['n_coincide']} de las {R['n_signo']} variables con signo esperado, el efecto aprendido coincide "
      f"con el que predice su teoría, incluidas las {primeras} de mayor importancia. De las {len(d)} restantes, "
      f"{texto_sin_dir}{len(contrarios)} tienen el signo contrario: "
      f"{lista([minus(e) for e in contrarios.etiqueta])}. Salvo la primera, cuya importancia es "
      f"{f(mayor.importancia, 2)}, son variables de poca importancia, y en las de importancia casi nula el "
      "signo observado no es informativo. El signo del estrato y del área rural es un efecto condicional: "
      "comparten información con el dominio, el departamento y los servicios de la vivienda, de modo que el "
      "modelo atribuye a esas variables la mayor parte del efecto territorial. Los programas sociales se "
      "asocian con la pobreza porque se asignan a hogares pobres; es una relación de focalización, no un "
      "efecto del programa.")
    pe = R["periodos"].sort_values("cambio", ascending=False)
    sube, baja = pe.iloc[0], pe.iloc[-1]
    p(f"Al explicar el mismo modelo con los hogares de 2017–2019 y de 2021–2024 (Figura {F()}), el orden de "
      f"las variables casi no cambia. La que más ganó importancia es {minus(etq.get(sube.variable, sube.variable))}, "
      f"de {f(sube.importancia_antes,2)} a {f(sube.importancia_despues,2)}, y la que más perdió es "
      f"{minus(etq.get(baja.variable, baja.variable))}, de {f(baja.importancia_antes,2)} a "
      f"{f(baja.importancia_despues,2)}. Los determinantes que usa el modelo son, por tanto, estables antes y "
      "después de la pandemia.")
    figura("Importancia de las variables antes (2017–2019) y después (2021–2024) de la pandemia",
           FIG / "fig_shap_periodos.png", 12.4, FUENTE)

    # ------------------------------------------------------------------ OE3
    h(3, OE3)
    h(4, "Desempeño en el año de prueba")
    pr = R["prueba"]
    nv = pr[pr.Variante.str.startswith("Solo hogares no vistos")].iloc[0]
    po = pr[pr.Variante.str.contains("ponderado")].iloc[0]
    p(f"En la ENAHO 2024, que no se usó en ninguna etapa anterior, XGBoost alcanzó un AUC-ROC de "
      f"{f(m['auc_roc'])} y un AUC-PR de {f(m['auc_pr'])}, e identificó al {f(100*m['recall'],1)} % de los "
      f"hogares pobres (Tabla {T()}). El resultado casi no cambia al ponderar por el factor de expansión "
      f"(AUC-ROC {f(po.auc_roc)}) ni al evaluar solo con los {miles(nv.hogares)} hogares nunca vistos "
      f"(AUC-ROC {f(nv.auc_roc)}). Por tanto, los hogares repetidos de la base apilada no inflan el desempeño.")
    filas = [[r.Variante, miles(r.hogares), f(r.auc_roc), f(r.auc_pr), f(r.recall), f(r.precision), f(r.tasa_predicha, 2)]
             for r in pr.itertuples()]
    tabla("Desempeño de XGBoost en la ENAHO 2024 según los hogares evaluados",
          ["Hogares evaluados", "N.°", "AUC-ROC", "AUC-PR", "Exh.", "Prec.", "Pobreza estimada (%)"], filas,
          [3.3, 1.7, 1.5, 1.5, 1.3, 1.3, 1.8], {1, 2, 3, 4, 5, 6},
          ABREV + "Pobreza estimada: promedio de las probabilidades calibradas ponderado por FACTOR07 × MIEPERHO. " + FUENTE)

    h(4, "Prueba de hipótesis")
    dl = R["delong"]
    pb = dl[dl.modelo_comparado == "probit"].iloc[0]
    filas = [[NOMBRES[r.modelo_comparado], f(r.auc_b), f(r.diferencia), f"[{f(r.ic95_inferior)}; {f(r.ic95_superior)}]",
              f(r.z, 2), "< 0.001" if r.p_valor < 0.001 else f(r.p_valor, 3)] for r in dl.itertuples()]
    p(f"La prueba de DeLong compara el AUC-ROC de XGBoost ({f(m['auc_roc'])}) con el de cada modelo sobre los "
      f"mismos {miles(m['hogares'])} hogares de 2024 (Tabla {T()}). Frente al probit, el mejor modelo de "
      f"referencia, la diferencia es {f(pb.diferencia)} (IC 95 %: {f(pb.ic95_inferior)} a {f(pb.ic95_superior)}; "
      f"z = {f(pb.z,2)}; p < 0.001). En todas las comparaciones se rechaza la hipótesis nula de igualdad de AUC.")
    tabla("Prueba de DeLong: AUC-ROC de XGBoost frente a cada modelo en la ENAHO 2024",
          ["Modelo comparado", "AUC", "Diferencia", "IC 95 %", "z", "p"], filas,
          [3.0, 1.4, 1.9, 3.1, 1.3, 1.7], {1, 2, 4, 5},
          f"AUC de XGBoost: {f(m['auc_roc'])}. Diferencia = AUC de XGBoost − AUC del modelo comparado. " + FUENTE)
    p("Con estos resultados se acepta la hipótesis específica 3: XGBoost tiene un rendimiento superior al de "
      "los modelos de referencia fuera de muestra. La diferencia con los modelos econométricos es pequeña en "
      "magnitud, lo que indica que gran parte de la capacidad predictiva proviene de las variables elegidas y "
      "no solo del algoritmo.")

    h(4, "Errores de focalización")
    cf = R["confusion"].set_index("Celda")
    vp, fn = cf.loc["Verdadero positivo"], cf.loc["Falso negativo (exclusión)"]
    fp, vn = cf.loc["Falso positivo (filtración)"], cf.loc["Verdadero negativo"]
    p(f"Con el umbral de {R['umbral']}, el modelo identifica correctamente a {miles(vp.Hogares)} hogares pobres y "
      f"deja fuera a {miles(fn.Hogares)} (error de exclusión), que representan "
      f"{f(fn['Personas expandidas']/1e6,1)} millones de personas (Figura {F()}). A cambio, señala como pobres a "
      f"{miles(fp.Hogares)} hogares que no lo son (filtración). El umbral se eligió para no dejar fuera a los "
      "hogares pobres; subirlo reduciría la filtración a costa de más exclusión.")
    figura("Matriz de confusión de XGBoost en la ENAHO 2024", FIG / "fig_matriz_confusion.png", 8.5,
           "Valores en hogares de la muestra. " + FUENTE)

    h(4, "Curvas de discriminación y calibración")
    p(f"La curva ROC se aleja claramente de la diagonal del azar y la curva de precisión y exhaustividad se "
      f"mantiene muy por encima de la proporción de hogares pobres en la muestra (Figura {F()}).")
    figura("Curvas ROC y de precisión-exhaustividad de XGBoost en la ENAHO 2024",
           FIG / "fig_curvas_roc_pr.png", 12.4, FUENTE)
    p(f"Las probabilidades están calibradas: en los diez grupos de hogares ordenados por probabilidad, la "
      f"proporción observada de pobres sigue de cerca a la probabilidad predicha (Figura {F()}). Por eso el "
      f"promedio de las probabilidades estima bien la incidencia: {f(m['tasa_predicha'],2)} % frente a "
      f"{f(m['tasa_real'],2)} % observada en 2024. Si en lugar del promedio se contara a los hogares que superan "
      f"el umbral, la pobreza se sobreestimaría ({f(m['tasa_clasificados'],2)} %), porque el umbral prioriza no "
      "excluir a los pobres.")
    figura("Calibración de las probabilidades de XGBoost en la ENAHO 2024", FIG / "fig_calibracion.png", 9.5, FUENTE)

    h(4, "Pobreza estimada por departamento")
    sr = R["sesgo_res"]; sg = R["sesgo"]
    mx = sg.loc[sg.sesgo_pp.abs().idxmax()]
    p(f"Al promediar las probabilidades por departamento, la pobreza estimada se aleja de la observada "
      f"{f(sr['error_absoluto_medio_pp'],1)} puntos porcentuales en promedio, con un máximo de "
      f"{f(abs(mx.sesgo_pp),1)} puntos en {mx.departamento}; la correlación entre ambas es "
      f"{f(sr['correlacion_observada_predicha'],3)} (Figura {F()}). El modelo ordena bien a los departamentos: "
      f"estima como los más pobres a {lista(list(sg.nlargest(3, 'tasa_predicha').departamento))} y, como los "
      f"menos pobres, a {lista(list(sg.nsmallest(3, 'tasa_predicha').departamento))}; en la pobreza observada "
      f"los más pobres son {lista(list(sg.nlargest(3, 'tasa_observada').departamento))}, y los menos pobres, "
      f"{lista(list(sg.nsmallest(3, 'tasa_observada').departamento))}. Los mayores errores por exceso se dan en "
      f"{lista(list(sg.nlargest(3, 'sesgo_pp').departamento))}, y por defecto en "
      f"{lista(list(sg.nsmallest(3, 'sesgo_pp').departamento))}.")
    figura("Pobreza monetaria observada y estimada por el modelo por departamento, ENAHO 2024",
           FIG / "fig_sesgo_regional.png", 12.0,
           "Estimada: promedio de las probabilidades calibradas ponderado por FACTOR07 × MIEPERHO. " + FUENTE)

    h(4, "Desempeño por área y dominio geográfico")
    pa = R["por_area"]
    ru = pa[pa.grupo == "Rural"].iloc[0]; ur = pa[pa.grupo == "Urbana"].iloc[0]
    lm = pa[pa.grupo == "Lima Metropolitana"].iloc[0]
    sc = pa[pa.grupo == "Sierra Centro"].iloc[0]; ss = pa[pa.grupo == "Sierra Sur"].iloc[0]
    p(f"El modelo discrimina mejor en el área urbana (AUC-ROC {f(ur.auc,3)}) que en la rural ({f(ru.auc,3)}), "
      f"donde los hogares son más parecidos entre sí en vivienda y servicios (Tabla {T()}). En el área rural "
      f"identifica a más pobres (exhaustividad {f(ru.recall,3)}) pero sobreestima la incidencia "
      f"({f(ru.estim,1)} % frente a {f(ru.real,1)} %); en el área urbana la estimación queda cerca de la observada "
      f"({f(ur.estim,1)} % frente a {f(ur.real,1)} %). Por dominio, la sierra centro y la sierra sur se "
      f"sobreestiman en {f(sc.estim-sc.real,1)} y {f(ss.estim-ss.real,1)} puntos, y Lima Metropolitana se "
      f"subestima en {f(lm.real-lm.estim,1)} puntos.")
    filas = [[r.grupo, miles(r.hogares), f(r.auc, 3), f(r.recall, 3), f(r.prec, 3), f(r.real, 1), f(r.estim, 1)]
             for r in pa.itertuples()]
    tabla("Desempeño de XGBoost por área de residencia y dominio geográfico, ENAHO 2024",
          ["Área o dominio", "Hogares", "AUC-ROC", "Exh.", "Prec.", "Observada (%)", "Estimada (%)"],
          filas, [3.0, 1.6, 1.6, 1.3, 1.3, 1.8, 1.8], {1, 2, 3, 4, 5, 6},
          ABREV + "Pobreza observada y estimada: en personas, ponderada por FACTOR07 × MIEPERHO. " + FUENTE)
    p("Estas diferencias tienen una explicación económica: la línea de pobreza varía por dominio según el costo de "
      "vida, de modo que una misma vivienda o un mismo nivel educativo se asocia con un gasto distinto en Lima que en "
      "la sierra. El modelo aprende estas diferencias a través de las variables de territorio, pero no del todo; por "
      "eso conviene leer las estimaciones de cada dominio junto con su error.")

    h(4, "Sensibilidad al alquiler estimado")
    sn = R["sensibilidad"]; sa = sn[sn.estimador.str.endswith("alquiler")].iloc[0]
    p(f"El alquiler estimado (P106) es la variable más importante y podría estar ligado al gasto con que se "
      f"mide la pobreza. Sin ella, el AUC-ROC baja de {f(m['auc_roc'])} a {f(sa.auc_roc)} y el AUC-PR de "
      f"{f(m['auc_pr'])} a {f(sa.auc_pr)} (Tabla {T()}). El modelo pierde algo de precisión, pero su desempeño "
      "no depende de esa variable.")
    filas = [[NOMBRES[r.estimador], f(r.auc_roc), f(r.auc_pr), f(r.recall), f(r.precision), f(r.tasa_predicha, 2)]
             for r in sn.itertuples()]
    tabla("Sensibilidad del desempeño al excluir el alquiler estimado (P106), ENAHO 2024",
          ["Modelo", "AUC-ROC", "AUC-PR", "Exh.", "Prec.", "Pobreza estimada (%)"], filas,
          [3.2, 1.7, 1.7, 1.6, 1.6, 2.6], {1, 2, 3, 4, 5}, ABREV + FUENTE)

    h(4, "Web de resultados")
    p(f"Los resultados se publicaron en una web desarrollada con Angular (Figura {F()}), que muestra la "
      "pobreza por año y por departamento, el desempeño del modelo, la importancia de las variables y el "
      "método. La web lee los datos que genera el mismo procedimiento, de modo que se actualiza al volver a "
      "ejecutarlo.")
    figura("Página de pobreza por departamento de la web de resultados", ctx["ruta_web"], 12.4)

    E.extend(cierre.discusion(R))
    return E
