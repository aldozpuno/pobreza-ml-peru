# Decisiones metodológicas

Este documento justifica las decisiones que el código toma, en el orden del pipeline.
Puede adaptarse directamente al capítulo III de la tesis.

## 1. Fuente y unidad de análisis

Microdatos de la ENAHO 2017–2024 (INEI), metodología actualizada. La unidad de análisis
es el hogar. Se usan la Sumaria (módulo 34) y los módulos 01 (vivienda), 02 (miembros),
03 (educación), 04 (salud), 05 (empleo) y 37 (programas sociales). La Sumaria es la tabla
base: solo entran los hogares con encuesta completa y clasificación de pobreza.

## 2. Estructura de los datos: corte transversal agrupado

Los años se apilan (corte transversal agrupado). Como la ENAHO vuelve a entrevistar a una
parte de su muestra, un hogar puede aparecer en más de un año. Se identifica por dos vías:
la pregunta PANEL del módulo 100 ("¿El hogar fue entrevistado el año pasado?") y la llave
CONGLOME-VIVIENDA-HOGAR en años anteriores. La base reporta cuántos hogares marca cada
criterio y cuántos marcan ambos (`resumen_panel.csv`). La prueba final se evalúa con
todos los hogares de 2024 y solo con los no vistos antes.

## 3. Medición de la pobreza

Variable objetivo: `pobre` = 1 si POBREZA (Sumaria) es 1 (pobre extremo) o 2 (pobre no
extremo). La incidencia se calcula como el INEI:

    Tasa = Σ (pobre × MIEPERHO × FACTOR07) / Σ (MIEPERHO × FACTOR07)

Antes de entrenar, el pipeline compara la tasa reproducida con la cifra oficial de cada
año y se detiene si la diferencia supera 0,3 puntos. También informa la tasa de hogares
(peso FACTOR07), que es menor porque los hogares pobres tienen más miembros.

## 4. Factor de expansión

La ENAHO tiene un diseño muestral probabilístico, estratificado y multietápico; cada
hogar representa a un número distinto de hogares (FACTOR07). Por eso:

- toda cifra poblacional (incidencia, mapas, tasa predicha) usa FACTOR07 × MIEPERHO;
- las métricas se reportan sin ponderar y ponderadas por FACTOR07;
- el entrenamiento no usa pesos por defecto (`entrenar_con_factor: false`): un modelo
  predictivo bien especificado estima la probabilidad condicional sin ellos
  (Solon, Haider y Wooldridge, 2015). Cambiar el parámetro permite comparar.

## 5. Variables predictoras y fuga de datos

Las variables están en `config/features.yaml`, cada una con su módulo, definición, teoría
y signo esperado. Se excluyen las que definen la pobreza o se calculan con el gasto o el
ingreso (gasto, ingreso, líneas de pobreza, estrato socioeconómico, perceptores) y el año,
que en la prueba toma un valor nunca visto. El alquiler estimado (P106) se mantiene, pero
se reporta un modelo sin él, porque el gasto del hogar puede incluir el alquiler imputado.

Empleo informal: la ENAHO 2024 no publica la variable OCUPINF. Para que la informalidad
signifique lo mismo en todos los años, se reconstruye con el criterio de la OIT:
empleador o independiente con negocio no registrado en la SUNAT (P510A1 = 3), asalariado
no afiliado a un sistema de pensiones (P558A5 = 5) y trabajador familiar no remunerado.
En 2017–2023 la regla coincide con OCUPINF en el 93,6–94,6 % de los ocupados. El pipeline
avisa si algún predictor queda constante o vacío en un año, que es como se detectó el caso.

Conexión a internet: se excluye por la misma razón de comparabilidad. Desde la ENAHO 2023 el
cuestionario añade las preguntas P114B1 a P114B3 (conexión fija, móvil pospago y móvil prepago)
y P1144 pasa a contar también el internet móvil: los hogares con conexión pasan de 55,2 % en
2022 a 89,6 % en 2023. Como la prueba final entrena con 2017–2022 y calibra y evalúa con
2023–2024, la variable significaría una cosa al entrenar y otra al probar. No puede homologarse,
porque antes de 2023 no se registra el tipo de conexión. Sin ella el AUC-ROC de la prueba no
baja; sí aumenta el error de la pobreza estimada por departamento (de 3,3 a 3,9 puntos) y la
sobreestimación en el área rural, que se informa como limitación.

Colinealidad exacta: la brecha educativa (años máximos menos promedio) y el índice de
privación (suma de seis privaciones que ya entran por separado) son combinaciones lineales de
otras variables y se desactivaron en `features.yaml`. Con ellas fuera, el VIF máximo es menor
que 10.

Correcciones respecto del código anterior: el hacinamiento divide entre P104
(habitaciones), no P103 (material del piso); el piso de tierra es P103 = 6 y la pared
precaria se toma de P102 (material de paredes), no de P101 (tipo de vivienda).

## 6. Validación temporal y prueba

Ventana expansiva: cada pliegue entrena con los años anteriores, calibra con un año y
evalúa con el siguiente (2020 a 2023). La prueba final entrena con 2017–2022, calibra con
2023 y evalúa con 2024, que no se usa para ninguna decisión.

## 7. Calibración y umbral

Las probabilidades se calibran con regresión isotónica en el año de calibración. El umbral
de decisión se elige en ese mismo año (por defecto, el que maximiza el F1); nunca en la
prueba. El error de exclusión (pobres clasificados como no pobres) se informa siempre,
porque es el costo principal en focalización.

Tasa estimada frente a hogares clasificados. Para estimar la incidencia de un territorio
se promedian las probabilidades calibradas, ponderadas por FACTOR07 × MIEPERHO. Contar
los hogares que superan el umbral sobreestima la pobreza, porque el umbral del F1 prioriza
no excluir a hogares pobres: en 2024 el promedio de probabilidades da 28,0 % (INEI 27,6 %)
y los hogares sobre el umbral representan el 40,1 % de la población. El umbral sirve para
focalizar (a quién atender); el promedio, para medir (cuántos son pobres).

## 8. Prueba de hipótesis

La ventaja del modelo principal se contrasta con la prueba de DeLong para curvas ROC
correlacionadas (DeLong et al., 1988): todos los modelos se evalúan sobre los mismos hogares
de 2024, así que la varianza de la diferencia de AUC considera la covarianza entre ambos.
`evaluation/inference.py` la implementa (versión rápida de Sun y Xu, 2014) y la etapa
`evaluar` escribe `prueba_delong.csv`.

## 9. Interpretación

Los valores SHAP se calculan sobre el margen del modelo (log-odds). Para cada variable se
compara el signo observado con el esperado según su teoría. Los programas sociales se
asocian a la pobreza porque se asignan a hogares pobres; no se interpretan como efecto
causal.
