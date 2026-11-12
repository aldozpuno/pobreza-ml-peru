import { Component, computed, input } from '@angular/core';

import { ModoMapa } from './mapa.component';

/** Leyenda de color del mapa: barra continua con los extremos rotulados. */
@Component({
  selector: 'app-escala',
  template: `
    <div class="escala">
      <span class="titulo">{{ titulo() }}</span>
      <span class="barra" [style.background]="fondo()"></span>
      <span class="extremos"><span>{{ minimo() }}</span>@if (modo() === 'divergente') {<span>0</span>}<span>{{ maximo() }}</span></span>
      @if (modo() === 'divergente') {
        <span class="extremos sentido"><span>subestima</span><span>sobreestima</span></span>
      }
    </div>
  `,
  styles: `
    .escala { display: grid; gap: 0.25rem; max-width: 18rem; font-size: var(--t-0); color: var(--tinta-3); }
    .titulo { color: var(--tinta-2); }
    .barra { height: 10px; border-radius: 2px; }
    .extremos { display: flex; justify-content: space-between; }
  `,
})
export class EscalaComponent {
  readonly titulo = input.required<string>();
  readonly minimo = input.required<string>();
  readonly maximo = input.required<string>();
  readonly modo = input<ModoMapa>('secuencial');
  readonly fondo = computed(() => this.modo() === 'secuencial'
    ? 'linear-gradient(90deg, var(--mapa-bajo), var(--mapa-alto))'
    : 'linear-gradient(90deg, var(--indigo), var(--medio), var(--cochinilla))');
}
