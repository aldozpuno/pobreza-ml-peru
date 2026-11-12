import { Component, computed, input } from '@angular/core';

import { entero, millones } from '../../core/formato';

interface Celda { Celda: string; Hogares: number; 'Personas expandidas': number }

/**
 * Matriz de confusión del año de prueba. Cada celda muestra hogares de la muestra y
 * personas que representan; el tono indica si la celda es acierto o error.
 */
@Component({
  selector: 'app-matriz',
  template: `
    <div class="matriz" role="table" aria-label="Matriz de confusión">
      <div role="row" class="fila cabeza">
        <span role="columnheader"></span>
        <span role="columnheader">El modelo dice: pobre</span>
        <span role="columnheader">El modelo dice: no pobre</span>
      </div>
      @for (f of filas(); track f.nombre) {
        <div role="row" class="fila">
          <span role="rowheader" class="lado">{{ f.nombre }}</span>
          @for (c of f.celdas; track c.titulo) {
            <span role="cell" class="celda" [class.error]="c.error">
              <b>{{ entero(c.hogares) }}</b> hogares
              <small>{{ millones(c.personas) }} de personas</small>
              <em>{{ c.titulo }}</em>
            </span>
          }
        </div>
      }
    </div>
  `,
  styles: `
    .matriz { display: grid; gap: 4px; font-size: var(--t-1); }
    .fila { display: grid; grid-template-columns: 8.5rem 1fr 1fr; gap: 4px; }
    .cabeza span { font-size: var(--t-0); color: var(--tinta-3); padding: 0 0.6rem 0.2rem; }
    .lado { font-size: var(--t-0); color: var(--tinta-2); align-self: center; }
    .celda { background: var(--linea-suave); padding: 0.8rem 0.9rem; border-radius: var(--radio); display: grid; gap: 0.15rem; }
    .celda.error { background: var(--cochinilla-tenue); }
    .celda b { font-size: 1.6rem; font-weight: 700; font-variation-settings: "wdth" 110; line-height: 1.1; }
    .celda small { color: var(--tinta-3); font-size: var(--t-0); }
    .celda em { font-style: normal; font-size: var(--t-0); color: var(--tinta-2); margin-top: 0.3rem; }
    .error em { color: var(--cochinilla); font-weight: 600; }
    @media (max-width: 520px) { .fila { grid-template-columns: 5.5rem 1fr 1fr; } .celda b { font-size: 1.25rem; } }
  `,
})
export class MatrizComponent {
  readonly celdas = input.required<Celda[]>();
  readonly entero = entero;
  readonly millones = millones;

  readonly filas = computed(() => {
    const buscar = (texto: string) => this.celdas().find((c) => c.Celda.startsWith(texto))!;
    const celda = (texto: string, titulo: string, error: boolean) => {
      const c = buscar(texto);
      return { titulo, error, hogares: c.Hogares, personas: c['Personas expandidas'] };
    };
    return [
      { nombre: 'Es pobre', celdas: [celda('Verdadero positivo', 'Acierto', false), celda('Falso negativo', 'Exclusión: pobre no identificado', true)] },
      { nombre: 'No es pobre', celdas: [celda('Falso positivo', 'Filtración: no pobre señalado', true), celda('Verdadero negativo', 'Acierto', false)] },
    ];
  });
}
