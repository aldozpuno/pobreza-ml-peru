import { Component, computed, input, signal } from '@angular/core';
import { scaleLinear } from 'd3-scale';

import { anchoDelAnfitrion } from '../../core/ancho';
import { GloboComponent } from './globo.component';

export interface FilaPesas { clave: string; etiqueta: string; a: number; b: number }

/**
 * Gráfico de pesas: dos valores por fila unidos por un segmento
 * (observado frente a estimado, o antes frente a después).
 * `a` se dibuja como círculo hueco en tinta y `b` como círculo lleno de color.
 */
@Component({
  selector: 'app-pesas',
  imports: [GloboComponent],
  template: `
    <ul class="leyenda">
      <li><i class="hueco"></i>{{ nombreA() }}</li>
      <li><i class="lleno"></i>{{ nombreB() }}</li>
    </ul>
    <div class="lienzo" (mouseleave)="activa.set(null)">
      <svg [attr.width]="ancho()" [attr.height]="alto()" role="img" [attr.aria-label]="descripcion()">
        @for (t of marcas(); track t) {
          <line class="rejilla" [attr.x1]="x()(t)" [attr.x2]="x()(t)" y1="0" [attr.y2]="alto() - 22" />
          <text class="eje" [attr.x]="x()(t)" [attr.y]="alto() - 6" text-anchor="middle">{{ formato()(t) }}</text>
        }
        @for (f of filas(); track f.clave; let i = $index) {
          <g [attr.transform]="'translate(0,' + (i * paso + paso / 2) + ')'" (mouseenter)="activa.set({ fila: f, y: i * paso + paso / 2 })">
            <rect class="zona" x="0" [attr.y]="-paso / 2" [attr.width]="ancho()" [attr.height]="paso" />
            <text class="etiqueta" [attr.x]="izquierda() - 12" y="4" text-anchor="end">{{ f.etiqueta }}</text>
            <line class="union" [attr.x1]="x()(f.a)" [attr.x2]="x()(f.b)" y1="0" y2="0" />
            <circle class="punto-a" [attr.cx]="x()(f.a)" cy="0" r="5" />
            <circle class="punto-b" [attr.cx]="x()(f.b)" cy="0" r="5" />
          </g>
        }
      </svg>
      @if (activa(); as a) {
        <app-globo [x]="x()(Math.max(a.fila.a, a.fila.b))" [y]="a.y" [ancho]="ancho()">
          <span class="g-titulo">{{ a.fila.etiqueta }}</span>
          <span class="g-fila"><span>{{ nombreA() }}</span><b>{{ formato()(a.fila.a) }}</b></span>
          <span class="g-fila"><span>{{ nombreB() }}</span><b>{{ formato()(a.fila.b) }}</b></span>
          <span class="g-fila"><span>Diferencia</span><b>{{ diferencia()(a.fila.b - a.fila.a) }}</b></span>
        </app-globo>
      }
    </div>
  `,
  styles: `
    :host { display: block; min-width: 0; }
    .lienzo { position: relative; }
    svg { display: block; overflow: visible; }
    .rejilla { stroke: var(--linea-suave); }
    .eje { fill: var(--tinta-3); font-size: 12px; }
    .etiqueta { fill: var(--tinta-2); font-size: 13px; }
    .union { stroke: var(--neutro); stroke-width: 2; }
    .punto-a { fill: var(--papel); stroke: var(--tinta); stroke-width: 1.8; }
    .punto-b { fill: var(--cochinilla); stroke: var(--papel); stroke-width: 2; }
    .zona { fill: transparent; }
    g:hover .zona { fill: var(--linea-suave); opacity: 0.5; }
    .leyenda { list-style: none; display: flex; gap: 1.2rem; padding: 0; margin: 0 0 0.6rem; font-size: var(--t-0); color: var(--tinta-2); }
    .leyenda i { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 0.4rem; vertical-align: -1px; }
    .hueco { border: 1.8px solid var(--tinta); }
    .lleno { background: var(--cochinilla); }
  `,
})
export class PesasComponent {
  readonly filas = input.required<FilaPesas[]>();
  readonly nombreA = input.required<string>();
  readonly nombreB = input.required<string>();
  readonly formato = input<(v: number) => string>((v) => String(v));
  readonly diferencia = input<(v: number) => string>((v) => String(v));
  readonly dominio = input<[number, number]>();
  readonly descripcion = input('Comparación de dos valores por fila');

  readonly Math = Math;
  readonly paso = 26;
  readonly ancho = anchoDelAnfitrion(600);
  readonly activa = signal<{ fila: FilaPesas; y: number } | null>(null);
  readonly alto = computed(() => this.filas().length * this.paso + 26);
  readonly izquierda = computed(() => (this.ancho() < 480 ? 112 : 190));

  readonly x = computed(() => {
    const valores = this.filas().flatMap((f) => [f.a, f.b]);
    const dominio = this.dominio() ?? [0, Math.max(...valores)];
    return scaleLinear().domain(dominio).nice().range([this.izquierda(), this.ancho() - 16]);
  });
  readonly marcas = computed(() => this.x().ticks(this.ancho() < 480 ? 3 : 6));
}
