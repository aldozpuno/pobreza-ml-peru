import { Component, computed, input, signal } from '@angular/core';
import { scaleLinear } from 'd3-scale';

import { anchoDelAnfitrion } from '../../core/ancho';
import { porcentaje, puntos } from '../../core/formato';
import { IncidenciaAnual } from '../../core/models';
import { GloboComponent } from './globo.component';

interface Cordon {
  anio: number;
  x: number;
  largo: number;       // personas
  largoHogar: number;  // hogares
  nudos: number[];     // cada 5 pp
  oficial: number | null;
  fila: IncidenciaAnual;
}

/**
 * La serie anual dibujada como un khipu: un cordón principal del que cuelga un cordón
 * por año. Su largo es la tasa de personas pobres y lleva un nudo cada 5 puntos; el
 * cordón secundario, más delgado, es la tasa de hogares. El anillo marca la cifra del INEI.
 */
@Component({
  selector: 'app-khipu',
  imports: [GloboComponent],
  templateUrl: './khipu.component.html',
  styleUrl: './khipu.component.css',
})
export class KhipuComponent {
  readonly serie = input.required<IncidenciaAnual[]>();
  readonly ancho = anchoDelAnfitrion(900);
  readonly activo = signal<Cordon | null>(null);

  readonly arriba = 54;
  readonly izquierda = 48;
  readonly porcentaje = porcentaje;
  readonly puntos = puntos;

  readonly alto = computed(() => (this.ancho() < 560 ? 320 : 440));
  readonly compacto = computed(() => this.ancho() < 560);

  readonly escala = computed(() =>
    scaleLinear().domain([0, 32]).range([0, this.alto() - this.arriba - 48]));

  readonly regla = computed(() =>
    [10, 20, 30].map((v) => ({ valor: v, y: this.arriba + this.escala()(v) })));

  readonly cordones = computed<Cordon[]>(() => {
    const filas = this.serie();
    const paso = (this.ancho() - this.izquierda - 16) / filas.length;
    const y = this.escala();
    return filas.map((fila, i) => {
      const nudos: number[] = [];
      for (let v = 5; v < fila.tasa_personas - 1.5; v += 5) nudos.push(y(v));
      return {
        anio: fila.anio,
        x: Math.round(this.izquierda + paso * (i + 0.5)),
        largo: y(fila.tasa_personas),
        largoHogar: y(fila.tasa_hogares),
        nudos,
        oficial: fila.tasa_oficial_inei === null ? null : y(fila.tasa_oficial_inei),
        fila,
      };
    });
  });

  /** Marcas diagonales que imitan la torsión del cordón principal. */
  readonly torsion = computed(() => {
    const marcas: number[] = [];
    for (let x = this.izquierda - 8; x < this.ancho() - 10; x += 7) marcas.push(x);
    return marcas;
  });

  etiqueta(c: Cordon): string {
    return this.compacto() ? c.fila.tasa_personas.toFixed(1).replace('.', ',') : porcentaje(c.fila.tasa_personas);
  }
}
