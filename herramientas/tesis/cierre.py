"""Discusión, conclusiones y recomendaciones del Capítulo IV."""

from __future__ import annotations

import constructor as c
from datos import f


def discusion(R) -> list:
    E = []
    m = R["m"]
    pb = R["delong"][R["delong"].modelo_comparado == "probit"].iloc[0]
    sr = R["sesgo_res"]
    nv = R["prueba"][R["prueba"].Variante.str.startswith("Solo hogares no vistos")].iloc[0]
    ru = R["por_area"][R["por_area"].grupo == "Rural"].iloc[0]
    h = lambda n, t: E.append(c.titulo(n, t))
    h(2, "Discusión")
    E.append(c.parrafo(
        "Los resultados permiten discutir cuatro aspectos: la medición de la variable dependiente y la "
        "estructura de los datos, los determinantes que identifica el modelo, el desempeño frente a la "
        "econometría clásica y su uso para focalizar.", 2))
    E.append(c.parrafo(
        f"Sobre la medición y los datos, el estudio reprodujo la incidencia oficial del INEI con diferencias "
        f"de 0.05 puntos o menos, de modo que el modelo aprende la misma definición de pobreza que usa el Estado. "
        f"La base apilada contiene hogares que se repiten entre años ({R['pct_rep']} % de las observaciones); "
        f"al evaluar solo con hogares nunca vistos el AUC-ROC fue {f(nv.auc_roc,3)}, frente a {f(m['auc_roc'],3)} "
        "con todos los hogares, lo que descarta que el modelo acierte por memorizar hogares. Excluir las variables construidas "
        "con el gasto o el ingreso coincide con lo que hizo Dabús (2020) para Argentina: predecir la condición "
        "de pobreza con variables distintas al ingreso permite usar el modelo donde el ingreso no se observa.", 2))
    E.append(c.parrafo(
        "Sobre los determinantes, la descomposición SHAP indica que la pobreza se explica sobre todo por el "
        "valor de la vivienda, el tamaño del hogar, el hacinamiento, el territorio y la inserción laboral. En "
        f"{R['n_coincide']} de {R['n_signo']} variables el signo aprendido coincide con el de su teoría. El peso "
        "de la educación y la ocupación es coherente con el enfoque de capacidades de Sen (1995), y el del "
        "hacinamiento y el piso de tierra con el enfoque multidimensional de Alkire y Foster (2011). La "
        "importancia del territorio respalda la perspectiva estructuralista de Sosa Escudero (2023). La "
        "importancia de las variables casi no cambia entre 2017–2019 y 2021–2024, lo que indica que estos "
        "determinantes son estructurales y no un efecto pasajero de la pandemia.", 2))
    E.append(c.parrafo(
        f"Sobre el desempeño, XGBoost superó a todos los modelos de referencia y la diferencia fue significativa "
        f"en la prueba de DeLong, como encontraron Galvis Caballero (2021) y Santolin y Oliveira (2023) con "
        f"aprendizaje automático en encuestas de hogares. Sin embargo, la ventaja sobre el probit fue de "
        f"{f(pb.diferencia,3)} en AUC-ROC, menor que la que reportan algunos estudios; esto sugiere que, con "
        "variables bien elegidas, los modelos econométricos ya capturan buena parte de la señal y que la "
        "contribución del aprendizaje automático está en las interacciones y en la calidad de las "
        "probabilidades. La caída de la exhaustividad en 2020 es consistente con la distinción entre pobreza "
        "crónica y transitoria de Cantó et al. (2012): los nuevos pobres de la pandemia perdieron ingresos sin "
        "cambiar todavía sus activos.", 2))
    E.append(c.parrafo(
        f"Sobre la focalización, el modelo identifica al {f(100*m['recall'],1)} % de los hogares pobres, con una "
        f"precisión de {f(m['precision'],3)}. Como señalan Solís-Salazar y Madrigal-Sanabria (2022), el umbral "
        "fija el equilibrio entre exclusión y filtración y debe elegirse según el costo de cada error para el "
        "programa. Para estimar la pobreza de un territorio no debe contarse a los hogares sobre el umbral sino "
        "promediarse las probabilidades calibradas: así el error medio por departamento fue "
        f"{f(sr['error_absoluto_medio_pp'],1)} puntos. Esto coincide con la recomendación de Sosa Escudero y "
        "Cornejo (2022) de combinar información micro y territorial. Una limitación es que la calibración depende "
        "de que el año de calibración se parezca al de aplicación: ante un choque como el de 2020 la incidencia "
        "estimada se subestima, por lo que el modelo debe recalibrarse con información reciente.", 2))
    E.append(c.parrafo(
        "Los resultados también dialogan con los antecedentes nacionales. Castillo y Guillén (2025) encontraron que "
        "la regresión logística y el bosque aleatorio daban las mejores predicciones de la pobreza fuera de muestra "
        "con la ENAHO; en esta tesis la regresión logística quedó muy cerca de XGBoost, lo que refuerza que un "
        "modelo lineal bien especificado es una referencia exigente. Sikov y Cerda-Hernández (2024) estimaron que la "
        "pobreza urbana llegó a 26.4 % en 2023; la serie de esta tesis reproduce esa cifra (26.4 % en 2023) y "
        "muestra que la brecha entre campo y ciudad se redujo por el aumento de la pobreza urbana. Arias y Sucari "
        "(2019) y Quispe Mamani et al. (2021) destacan la educación, el saneamiento y la vivienda como factores "
        "asociados a la reducción de la pobreza; esas mismas dimensiones aparecen entre los determinantes del "
        "modelo.", 2))
    E.append(c.parrafo(
        "Frente a los antecedentes internacionales, el resultado coincide con Solís-Salazar y Madrigal-Sanabria "
        "(2022) y con Galvis Caballero (2021), que también encontraron en XGBoost el mejor clasificador. En cambio, "
        "Hassan et al. (2024) y Ochoa Guaraca et al. (2021) obtuvieron su mejor desempeño con el bosque aleatorio. "
        "En esta tesis el bosque aleatorio quedó por debajo de los modelos lineales; una explicación posible es que "
        "en esta base buena parte de la relación entre las variables y la pobreza es cercana a lineal, lo que "
        "favorece a los modelos lineales y al boosting frente al bosque aleatorio. La diferencia confirma que el "
        "mejor algoritmo depende de los datos y que la comparación debe hacerse con un mismo esquema de validación.", 2))
    E.append(c.parrafo(
        "La investigación tiene limitaciones. Primero, la ENAHO es una encuesta y las tasas departamentales anuales "
        "tienen error muestral, por lo que parte de la diferencia entre la pobreza estimada y la observada se debe "
        "a la muestra y no al modelo. Segundo, el alquiler estimado puede estar ligado al gasto del hogar; por eso se "
        "presentó un modelo sin esa variable. Tercero, los valores SHAP describen asociaciones que el modelo usa para "
        "predecir y no efectos causales, en particular en los programas sociales. Cuarto, los cambios de "
        "cuestionario limitan las variables que pueden usarse: la conexión a internet se excluyó porque desde 2023 "
        "incluye el internet móvil y dejó de ser comparable con los años de entrenamiento. Quinto, el modelo "
        f"sobreestima la pobreza del área rural ({f(ru.estim,1)} % frente a {f(ru.real,1)} % observada), por lo que "
        "las estimaciones territoriales deben leerse junto con su error. Por último, el modelo predice la "
        "condición de pobreza de un año con las características del mismo año; anticipar la pobreza futura de un "
        "hogar requeriría un diseño de panel.", 2))
    return E


