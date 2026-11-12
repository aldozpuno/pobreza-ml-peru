import { Component, computed, input } from '@angular/core';

/**
 * Globo de información que sigue al cursor dentro de un gráfico.
 * Se coloca a la derecha del punto y salta a la izquierda cerca del borde.
 */
@Component({
  selector: 'app-globo',
  template: `<div class="globo" [style.left.px]="izquierda()" [style.top.px]="y()" role="status"><ng-content /></div>`,
  styles: `
    :host { position: absolute; inset: 0; pointer-events: none; }
    .globo {
      position: absolute; transform: translateY(-50%); min-width: 9rem; max-width: 16rem;
      background: var(--tinta); color: var(--papel); border-radius: var(--radio);
      padding: 0.5rem 0.7rem; font-size: var(--t-0); line-height: 1.4; box-shadow: 0 6px 18px rgb(0 0 0 / 0.18);
    }
  `,
})
export class GloboComponent {
  readonly x = input.required<number>();
  readonly y = input.required<number>();
  readonly ancho = input.required<number>();
  readonly izquierda = computed(() => (this.x() + 200 > this.ancho() ? this.x() - 196 : this.x() + 14));
}
