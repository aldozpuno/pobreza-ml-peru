"""Contenido del Capítulo III (desde 3.3 Muestra hasta el final del capítulo)."""

from __future__ import annotations

import constructor as c
from datos import f

# Texto de 3.4 tal como figuraba en el borrador del autor (versión «correccion1 – formato EPG»).
METODO = [
    "Esta investigación adopta un enfoque analítico, basado en el examen sistemático de datos cuantitativos y "
    "su análisis, con el objetivo de identificar patrones y relaciones entre variables clave que permitan "
    "desarrollar un modelo predictivo para la pobreza monetaria en el Perú (Hernández Sampieri et al., 1991).",
    "Utilizando un enfoque cuantitativo, se recopilaron datos numéricos y se aplicaron métodos estadísticos "
    "avanzados para analizar la relación entre las variables y predecir escenarios futuros con el apoyo de "
    "técnicas de Machine Learning (Del Canto y Silva Silva, 2013). Este enfoque permite identificar patrones "
    "complejos y realizar predicciones precisas en diferentes contextos socioeconómicos, tal como lo destacan "
    "James et al. (2021) en su obra, donde explican el papel fundamental del aprendizaje automático y los "
    "métodos estadísticos en la toma de decisiones basada en datos.",
    "La investigación es de propósito aplicado y de alcance explicativo y predictivo. El diseño metodológico es "
    "no experimental, ya que no se manipulan las variables, y longitudinal de cortes transversales agrupados "
    "(*pooled cross-section*). Se trabajó con datos de fuente secundaria, los microdatos de la ENAHO 2017–2024 "
    "del INEI, mediante la técnica de análisis documental y con una ficha de registro de datos como "
    "instrumento. Estos datos fueron procesados y analizados mediante técnicas de aprendizaje automático para "
    "construir y evaluar el modelo predictivo.",
]


