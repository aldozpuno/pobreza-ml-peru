# Herramientas para actualizar el borrador de la tesis

Reescriben el borrador (`BORRADOR DE TESIS FINAL.docx`) con los resultados del pipeline y
conservan el formato EPG del documento: estilos de títulos, rótulos de tablas y figuras con sus
marcadores, índices de tablas, figuras y general, y numeración de páginas.

| Archivo | Qué hace |
| --- | --- |
| `actualizar.py` | Punto de entrada: dos pasadas (la segunda con números de página) y reemplazo del original |
| `armar.py` | Ubica las secciones del borrador y las reemplaza |
| `datos.py` | Reúne las cifras desde `resultados/` y `web/public/data/` |
| `cap3.py` | Capítulo III desde 3.3 Muestra |
| `cap4.py` | Capítulo IV: resultados por objetivo específico |
| `cierre.py` | Discusión, conclusiones y recomendaciones |
| `textos.py` | Resumen, abstract, introducción, marco teórico 1.1.9, bibliografía, textos de la matriz e índices |
| `anexo1.py` | Anexo 1: indicadores de la matriz de consistencia y tabla de operacionalización, desde el catálogo de variables |
| `anexos.py` | Anexos 2, 3, 4, 5 y 7 |
| `constructor.py` | Bloques OOXML: títulos, párrafos, viñetas, tablas EPG, figuras y ecuaciones |
| `paginas.py` | Calcula las páginas desde un PDF (lo genera LibreOffice o, en Windows, Microsoft Word; requiere `pdftotext`) |
| `acronimos.py` | Lista de acrónimos: quita las siglas que el texto ya no usa y añade las que faltan |
| `figuras.py` | Genera la Figura 1 (integración de los módulos), el flujograma y las capturas de código; `figuras/fig_web.png` se toma a mano |

Uso: `python herramientas/tesis/actualizar.py "D:/Proyecto Ing Aldo/BORRADOR DE TESIS FINAL.docx"`.

Se puede ejecutar varias veces sobre el borrador ya corregido; en cada pasada se retiran las
imágenes que ya no se usan, para que el archivo no crezca. Sin LibreOffice ni Word, o sin
`pdftotext`, los índices quedan sin número de página hasta que se actualizan los campos en Word
(Ctrl+E y luego F9). Cierre el borrador en Word antes de ejecutarlo.
