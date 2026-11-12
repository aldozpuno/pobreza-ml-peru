import { HttpClient } from '@angular/common/http';
import { Component, computed, inject, input, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import type { Feature, FeatureCollection, Geometry } from 'geojson';
import { geoMercator, geoPath } from 'd3-geo';
import { feature } from 'topojson-client';
import type { Topology } from 'topojson-specification';

import { anchoDelAnfitrion } from '../../core/ancho';
import { GloboComponent } from './globo.component';

type Propiedades = { FIRST_IDDP: string; NOMBDEP: string };
export type ModoMapa = 'secuencial' | 'divergente';

/**
 * Mapa coroplético de los 25 departamentos (código INEI en `FIRST_IDDP`).
 * Secuencial: un solo tono de claro a oscuro. Divergente: índigo por debajo de cero,
 * cochinilla por encima y gris en el punto medio.
 */
@Component({
  selector: 'app-mapa',
  imports: [GloboComponent],
  template: `
    <div class="lienzo" (mouseleave)="activo.set(null)">
      <svg [attr.width]="ancho()" [attr.height]="alto()" role="img" [attr.aria-label]="descripcion()">
        @for (d of departamentos(); track d.codigo) {
          <path [attr.d]="d.d" [style.fill]="d.color" [class.activo]="activo()?.codigo === d.codigo"
                (mouseenter)="activo.set(d)" tabindex="0" (focus)="activo.set(d)" (blur)="activo.set(null)"
                [attr.aria-label]="d.nombre + ': ' + d.texto" />
        }
      </svg>
      @if (activo(); as a) {
        <app-globo [x]="a.cx" [y]="a.cy" [ancho]="ancho()">
          <span class="g-titulo">{{ a.nombre }}</span>
          <span>{{ a.texto }}</span>
          @if (detalle()(a.codigo); as extra) { <span class="extra">{{ extra }}</span> }
        </app-globo>
      }
    </div>
  `,
  styles: `
    :host { display: block; min-width: 0; }
    .lienzo { position: relative; }
    svg { display: block; margin: 0 auto; }
    path { stroke: var(--papel); stroke-width: 1; stroke-linejoin: round; cursor: default; outline: none; }
    path.activo { stroke: var(--tinta); stroke-width: 2; }
    .extra { display: block; opacity: 0.8; margin-top: 0.15rem; }
  `,
})
export class MapaComponent {
  private readonly http = inject(HttpClient);
  private readonly topo = toSignal(this.http.get<Topology>('peru-departamentos.topo.json'));

  readonly valores = input.required<Record<string, number>>();
  readonly dominio = input.required<[number, number]>();
  readonly modo = input<ModoMapa>('secuencial');
  readonly formato = input<(v: number) => string>((v) => String(v));
  readonly detalle = input<(codigo: string) => string | null>(() => null);
  readonly descripcion = input('Mapa del Perú por departamento');

  readonly ancho = anchoDelAnfitrion(420);
  readonly alto = computed(() => Math.min(620, Math.round(this.ancho() * 1.32)));
  readonly activo = signal<{ codigo: string; nombre: string; texto: string; cx: number; cy: number } | null>(null);

  private readonly geo = computed(() => {
    const t = this.topo();
    if (!t) return null;
    const objeto = Object.values(t.objects)[0];
    return feature(t, objeto) as unknown as FeatureCollection<Geometry, Propiedades>;
  });

  readonly departamentos = computed(() => {
    const geo = this.geo();
    if (!geo) return [];
    const ancho = Math.min(this.ancho(), 470);
    const proyeccion = geoMercator().fitSize([ancho, this.alto()], geo);
    const camino = geoPath(proyeccion);
    const desplazar = (this.ancho() - ancho) / 2;
    return geo.features.map((f: Feature<Geometry, Propiedades>) => {
      const codigo = f.properties.FIRST_IDDP;
      const valor = this.valores()[codigo];
      const [cx, cy] = camino.centroid(f);
      return {
        codigo,
        nombre: this.nombre(f.properties.NOMBDEP),
        d: camino(f) ?? '',
        color: valor === undefined ? 'var(--linea)' : this.color(valor),
        texto: valor === undefined ? 'Sin dato' : this.formato()(valor),
        cx: cx + desplazar, cy,
      };
    });
  });

  /** Color con mezcla OKLab entre tokens CSS, de modo que también funciona en modo oscuro. */
  private color(valor: number): string {
    const [min, max] = this.dominio();
    if (this.modo() === 'secuencial') {
      const t = Math.max(0, Math.min(1, (valor - min) / (max - min)));
      return `color-mix(in oklab, var(--mapa-alto) ${Math.round(t * 100)}%, var(--mapa-bajo))`;
    }
    const limite = Math.max(Math.abs(min), Math.abs(max));
    const t = Math.min(1, Math.abs(valor) / limite);
    const polo = valor < 0 ? 'var(--indigo)' : 'var(--cochinilla)';
    return `color-mix(in oklab, ${polo} ${Math.round(t * 100)}%, var(--medio))`;
  }

  private nombre(mayusculas: string): string {
    const correcciones: Record<string, string> = {
      ANCASH: 'Áncash', APURIMAC: 'Apurímac', HUANUCO: 'Huánuco', JUNIN: 'Junín', 'SAN MARTIN': 'San Martín',
      'MADRE DE DIOS': 'Madre de Dios', 'LA LIBERTAD': 'La Libertad', 'CALLAO': 'Callao',
    };
    return correcciones[mayusculas] ?? mayusculas.charAt(0) + mayusculas.slice(1).toLowerCase();
  }
}
