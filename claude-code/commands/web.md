---
description: Compila y sirve la web de resultados (Angular) con los datos actuales
---

1. Si cambió el pipeline, ejecuta `pobreza reportar` para regenerar `web/public/data/*.json`.
2. En `web/`: `npm install` (solo si falta `node_modules`) y `npm run build`.
3. Ejecuta `npm start` para servirla en http://localhost:4500.
4. Si cambia un campo en `src/pobreza/reporting/dashboard_export.py`, actualiza
   `web/src/app/core/models.ts` antes de compilar.
