import { Component, computed, input, signal } from '@angular/core';
import { extent } from 'd3-array';
import { scaleLinear } from 'd3-scale';
import { line } from 'd3-shape';

import { anchoDelAnfitrion } from '../../core/ancho';
import { GloboComponent } from './globo.component';

export interface Punto { x: number; y: number }
export interface Serie { id: string; nombre: string; color: string; puntos: Punto[]; marcas?: boolean }

/**
 * Gráfico de líneas genérico (series anuales, curvas ROC y PR, calibración).
 * Un solo eje y; etiquetas directas al final de cada línea y leyenda cuando hay más
 * de una serie; al pasar el cursor, una guía vertical con los valores de todas las series.
 */
@Component({
  selector: 'app-lineas',
  imports: [GloboComponent],
  templateUrl: './lineas.component.html',
  styleUrl: './lineas.component.css',
})
export class LineasComponent {
  readonly series = input.required<Serie[]>();
  readonly alto = input(280);
  readonly dominioX = input<[number, number]>();
  readonly dominioY = input<[number, number]>();
  readonly formatoX = input<(v: number) => string>((v) => String(v));
  readonly formatoY = input<(v: number) => string>((v) => String(v));
  readonly ticksX = input<number[]>();
  readonly tituloX = input<string>();
  readonly tituloY = input<string>();
  readonly diagonal = input(false);
  readonly descripcion = input('Gráfico de líneas');

  readonly ancho = anchoDelAnfitrion(600);
  readonly guia = signal<number | null>(null);
  readonly m = { arriba: 26, derecha: 20, abajo: 40, izquierda: 52 };

  readonly derecha = computed(() => (this.series().length > 1 && this.ancho() > 480 ? 92 : this.m.derecha));

  readonly x = computed(() => {
    const valores = this.series().flatMap((s) => s.puntos.map((p) => p.x));
    const dominio = this.dominioX() ?? (extent(valores) as [number, number]);
    return scaleLinear().domain(dominio).range([this.m.izquierda, this.ancho() - this.derecha()]);
  });

  readonly y = computed(() => {
    const valores = this.series().flatMap((s) => s.puntos.map((p) => p.y));
    const dominio = this.dominioY() ?? [0, Math.max(...valores) * 1.1];
    return scaleLinear().domain(dominio).nice().range([this.alto() - this.m.abajo, this.m.arriba]);
  });

  readonly marcasX = computed(() => this.ticksX() ?? this.x().ticks(this.ancho() < 480 ? 4 : 6));
  readonly marcasY = computed(() => this.y().ticks(5));

  readonly trazos = computed(() => {
    const x = this.x(), y = this.y();
    const generador = line<Punto>().x((p) => x(p.x)).y((p) => y(p.y));
    return this.series().map((s) => {
      const ultimo = s.puntos[s.puntos.length - 1];
      return { ...s, d: generador(s.puntos) ?? '', fin: { x: x(ultimo.x), y: y(ultimo.y) } };
    });
  });

  /** Etiquetas finales separadas al menos 16 px para que no se monten. */
  readonly etiquetasFinales = computed(() => {
    const orden = [...this.trazos()].sort((a, b) => a.fin.y - b.fin.y);
    let previo = -Infinity;
    return orden.map((t) => {
      const yy = Math.max(t.fin.y, previo + 16);
      previo = yy;
      return { id: t.id, nombre: t.nombre, color: t.color, x: t.fin.x + 8, y: yy + 4 };
    });
  });

  readonly valoresGuia = computed(() => {
    const gx = this.guia();
    if (gx === null) return null;
    const filas = this.series().map((s) => {
      const p = s.puntos.reduce((a, b) => (Math.abs(b.x - gx) < Math.abs(a.x - gx) ? b : a));
      return { nombre: s.nombre, color: s.color, x: p.x, y: p.y };
    });
    return { x: filas[0].x, filas };
  });

  mover(evento: MouseEvent): void {
    const caja = (evento.currentTarget as SVGRectElement).getBoundingClientRect();
    this.guia.set(this.x().invert(evento.clientX - caja.left + this.m.izquierda));
  }
}
