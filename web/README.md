# Web de resultados

Aplicación Angular 19 que presenta los resultados del modelo. No calcula nada: lee los
seis JSON que escribe el pipeline (`pobreza reportar`) en `public/data/`.

```bash
npm install
npm start           # desarrollo en http://localhost:4500 (abre el navegador)
npm run preview     # sirve la versión compilada en http://localhost:4501
npm run build       # salida estática en dist/web/browser/
```

## Estructura

```
src/
  index.html              documento base (fuente Archivo empaquetada, sin CDN)
  styles.css              importa los estilos globales
  styles/                 tokens (colores, tipos), base, maquetación y tablas
  app/
    app.component.*       cabecera, navegación, estados de carga y pie
    app.routes.ts         una ruta por página, cargada bajo demanda (#/territorio …)
    core/
      models.ts           contrato de datos con src/pobreza/reporting/dashboard_export.py
      datos.service.ts    carga los JSON una vez y los expone como señales
      formato.ts          números en español (coma decimal, espacio de miles)
      ancho.ts            ancho real del gráfico para dibujar en píxeles
    shared/
      charts/             gráficos SVG propios: khipu, líneas, mapa, pesas, barras,
                          matriz de confusión, pliegues, "n de cada 100", globo
      ui/                 figura (con alternancia gráfico/tabla), tabla, conmutador
    pages/                panorama, territorio, modelo, variables, metodo
```

## Diseño

- Paleta de tintes andinos: índigo y grana cochinilla sobre piedra. Las dos series están
  validadas para daltonismo y tienen su versión para el modo oscuro del sistema.
- Tipografía única (Archivo) con su eje de ancho: condensada en titulares, normal en texto.
- La serie anual se dibuja como un khipu: un cordón por año, un nudo cada 5 puntos.
- Toda figura con datos detallados ofrece "Ver tabla", de modo que nada depende solo del
  color o del cursor.

## Si cambia el pipeline

Si se agrega o renombra un campo en `dashboard_export.py`, actualice `core/models.ts`.
