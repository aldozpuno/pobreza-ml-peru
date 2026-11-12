import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { forkJoin } from 'rxjs';

import { DatosTablero } from './models';

export type EstadoCarga = 'cargando' | 'listo' | 'error';

/** Archivos que escribe el pipeline (`pobreza reportar`) en `web/public/data/`. */
const ARCHIVOS = ['meta', 'resumen', 'territorio', 'modelo', 'explicabilidad', 'metodologia'] as const;

/**
 * Carga una sola vez los seis JSON del pipeline y los expone como señales.
 * Las páginas leen `datos()` y no hacen peticiones propias.
 */
@Injectable({ providedIn: 'root' })
export class DatosService {
  private readonly http = inject(HttpClient);
  private readonly _datos = signal<DatosTablero | null>(null);
  private readonly _estado = signal<EstadoCarga>('cargando');

  readonly datos = this._datos.asReadonly();
  readonly estado = this._estado.asReadonly();
  readonly esSintetico = computed(() => this._datos()?.meta.origen === 'sintetico');

  constructor() {
    const peticiones = Object.fromEntries(
      ARCHIVOS.map((nombre) => [nombre, this.http.get(`data/${nombre}.json`)]),
    );
    forkJoin(peticiones).subscribe({
      next: (respuesta) => {
        this._datos.set(respuesta as unknown as DatosTablero);
        this._estado.set('listo');
      },
      error: () => this._estado.set('error'),
    });
  }
}
