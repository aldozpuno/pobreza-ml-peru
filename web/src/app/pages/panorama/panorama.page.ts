import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';

import { DatosService } from '../../core/datos.service';
import { decimal, entero, porcentaje, puntos } from '../../core/formato';
import { IncidenciaAnual } from '../../core/models';
import { CienComponent } from '../../shared/charts/cien.component';
import { KhipuComponent } from '../../shared/charts/khipu.component';
import { LineasComponent, Serie } from '../../shared/charts/lineas.component';
import { FiguraComponent } from '../../shared/ui/figura.component';
import { Columna, TablaComponent } from '../../shared/ui/tabla.component';

/** Portada: cuánta pobreza hay, qué tan bien la identifica el modelo y la brecha rural. */
@Component({
  selector: 'app-panorama',
  imports: [RouterLink, KhipuComponent, LineasComponent, CienComponent, FiguraComponent, TablaComponent],
  templateUrl: './panorama.page.html',
  styleUrl: './panorama.page.css',
})
export class PanoramaPage {
  private readonly d = inject(DatosService).datos;
  readonly porcentaje = porcentaje;
  readonly decimal = decimal;
  readonly entero = entero;
  readonly Math = Math;

  readonly meta = computed(() => this.d()!.meta);
  readonly kpis = computed(() => this.d()!.resumen.kpis);
  readonly serie = computed(() => this.d()!.resumen.serie_anual);
  readonly ultimo = computed(() => this.serie()[this.serie().length - 1]);
  readonly prueba = computed(() => this.d()!.modelo.prueba);
  readonly noVistos = computed(() => this.prueba().find((p) => p.Variante.startsWith('Solo hogares no vistos')));

  /** Lecturas del desempeño en la prueba, expresadas como "n de cada 100". */
  readonly lecturas = computed(() => {
    const k = this.kpis();
    return [
      { valor: k.recall, texto: 'de cada 100 hogares pobres son identificados por el modelo',
        nota: `Los ${Math.round((1 - k.recall) * 100)} restantes quedan fuera: es el error de exclusión.` },
      { valor: k.precision, texto: 'de cada 100 hogares señalados como pobres lo son de verdad',
        nota: 'Los demás son hogares cercanos a la línea de pobreza que el modelo confunde.' },
      { valor: k.auc_roc, texto: 'de cada 100 pares de un hogar pobre y uno no pobre quedan bien ordenados',
        nota: `Es el AUC-ROC (${decimal(k.auc_roc, 3)}): la probabilidad de que el pobre reciba un puntaje mayor.` },
    ];
  });

  readonly areas = computed<Serie[]>(() => {
    const filas = this.d()!.resumen.serie_area;
    const serie = (rural: number) => filas.filter((f) => f.rural === rural).map((f) => ({ x: f.anio, y: f.tasa_personas }));
    return [
      { id: 'rural', nombre: 'Rural', color: 'var(--cochinilla)', puntos: serie(1), marcas: true },
      { id: 'urbana', nombre: 'Urbana', color: 'var(--indigo)', puntos: serie(0), marcas: true },
    ];
  });

  readonly brecha = computed(() => {
    const [r, u] = this.areas().map((s) => s.puntos);
    const fin = (p: { y: number }[]) => p[p.length - 1].y;
    return { rural: fin(r), urbana: fin(u), veces: fin(r) / fin(u),
             desde: r[0].x, ruralInicio: r[0].y, urbanaInicio: u[0].y };
  });

  readonly formatoAnio = (v: number) => String(v);
  readonly formatoPct = (v: number) => `${v} %`;

  readonly columnasAnuales: Columna<IncidenciaAnual>[] = [
    { titulo: 'Año', valor: (f) => f.anio },
    { titulo: 'Hogares en la muestra', valor: (f) => entero(f.hogares_muestra), numerica: true },
    { titulo: 'Personas pobres', valor: (f) => porcentaje(f.tasa_personas, 2), numerica: true },
    { titulo: 'Hogares pobres', valor: (f) => porcentaje(f.tasa_hogares, 2), numerica: true },
    { titulo: 'INEI', valor: (f) => porcentaje(f.tasa_oficial_inei), numerica: true },
    { titulo: 'Diferencia', valor: (f) => puntos(f.diferencia_pp, 2), numerica: true },
  ];
}
