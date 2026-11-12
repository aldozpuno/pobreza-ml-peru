import { Component, computed, input } from '@angular/core';

export type Tono = 'indigo' | 'cochinilla' | 'neutro' | 'tinta';
export interface FilaBarra { clave: string; etiqueta: string; valor: number; tono: Tono; detalle?: string; nota?: string }

/**
 * Barras horizontales en HTML (no SVG): la etiqueta y su detalle pueden ocupar dos
 * líneas sin cálculos de texto. El valor se escribe al final de cada barra.
 */
@Component({
  selector: 'app-barras',
  template: `
    <ol class="barras" [attr.aria-label]="descripcion()">
      @for (f of filas(); track f.clave) {
        <li>
          <span class="nombre">{{ f.etiqueta }}@if (f.detalle) {<small>{{ f.detalle }}</small>}</span>
          <span class="pista">
            <span class="barra" [class]="'barra ' + f.tono" [style.width.%]="ancho(f.valor)"></span>
            <span class="valor">{{ formato()(f.valor) }}</span>
          </span>
          @if (f.nota !== undefined) { <span class="nota">{{ f.nota }}</span> }
        </li>
      }
    </ol>
  `,
  styles: `
    .barras { list-style: none; margin: 0; padding: 0; display: grid; gap: 0.55rem; }
    li { display: grid; grid-template-columns: minmax(8rem, 13rem) minmax(0, 1fr) auto; align-items: center; column-gap: 1rem; }
    .nombre { font-size: var(--t-1); line-height: 1.25; }
    .nombre small { display: block; color: var(--tinta-3); font-size: 12px; margin-top: 0.1rem; }
    .pista { display: flex; align-items: center; gap: 0.5rem; min-width: 0; }
    .barra { height: 12px; border-radius: 0 4px 4px 0; min-width: 2px; }
    .indigo { background: var(--indigo); } .cochinilla { background: var(--cochinilla); }
    .neutro { background: var(--neutro); } .tinta { background: var(--tinta); }
    .valor { font-size: var(--t-0); color: var(--tinta-2); white-space: nowrap; }
    .nota { font-size: var(--t-0); color: var(--tinta-3); min-width: 7.5rem; }
    @media (max-width: 600px) {
      li { grid-template-columns: minmax(0, 1fr) auto; row-gap: 0.25rem; }
      .pista { grid-column: 1 / -1; grid-row: 2; }
      .nota { min-width: 0; text-align: right; }
    }
  `,
})
export class BarrasComponent {
  readonly filas = input.required<FilaBarra[]>();
  readonly formato = input<(v: number) => string>((v) => String(v));
  readonly maximo = input<number>();
  readonly descripcion = input('Gráfico de barras');

  private readonly tope = computed(() => this.maximo() ?? Math.max(...this.filas().map((f) => f.valor)));
  ancho(valor: number): number { return Math.max(0, (valor / this.tope()) * 82); }
}
