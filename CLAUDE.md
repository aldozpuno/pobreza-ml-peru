# Proyecto: modelo predictivo de pobreza monetaria en el Perú (ENAHO 2017–2024)

Tesis doctoral de Aldo Hernán Zanabria Gálvez (Doctorado en Economía y Políticas Públicas,
EPG UNA Puno). Este repositorio mide la pobreza como el INEI, entrena cinco modelos, evalúa
el modelo final con la ENAHO 2024 y produce las tablas, figuras, la web de resultados y las
correcciones del borrador de la tesis.

## Cómo trabajar aquí

- Responde y documenta en español. Nombres de funciones y variables también en español.
- Archivos cortos y con una sola responsabilidad (idealmente menos de 300 líneas, nunca más de 500).
- Los parámetros viven en `config/` (años, módulos, variables, hiperparámetros), no en el código.
- **No crear copias del borrador de la tesis** ("final 1", "final 2"…): se edita el original
  `D:\Proyecto Ing Aldo\BORRADOR DE TESIS FINAL.docx`. Los temporales van a una carpeta temporal.
- Antes de escribir una cifra en la tesis o en la web, sácala de `resultados/reportes/datos/`.
- Después de cambiar código: `pytest`. Después de cambiar la web: `npm run build` en `web/`.

## Comandos

```bash
pip install -r requirements-lock.txt && pip install -e ".[dev,tesis]" --no-deps   # una vez
pobreza todo                         # descargar → construir → medir → entrenar → evaluar → reportar
pobreza evaluar && pobreza reportar  # sin reentrenar
pytest                               # pruebas con datos sintéticos
python herramientas/tesis/figuras.py # Figura 1, flujograma y capturas de código para la tesis
python herramientas/tesis/capturas_web.py  # capturas completas de la web (necesita la web en :4500)
python herramientas/tesis/actualizar.py "D:/Proyecto Ing Aldo/BORRADOR DE TESIS FINAL.docx"
cd web && npm install && npm start   # web en http://localhost:4500
```

Comandos de Claude Code: `/reproducir`, `/actualizar-tesis` y `/web`, en `.claude/commands/`. Si esa carpeta
no existe, cópialos desde `claude-code/commands/` (las herramientas remotas no pueden escribir en `.claude`).

## Datos

- Microdatos: los 56 zip del INEI están en `D:\Proyecto Ing Aldo\datos-inei\enaho_{año}_modulo{NN}.zip`.
  El pipeline los espera en `datos/crudos/{año}/{modulo}.zip`, con módulo = `sumaria` (34),
  `vivienda` (01), `miembros` (02), `educacion` (03), `salud` (04), `empleo` (05), `programas` (37).
  Códigos INEI por año en `config/pipeline.yaml` (2017 = 603 … 2024 = 966).
- Base procesada: `datos/procesados/hogares.parquet` (277 136 observaciones hogar-año, 207 037 hogares).
- `datos/intermedios/hogares_{año}.parquet` es caché por año: bórralo si cambias un procesador.

## Arquitectura (detalle en docs/ARQUITECTURA.md)

`src/pobreza/`: `data` (catálogo, descarga, lectura) → `processing` (un módulo ENAHO por archivo;
`assemble.py` une y apila) → `measurement` (incidencia) → `features` (catálogo, derivadas, fuga,
VIF) → `modeling` (pliegues, estimadores, calibración, umbral) → `evaluation` (métricas, sesgo
regional, SHAP, prueba de DeLong) → `reporting` (figuras EPG, tablas .docx, JSON de la web).
`stages/` orquesta cada etapa y `cli.py` es la entrada. `web/` es Angular 19 y solo lee
`web/public/data/*.json`. `herramientas/tesis/` reescribe el borrador (ver su README).

## Decisiones que no se deben deshacer (detalle en docs/METODOLOGIA.md)