def conclusiones(R) -> list:
    m = R["m"]; dl = R["delong"]; pb = dl[dl.modelo_comparado == "probit"].iloc[0]
    sr = R["sesgo_res"]
    nv = R["prueba"][R["prueba"].Variante.str.startswith("Solo hogares no vistos")].iloc[0]
    xg = R["pliegues_m"][R["pliegues_m"].estimador == "xgboost"]
    return [
        c.conclusion("PRIMERO",
            f"Se desarrolló y validó un modelo predictivo de la pobreza monetaria basado en XGBoost que, evaluado "
            f"con la ENAHO 2024 sin haberla usado antes, alcanzó un AUC-ROC de {f(m['auc_roc'])} y un AUC-PR de "
            f"{f(m['auc_pr'])}, y superó de forma estadísticamente significativa a los modelos econométricos y de "
            f"aprendizaje automático de referencia (prueba de DeLong, p < 0.001). Con ello se acepta la hipótesis "
            f"general. El promedio de sus probabilidades estimó una pobreza de {f(m['tasa_predicha'],1)} % frente a "
            f"{f(m['tasa_real'],1)} % observada."),
        c.conclusion("SEGUNDO",
            f"Las variables relevantes para predecir la pobreza son características observables del hogar: el "
            f"valor de la vivienda, el tamaño y la composición del hogar, el hacinamiento, la "
            f"ocupación, la educación y el territorio. De las variables con signo esperado, {R['n_coincide']} de "
            f"{R['n_signo']} se comportan como predice su teoría. La variable dependiente reprodujo la cifra oficial "
            f"del INEI con diferencias de 0.05 puntos o menos, y la exclusión de las variables con fuga de datos, "
            f"colinealidad exacta o definición no comparable entre años dejó un conjunto de {R['n_vars']} "
            f"predictores con VIF menor que 10."),
        c.conclusion("TERCERO",
            f"El entrenamiento con validación temporal, calibración isotónica y umbral elegido fuera de la prueba "
            f"produjo un modelo estable: su AUC-ROC se mantuvo entre {f(xg.auc_roc.min(),3)} y "
            f"{f(xg.auc_roc.max(),3)} en los años evaluados, incluido "
            f"2020. Los hogares que se repiten entre años no inflan el resultado, porque con hogares nunca vistos el "
            f"AUC-ROC fue {f(nv.auc_roc)}. La ventaja de XGBoost sobre el probit fue de {f(pb.diferencia,3)}, "
            f"significativa pero pequeña."),
        c.conclusion("CUARTO",
            f"En la evaluación de precisión, sesgo y sensibilidad, el modelo identifica al {f(100*m['recall'],1)} % "
            f"de los hogares pobres con una precisión de {f(m['precision'],3)}, y estima la pobreza por departamento "
            f"con un error medio de {f(sr['error_absoluto_medio_pp'],1)} puntos porcentuales (correlación "
            f"{f(sr['correlacion_observada_predicha'],3)}). Sin el alquiler estimado, el AUC-ROC baja a "
            f"{f(R['sensibilidad'].auc_roc.iloc[1])}, por lo que el desempeño no depende de esa variable."),
    ]


