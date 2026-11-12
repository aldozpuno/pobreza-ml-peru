---
description: Reescribe los capítulos III y IV, conclusiones, resumen, anexos e índices del borrador con los resultados actuales
argument-hint: "[ruta del borrador .docx]"
---

Actualiza el borrador de la tesis con los resultados del pipeline.

1. Si no se indicó ruta, usa `D:\Proyecto Ing Aldo\BORRADOR DE TESIS FINAL.docx`. Pide al usuario
   que lo cierre en Word antes de continuar.
2. Verifica que `resultados/reportes/datos/` y `web/public/data/` estén al día (ejecuta
   `pobreza evaluar` y `pobreza reportar` si cambió el código o los datos).
3. Si cambió el código citado en el Anexo 7 o el flujo del proceso, ejecuta
   `python herramientas/tesis/figuras.py`.
4. Ejecuta `python herramientas/tesis/actualizar.py "<ruta>"`. Trabaja sobre el original: no dejes
   copias en `D:\Proyecto Ing Aldo`; si el usuario pide un respaldo, usa `--respaldo` con una ruta
   fuera de esa carpeta.
5. Revisa que la salida no tenga avisos ("AVISO", "sin encontrar") y que haya 17 tablas y 14 figuras
   (o explica por qué cambió el número).
6. Recuerda al usuario actualizar los campos en Word: Ctrl+E y luego F9.

Para cambiar textos, edita los módulos de `herramientas/tesis/` (`cap3.py`, `cap4.py`, `cierre.py`,
`textos.py`, `anexos.py`). Las cifras salen de `datos.py`; nunca se escriben a mano.
