"""Etapas del pipeline. Cada etapa lee lo que dejó la anterior en disco y guarda su salida,
de modo que se puede repetir una etapa sin volver a correr las demás.

    descarga → construccion → medicion → entrenamiento → evaluacion → reportes
"""
