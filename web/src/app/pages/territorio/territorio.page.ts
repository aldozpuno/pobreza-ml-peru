import { Component, computed, inject, signal } from '@angular/core';

import { DatosService } from '../../core/datos.service';
import { decimal, entero, porcentaje, puntos } from '../../core/formato';
import { SesgoDepartamento } from '../../core/models';
import { BarrasComponent, FilaBarra } from '../../shared/charts/barras.component';
import { EscalaComponent } from '../../shared/charts/escala.component';
import { MapaComponent } from '../../shared/charts/mapa.component';
import { FilaPesas, PesasComponent } from '../../shared/charts/pesas.component';
import { FiguraComponent } from '../../shared/ui/figura.component';
import { Columna, TablaComponent } from '../../shared/ui/tabla.component';

/** Puno se resalta por ser la región de la universidad donde se presenta la tesis. */
const RESALTADO = '21';

/** Pobreza por departamento y error territorial del modelo en el año de prueba. */
@Component({
  selector: 'app-territorio',
  imports: [MapaComponent, EscalaComponent, BarrasComponent, PesasComponent, FiguraComponent, TablaComponent],
  templateUrl: './territorio.page.html',
  styleUrl: './territorio.page.css',
})
export class TerritorioPage {
  private readonly d = inject(DatosService).datos;
  readonly porcentaje = porcentaje;
  readonly decimal = decimal;

  readonly anios = computed(() => this.d()!.meta.anios);
  readonly anioPrueba = computed(() => this.d()!.meta.anio_prueba);
  readonly anio = signal(this.d()!.meta.anios.at(-1)!);

  private readonly delAnio = computed(() =>
    this.d()!.territorio.incidencia.filter((f) => f.anio === this.anio()));

  readonly valores = computed(() =>
    Object.fromEntries(this.delAnio().map((f) => [f.departamento, f.tasa_personas])));

  /** Escala fija para todos los años: así el mapa compara años sin cambiar de colores. */
  readonly dominio = computed<[number, number]>(() => {
    const todas = this.d()!.territorio.incidencia.map((f) => f.tasa_personas);
    return [Math.floor(Math.min(...todas)), Math.ceil(Math.max(...todas))];
  });

  readonly ranking = computed<FilaBarra[]>(() =>
    [...this.delAnio()].sort((a, b) => b.tasa_personas - a.tasa_personas).map((f) => ({
      clave: f.departamento, etiqueta: f.nombre, valor: f.tasa_personas,
      tono: f.departamento === RESALTADO ? 'cochinilla' : 'tinta',
    })));

  readonly muestra = computed(() => (codigo: string) => {
    const fila = this.delAnio().find((f) => f.departamento === codigo);
    return fila ? `${entero(fila.hogares_muestra)} hogares en la muestra` : null;
  });

  // Error del modelo por departamento (año de prueba)
  readonly sesgo = computed(() => this.d()!.territorio.sesgo_prueba);
  readonly resumen = computed(() => this.d()!.modelo.sesgo_regional);
  readonly mayorError = computed(() =>
    [...this.sesgo()].sort((a, b) => Math.abs(b.sesgo_pp) - Math.abs(a.sesgo_pp))[0]);
  readonly valoresSesgo = computed(() => Object.fromEntries(this.sesgo().map((f) => [f.codigo, f.sesgo_pp])));
  readonly dominioSesgo = computed<[number, number]>(() => {
    const limite = Math.ceil(Math.max(...this.sesgo().map((f) => Math.abs(f.sesgo_pp))));
    return [-limite, limite];
  });
  readonly pesas = computed<FilaPesas[]>(() => this.sesgo().map((f) => ({
    clave: f.codigo, etiqueta: f.departamento, a: f.tasa_observada, b: f.tasa_predicha })));
  readonly detalleSesgo = computed(() => (codigo: string) => {
    const f = this.sesgo().find((s) => s.codigo === codigo);
    return f ? `Observada ${porcentaje(f.tasa_observada)}, estimada ${porcentaje(f.tasa_predicha)}` : null;
  });

  readonly formatoPct = (v: number) => porcentaje(v);
  readonly formatoEje = (v: number) => `${v} %`;
  readonly formatoPp = (v: number) => puntos(v);

  readonly columnasSesgo: Columna<SesgoDepartamento>[] = [
    { titulo: 'Departamento', valor: (f) => f.departamento },
    { titulo: 'Hogares', valor: (f) => entero(f.hogares), numerica: true },
    { titulo: 'Observada', valor: (f) => porcentaje(f.tasa_observada), numerica: true },
    { titulo: 'Estimada', valor: (f) => porcentaje(f.tasa_predicha), numerica: true },
    { titulo: 'Diferencia', valor: (f) => puntos(f.sesgo_pp), numerica: true },
    { titulo: 'Sobre el umbral', valor: (f) => porcentaje(f.tasa_clasificados), numerica: true },
  ];

  cambiarAnio(evento: Event): void {
    this.anio.set(Number((evento.target as HTMLInputElement).value));
  }
}
