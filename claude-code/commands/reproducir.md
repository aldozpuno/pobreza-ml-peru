---
description: Ejecuta el pipeline con los datos de la ENAHO y verifica los resultados
argument-hint: "[etapa opcional: construir | medir | entrenar | evaluar | reportar]"
---

Reproduce los resultados de la tesis.

1. Verifica que existan los 56 zip en `datos/crudos/{año}/{modulo}.zip` (2017–2024 × 7 módulos).
   Si faltan y están en `D:\Proyecto Ing Aldo\datos-inei\enaho_{año}_modulo{NN}.zip`, cópialos con
   el nombre que espera el pipeline (34 → sumaria, 01 → vivienda, 02 → miembros, 03 → educacion,
   04 → salud, 05 → empleo, 37 → programas). No descargues de nuevo lo que ya existe.
2. Ejecuta `pobreza $ARGUMENTS` si se indicó una etapa; si no, `pobreza todo`.
3. Comprueba en `resultados/reportes/datos/incidencia_anual.csv` que `diferencia_pp` sea ≤ 0.3 en
   todos los años, y resume `resumen_evaluacion.json` y `prueba_delong.csv`.
4. Ejecuta `pytest`.
5. Informa en español qué cifras cambiaron respecto de la sección "Resultados actuales" de
   CLAUDE.md; si cambiaron, actualiza esa sección y propone ejecutar `/actualizar-tesis`.