def construir(doc, R, ctx) -> list:
    """R: resultados del pipeline; ctx: elementos reutilizados del borrador original."""
    E = []
    add = E.extend
    p = lambda t, n=2: E.append(c.parrafo(t, n))
    h = lambda n, t: E.append(c.titulo(n, t))

    h(2, "Muestra")
    p(f"La muestra está formada por los microdatos de la ENAHO de 2017 a 2024, organizados como un "
      f"corte transversal agrupado (*pooled cross-section*). Contiene {R['obs']} observaciones hogar-año "
      f"(entre {R['hog_min']} y {R['hog_max']} hogares por año), que corresponden a {R['distintos']} hogares "
      f"distintos según su llave CONGLOME–VIVIENDA–HOGAR. Solo se incluyen los hogares con encuesta completa "
      f"y clasificación de pobreza en la Sumaria. El muestreo de la ENAHO es probabilístico, estratificado y "
      f"multietápico, y cada hogar representa a un número distinto de hogares de la población según su "
      f"factor de expansión (FACTOR07).")

    h(2, "Método de investigación")
    if ctx["metodo"]:
        for el in ctx["metodo"]:
            E.append(el)
    else:  # el borrador perdió estos párrafos en una pasada anterior: se restituyen
        for texto in METODO:
            p(texto)

    h(2, "Descripción detallada de métodos por objetivos específicos")
    p("Objetivo específico 1. Para identificar las variables relevantes se revisó la literatura sobre los "
      "determinantes de la pobreza y se asoció cada variable candidata a una teoría y a un signo esperado. "
      "Con los módulos 01, 02, 03, 04, 05, 34 y 37 de la ENAHO se construyó una base con un registro por "
      "hogar y año. Antes de modelar se reprodujo la incidencia oficial de la pobreza, se identificaron los "
      "hogares entrevistados en más de un año y se excluyeron las variables con fuga de datos, con "
      "colinealidad exacta o que no son comparables entre años.")
    p("Objetivo específico 2. Se entrenaron cinco algoritmos con los mismos datos: XGBoost como modelo "
      "principal y, como referencia, bosque aleatorio, regresión logística, regresión probit y k vecinos más "
      "cercanos (KNN). El ajuste siguió una validación temporal con ventana expansiva: cada modelo aprende "
      "con los años anteriores, calibra sus probabilidades y elige su umbral con el año siguiente y se evalúa "
      "con el año posterior. Los valores SHAP permitieron contrastar el efecto aprendido de cada variable "
      "con el que predice su teoría.")
    p("Objetivo específico 3. El modelo final se evaluó una sola vez con la ENAHO 2024, que no intervino en "
      "ninguna decisión. Se calcularon las métricas de discriminación (AUC-ROC, AUC-PR), de clasificación "
      "(exhaustividad, precisión, F1) y de calibración (Brier); se contrastó con la prueba de DeLong si la "
      "ventaja de XGBoost sobre los demás modelos es estadísticamente significativa; y se midió el error de "
      "la pobreza estimada por departamento.")

    h(2, "Procesamiento de datos")
    p("El procesamiento se programó en Python como una secuencia de etapas reproducibles; cada etapa lee la "
      "salida de la anterior y los parámetros (años, módulos, variables e hiperparámetros) se declaran en "
      "archivos de configuración, no en el código. Las etapas son:")
    add(c.vinetas([
        "Descarga de los módulos de la ENAHO 2017–2024 desde el portal de microdatos del INEI.",
        "Lectura y homologación de nombres de columnas y de las llaves CONGLOME, VIVIENDA y HOGAR.",
        "Procesamiento de cada módulo hasta un registro por hogar (los módulos de personas se agregan por hogar).",
        "Unión de los módulos a la Sumaria, que es la tabla base, de modo que ningún hogar se pierde por falta de un módulo.",
        "Apilamiento de los años e identificación de los hogares entrevistados en más de un año.",
        "Construcción de variables derivadas y verificación de que ningún predictor quede constante o vacío en algún año.",
        "Medición de la pobreza y comparación con la cifra oficial antes de entrenar los modelos.",
    ]))
    h(3, "Arquitectura de la base de datos")
    add(c._rotulo("Figura", ctx["fig"](), "Integración de los módulos de la ENAHO en una base con un registro por hogar", 3))
    E.append(ctx["img_arquitectura"])
    p("Los módulos de personas (educación, salud, empleo y miembros) se resumen primero por hogar; luego se "
      "unen a la Sumaria junto con la vivienda y los programas sociales mediante la llave año, CONGLOME, "
      "VIVIENDA y HOGAR. Así cada observación conserva su identificador y puede seguirse entre años.", 3)

    h(3, "Hogares entrevistados en más de un año")
    p("Al apilar los años un mismo hogar puede aparecer más de una vez, porque la ENAHO vuelve a entrevistar "
      "a una parte de su muestra. Un hogar se considera repetido si responde que fue entrevistado el año "
      "anterior (variable PANEL del módulo 100) o si su llave CONGLOME–VIVIENDA–HOGAR ya figura en un año "
      "anterior de la base. La base se trata como un corte transversal agrupado y no como un panel, porque "
      "el objetivo es predecir la condición de pobreza de un hogar a partir de sus características del mismo "
      "año. Para descartar que el modelo acierte por haber visto antes al hogar, la prueba final se evalúa "
      "con todos los hogares y, por separado, solo con los hogares nunca vistos.", 3)

    h(2, "Medición de la pobreza monetaria")
    p("La variable dependiente se construye con la variable POBREZA de la Sumaria, que el INEI calcula "
      "comparando el gasto per cápita del hogar con la línea de pobreza:")
    E.append(c.ecuacion_pobreza())
    p("donde *Y*ᵢ = 1 si el hogar es pobre extremo o pobre no extremo (POBREZA = 1 o 2) y *Y*ᵢ = 0 en otro "
      "caso. La incidencia de la pobreza se calcula como lo hace el INEI, en personas:")
    E.append(c.ecuacion_incidencia())
    p("donde MIEPERHO es el número de miembros del hogar y FACTOR07 el factor de expansión del hogar.")
    p("Antes de entrenar, el procedimiento compara la tasa reproducida con la cifra oficial de cada año y se "
      "detiene si la diferencia supera 0.3 puntos porcentuales. También se informa la tasa de hogares "
      "(ponderada solo por FACTOR07), que es menor porque los hogares pobres tienen más miembros.")

    h(2, "Uso del factor de expansión")
    p("La ENAHO tiene un diseño muestral complejo y cada hogar representa a un número distinto de hogares. "
      "Por eso el factor de expansión se usa según el propósito de cada cálculo:")
    add(c.vinetas([
        "Toda cifra poblacional (incidencia, pobreza por departamento y pobreza estimada por el modelo) se pondera por FACTOR07 × MIEPERHO.",
        "Las métricas del modelo se informan sin ponderar y ponderadas por FACTOR07, para verificar que el desempeño en la muestra representa al de la población.",
        "El entrenamiento no usa pesos: un modelo predictivo bien especificado estima la probabilidad condicional de ser pobre sin ellos, y ponderar solo aumenta la varianza (Solon et al., 2015). El uso de pesos es un parámetro que puede activarse para comparar.",
    ]))

    h(2, "Variables predictoras")
    p(f"Cada variable predictora está documentada en un catálogo con su módulo de origen, su definición, la "
      f"teoría de la pobreza que la justifica y el signo esperado de su efecto. El modelo final usa "
      f"{R['n_vars']} variables agrupadas en territorio, composición del hogar, capital humano, salud, empleo, "
      f"vivienda y servicios, y protección social. Entre las variables derivadas están el hacinamiento "
      f"(miembros por habitación), la razón de dependencia, la tasa de ocupación, la tasa de informalidad, "
      f"los años de estudio promedio y máximos del hogar y la indicadora del año de la COVID-19.")
    p("Se excluyen las variables que definen la pobreza o se calculan con el gasto o el ingreso (gasto, "
      "ingreso, líneas de pobreza, estrato socioeconómico y número de perceptores), porque con ellas el "
      "modelo acertaría sin aprender nada útil (fuga de datos). También se excluyen las variables que son "
      "combinación lineal exacta de otras: la brecha educativa (años máximos menos promedio) y el índice de "
      "privación (suma de seis privaciones que ya entran por separado). El alquiler estimado de la vivienda "
      "(P106) se mantiene, pero se informa un modelo sin él, porque el gasto del hogar puede incluir el "
      "alquiler imputado.")
    p("La ENAHO 2024 no publica la variable de empleo informal (OCUPINF). Para que la informalidad signifique "
      "lo mismo en todos los años se reconstruye con el criterio de la Organización Internacional del Trabajo: "
      "empleador o independiente con negocio no registrado en la SUNAT, asalariado no afiliado a un sistema de "
      f"pensiones y trabajador familiar no remunerado. En 2017–2023 esta regla coincide con OCUPINF en el "
      f"{R['ocupinf']} de los ocupados, según el año.")
    ia = R["internet_anual"]
    p("Con el mismo criterio de comparabilidad se excluye la conexión a internet del hogar (P1144). Desde la "
      "ENAHO 2023 el cuestionario pregunta además por el tipo de conexión (P114B1 a P114B3: fija, móvil "
      "pospago y móvil prepago), de modo que P1144 pasó a contar también el internet móvil: los hogares con "
      f"conexión pasaron de {f(ia[2022],1)} % en 2022 a {f(ia[2023],1)} % en 2023. Como el modelo final se "
      "entrena con 2017–2022 y se calibra y evalúa con 2023 y 2024, la variable significaría una cosa en el "
      "entrenamiento y otra en la prueba. No es posible homologarla, porque antes de 2023 no se registra el "
      "tipo de conexión, y por eso no entra al modelo.")

    h(2, "Validación temporal del modelo")
    p("Como los datos tienen orden cronológico, no se usó la validación cruzada aleatoria, que mezcla años "
      "y deja entrar información del futuro. Se aplicó una validación con ventana expansiva (*walk-forward*): "
      "en cada pliegue el modelo entrena con los años anteriores, calibra sus probabilidades y elige el "
      "umbral con el año siguiente, y se evalúa con el año posterior (Tabla "
      f"{ctx['tab_siguiente']}).")
    filas = [[f["nombre"], f["entrena"], str(f["calibra"]), str(f["evalua"])] for f in R["pliegues"]]
    add(c.bloque_tabla(ctx["tab"](), "Diseño de la validación temporal con ventana expansiva, ENAHO 2017–2024",
                       ["Pliegue", "Entrenamiento", "Calibración y umbral", "Evaluación"], filas,
                       [3.5, 4, 4, 3.5], 2, {2, 3}))
    p("La prueba final entrena con 2017–2022, calibra con 2023 y evalúa con 2024. El año de prueba no se usa "
      "para elegir variables, hiperparámetros ni umbrales.")

    h(2, "Calibración de probabilidades y umbral de decisión")
    p("Las probabilidades de cada modelo se calibran con regresión isotónica en el año de calibración, de modo "
      "que una probabilidad de 0.3 corresponda a cerca de 30 % de hogares pobres. El umbral de decisión se "
      "elige en ese mismo año, como el que maximiza el F1, y nunca en la prueba. Las probabilidades calibradas "
      "cumplen dos usos distintos: su promedio, ponderado por FACTOR07 × MIEPERHO, estima la incidencia de "
      "un territorio; y el umbral clasifica a cada hogar para la focalización.")

    h(2, "Métricas de evaluación")
    p("El desempeño se evaluó con métricas para clasificación binaria con clases desbalanceadas (Tabla "
      f"{ctx['tab_siguiente']}).")
    add(c.bloque_tabla(ctx["tab"](), "Métricas de evaluación de los modelos predictivos",
                       ["Métrica", "Qué mide"], [
                           ["AUC-ROC", "Capacidad de ordenar a un hogar pobre por encima de uno no pobre (0.5 = azar; 1 = perfecto)"],
                           ["AUC-PR", "Precisión media a lo largo de la exhaustividad; más exigente cuando los pobres son minoría"],
                           ["Exhaustividad (recall)", "Proporción de hogares pobres que el modelo identifica; su complemento es el error de exclusión"],
                           ["Precisión", "Proporción de hogares señalados como pobres que lo son; su complemento es la filtración"],
                           ["F1", "Media armónica de precisión y exhaustividad"],
                           ["Brier", "Error cuadrático medio de la probabilidad; mide la calibración (menor es mejor)"],
                       ], [3.6, 11.4], 2))
    p("En la focalización de programas sociales el error de exclusión (hogares pobres clasificados como no "
      "pobres) es el costo principal, por eso la exhaustividad se informa siempre junto con la precisión.")

    h(2, "Prueba estadística inferencial")
    p("Para contrastar la hipótesis de que XGBoost supera a los modelos de referencia fuera de muestra se "
      "aplicó la prueba de DeLong para curvas ROC correlacionadas (DeLong et al., 1988). Como todos los "
      "modelos se evalúan sobre los mismos hogares de 2024, la prueba estima la varianza de la diferencia de "
      "AUC considerando la covarianza entre ambos. Las hipótesis son:")
    add(c.vinetas([
        "H₀: AUC(XGBoost) = AUC(modelo de referencia).",
        "H₁: AUC(XGBoost) ≠ AUC(modelo de referencia).",
    ]))
    p("Se rechaza H₀ si el valor p es menor que 0.05; además se informa el intervalo de confianza al 95 % de "
      "la diferencia.")

    h(2, "Interpretabilidad del modelo mediante valores SHAP")
    for el in ctx["shap"]:
        E.append(el)
    p("Para cada variable se compara el signo del efecto aprendido (correlación entre su valor y su valor "
      "SHAP) con el signo que predice su teoría. Además, el mismo modelo se explica con los hogares de "
      "2017–2019 y de 2021–2024 para ver cómo cambió la importancia de las variables con la pandemia.")

    h(2, "Modelos aplicados para el entrenamiento y validación")
    p("Se compararon cinco algoritmos de aprendizaje supervisado con los mismos datos, pliegues y calibración:")
    add(c.vinetas([
        "XGBoost (modelo principal): 400 árboles potenciados por gradiente, profundidad máxima 5, tasa de aprendizaje 0.05 y submuestreo de 80 % de hogares y variables.",
        "Bosque aleatorio: ensamble de árboles de decisión entrenados sobre muestras con reemplazo.",
        "Regresión logística y regresión probit: modelos econométricos de referencia para una variable dependiente binaria; las variables numéricas se estandarizan y las categóricas se codifican con variables indicadoras.",
        "k vecinos más cercanos (KNN): clasifica a cada hogar según la condición de los hogares más parecidos.",
    ]))
    p("La regresión por cuantiles, revisada en el marco teórico, no se usó como clasificador porque la "
      "variable dependiente es binaria; su lugar como referencia lineal lo ocupa la regresión logística.")

    h(2, "Técnicas de recolección de datos por objetivos específicos")
    add(c.vinetas([
        "Objetivo específico 1: revisión de literatura; descarga de los módulos de la ENAHO; construcción de la base por hogar; medición de la pobreza; identificación de hogares repetidos; diagnóstico de fuga de datos, colinealidad y comparabilidad entre años.",
        "Objetivo específico 2: entrenamiento de los cinco modelos con validación temporal; calibración isotónica; elección del umbral; cálculo de valores SHAP.",
        "Objetivo específico 3: evaluación en la ENAHO 2024; prueba de DeLong; matriz de confusión; error de la pobreza estimada por departamento; análisis de sensibilidad sin P106.",
    ]))

    h(2, "Materiales, equipos y software")
    p("Se usaron los microdatos oficiales de la ENAHO 2017–2024, la documentación metodológica del INEI y "
      "literatura especializada. El procesamiento se realizó en Python 3.14 con pandas y NumPy (datos), "
      "scikit-learn y XGBoost (modelos), SciPy (prueba de DeLong), SHAP (interpretabilidad) y Matplotlib "
      "(figuras). Los resultados se presentan además en una web desarrollada con Angular. El código, "
      "organizado por capas y con pruebas automáticas, se incluye en los anexos.")
    h(3, "Flujograma del proceso")
    add(c.bloque_figura(doc, ctx["fig"](), "Etapas del proceso de medición, modelamiento y evaluación",
                        ctx["ruta_flujo"], 15.0, 3))
    return E
