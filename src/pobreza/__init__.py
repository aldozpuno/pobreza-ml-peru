"""Modelo predictivo de pobreza monetaria en el Perú (ENAHO 2017-2024).

Paquete organizado por capas:
    data         → saber dónde está cada archivo del INEI, descargarlo y leerlo
    processing   → una tabla por hogar a partir de cada módulo de la ENAHO
    measurement  → incidencia de pobreza como la calcula el INEI
    features     → catálogo, variables derivadas y control de fuga de datos
    modeling     → validación temporal, estimadores, calibración y umbral
    evaluation   → métricas, sesgo regional y explicabilidad
    reporting    → tablas y figuras para la tesis, datos para el dashboard
"""

__version__ = "2.0.0"
