# Pobreza monetaria en el Perú — modelo predictivo (ENAHO 2017–2024)

Código de la tesis doctoral *Modelo predictivo de pobreza monetaria en el Perú utilizando
Machine Learning*, de Aldo Hernán Zanabria Gálvez (EPG UNA Puno). Versión 2, reconstruida
para atender las observaciones del asesor.

## Qué cambia respecto de la versión anterior

| Observación | Cómo se atiende |
| --- | --- |
| Datos apilados: un hogar puede repetirse entre años | Se conservan CONGLOME, VIVIENDA y HOGAR; la variable PANEL del módulo 100 y la llave entre años marcan a los repetidos; la prueba 2024 se evalúa con y sin ellos |
| Incluir la medición de la pobreza | Etapa `medir`: incidencia con FACTOR07 × MIEPERHO (método del Taller 6); el pipeline se detiene si no reproduce al INEI |
| Justificar el factor de expansión | Tasas poblacionales siempre ponderadas; métricas sin ponderar y ponderadas; el uso de pesos en el entrenamiento es un parámetro documentado |
| Relación teoría → variables → modelo | Cada variable de `config/features.yaml` declara su teoría y signo esperado; de ahí sale la tabla puente y se compara con el signo observado en SHAP |
| Rigor metodológico | Umbral elegido en el año de calibración; sensibilidad sin P106; códigos de vivienda corregidos (hacinamiento usaba P103, el material del piso); informalidad reconstruida con el criterio OIT y conexión a internet excluida, porque ambas cambian de definición dentro del periodo |
| Figuras y tablas en formato EPG | Figuras sin título interno y en español; tablas en `.docx` con el formato de la guía |

## Estructura

```
config/          parámetros (años, códigos INEI, hiperparámetros, catálogo de variables)
src/pobreza/     paquete por capas: data → processing → features/measurement → modeling
                 → evaluation → reporting; stages/ orquesta; cli.py es la entrada
tests/           pruebas con datos sintéticos que imitan la ENAHO
notebooks/       cuaderno de Colab que solo ejecuta las etapas
scripts/         demo con datos sintéticos
web/             web de resultados (Angular) que lee los JSON del pipeline
herramientas/    actualización del borrador de la tesis con los resultados (ver su README)
docs/            arquitectura y metodología
```

Detalle de cada capa en [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md); decisiones
metodológicas en [docs/METODOLOGIA.md](docs/METODOLOGIA.md).

## Cómo ejecutarlo

En Google Colab (recomendado, porque descarga del portal del INEI): abra
`notebooks/ejecutar_pipeline_colab.ipynb` y ejecute las celdas en orden.

En una computadora con Python 3.10 o superior:

```bash
pip install -r requirements-lock.txt   # versiones exactas con las que se obtuvieron las cifras de la tesis
pip install -e ".[dev]" --no-deps
pobreza todo            # o cada etapa: descargar, construir, medir, entrenar, evaluar, reportar
pytest                  # pruebas con datos sintéticos
python scripts/demo_sintetica.py   # demo completa sin conexión al INEI
```

Si el portal del INEI no responde, copie los zips a `datos/crudos/<año>/<módulo>.zip`
(módulos: `sumaria`, `vivienda`, `miembros`, `educacion`, `salud`, `empleo`, `programas`).

## Salidas

| Ruta | Contenido |
| --- | --- |
| `datos/procesados/hogares.parquet` | Base apilada, una fila por hogar-año |
| `resultados/reportes/figuras/` | Figuras para la tesis (PNG, 300 ppp) |
| `resultados/reportes/tablas_tesis.docx` | Tablas numeradas en formato EPG |
| `resultados/reportes/datos/` | Todos los resultados en CSV |
| `resultados/modelos/` | Modelo final, predicciones y umbrales |
| `web/public/data/` | Datos de la web de resultados |

## Web de resultados

```bash
cd web
npm install
npm start          # http://localhost:4500
npm run build      # web estática en web/dist/web/browser/
```

La carpeta `web/dist/web/browser/` se puede publicar en cualquier hosting estático
(GitHub Pages, Netlify, Vercel) o abrir con un servidor local. Detalle en `web/README.md`.

## Claude Code

El proyecto está preparado para Claude Code: `CLAUDE.md` resume el contexto y las decisiones, y
`claude-code/commands/` trae `/reproducir`, `/actualizar-tesis` y `/web`; cópialos a `.claude/commands/`.

## Agregar un año

Agregue el año a `anios` y su código a `codigos_inei` en `config/pipeline.yaml`, y la cifra
oficial a `incidencia_oficial`. Cambie `anio_prueba` en `config/model.yaml` si corresponde.