def recomendaciones() -> list:
    return [
        c.conclusion("PRIMERO",
            "Al Ministerio de Desarrollo e Inclusión Social (MIDIS) se recomienda evaluar el modelo como "
            "herramienta complementaria del Sistema de Focalización de Hogares para priorizar la actualización de "
            "la clasificación socioeconómica de los hogares con mayor probabilidad de pobreza, eligiendo el umbral "
            "según el costo de exclusión y filtración de cada programa."),
        c.conclusion("SEGUNDO",
            "A los gobiernos regionales y locales, en especial al Gobierno Regional de Puno, se recomienda usar la "
            "pobreza estimada por departamento y los determinantes identificados (vivienda, hacinamiento, "
            "educación y empleo) para priorizar las inversiones que cierran brechas en los hogares "
            "de mayor riesgo, en concordancia con Quispe Mamani et al. (2021) y Pilco Bonifacio (2023)."),
        c.conclusion("TERCERO",
            "Al Instituto Nacional de Estadística e Informática (INEI) y a la comunidad académica se recomienda "
            "evaluar los modelos de predicción de la pobreza con validación temporal, informar si los hogares se "
            "repiten entre años, medir las cifras poblacionales con el factor de expansión y verificar que las "
            "variables signifiquen lo mismo en todos los años, porque los cambios de cuestionario, como el de la "
            "conexión a internet en 2023, afectan su comparabilidad."),
        c.conclusion("CUARTO",
            "A futuras investigaciones se recomienda recalibrar el modelo cada año con la encuesta más reciente, "
            "incorporar registros administrativos e información geoespacial y estudiar la pobreza transitoria, que "
            "el modelo detecta con menor precisión en años de choque como 2020."),
    ]