- Pobreza en personas: Σ(pobre × MIEPERHO × FACTOR07) / Σ(MIEPERHO × FACTOR07). La etapa `medir`
  se detiene si difiere del INEI en más de 0.3 pp. La tasa de hogares (solo FACTOR07) es menor.
- Hogares repetidos: pregunta PANEL del módulo 100 o llave CONGLOME-VIVIENDA-HOGAR en un año
  anterior. La prueba se informa con todos los hogares y solo con los nunca vistos.
- Validación temporal: entrena con los años anteriores, calibra (isotónica) y elige el umbral (F1)
  con el siguiente, evalúa con el posterior. 2024 es la prueba final y no se usa para decidir nada.
- Pobreza estimada de un territorio = promedio de probabilidades calibradas ponderado por
  FACTOR07 × MIEPERHO. Contar hogares sobre el umbral la sobreestima (el umbral es para focalizar).
- Sin pesos en el entrenamiento (Solon et al., 2015); métricas sin ponderar y ponderadas.
- Excluidas por fuga de datos: gasto, ingreso, líneas de pobreza, estrato socioeconómico,
  perceptores y año. Excluidas por colinealidad exacta: `brecha_educ` e `indice_privacion`.
- Excluida por no ser comparable entre años: `internet` (P1144). Desde la ENAHO 2023 el
  cuestionario añade P114B1–B3 y P1144 cuenta también el internet móvil (55 % de hogares en
  2022, 90 % en 2023). El modelo entrenaría con una definición y se probaría con otra.
  Antes de agregar una variable, compara su media anual: un salto así delata un cambio de pregunta.
- OCUPINF no existe en 2024: la informalidad se reconstruye con el criterio OIT (`processing/empleo.py`).
- P106 (alquiler imputado) se mantiene, pero siempre se informa el modelo sin él.

## Resultados actuales (prueba ENAHO 2024, XGBoost)

38 predictores. AUC-ROC 0.8777, AUC-PR 0.6266, exhaustividad 0.778, precisión 0.498, umbral 0.322;
pobreza estimada 28.0 % frente a 27.6 % observada; error medio por departamento 3.9 pp;
DeLong frente al probit: +0.013 (p < 0.001). Si estas cifras cambian, actualiza la tesis con
`/actualizar-tesis`.

Estas cifras salen con las versiones de `requirements-lock.txt` (Python 3.14, xgboost 3.4.1).
El AUC es estable entre versiones, pero el umbral (máximo del F1 sobre una curva casi plana) no:
con otras versiones de las librerías cambia varias centésimas y con él la exhaustividad y la
precisión. Para reproducir la tesis, instala con `pip install -r requirements-lock.txt`.

## Formato de la tesis (Guía EPG UNA Puno 2024)

Times New Roman 12, interlineado 1.5, márgenes 3.5/2.5/2.5/2.5 cm; tablas con líneas solo
horizontales y encabezado gris (#BFBFBF); rótulo "Tabla N" en negrita y título en cursiva; nota
en 11 pt; citas APA 7 ("y" en el texto, "&" en la bibliografía). En la tesis los decimales van
con punto; en la web, con coma. Entre el Resumen y la Bibliografía deben quedar 60 a 120 páginas.

## Pendientes conocidos

- Anexos 8 y 9: formatos oficiales firmados.
- Hoja de jurados: falta la fecha de sustentación.
- Anexo 1: la indicadora de la COVID-19 figura en la dimensión "Geográfica" porque el capítulo II
  no define una dimensión temporal; decidir con el asesor si se crea una.
- `D:\Proyecto Ing Aldo\Matriz_de_consistencia_Tesis_Aldo_Zanabria.docx` es un archivo aparte y
  conserva los indicadores antiguos; el vigente es el Anexo 1 del borrador.

El Anexo 1 (matriz y operacionalización) lo escribe `herramientas/tesis/anexo1.py` desde el
catálogo de variables: si cambia `config/features.yaml`, se actualiza solo al regenerar el borrador.
- `actualizar.py` calcula las páginas con LibreOffice o, en Windows, con Microsoft Word.
