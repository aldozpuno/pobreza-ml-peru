import { Component, computed, inject, signal } from '@angular/core';

import { DatosService } from '../../core/datos.service';
import { entero, porcentaje } from '../../core/formato';
import { Metodologia, VariableCatalogo } from '../../core/models';
import { PlieguesComponent } from '../../shared/charts/pliegues.component';
import { FiguraComponent } from '../../shared/ui/figura.component';
import { Columna, TablaComponent } from '../../shared/ui/tabla.component';

type FilaPanel = Metodologia['panel'][number];
type FilaFuga = Metodologia['fuga'][number];

/** Etapas del pipeline en el orden en que se ejecutan (`pobreza <etapa>`). */
const ETAPAS = [
  { comando: 'descargar', nombre: 'Descargar', texto: 'Baja del INEI los módulos 01, 02, 03, 04, 05, 34 y 37 de cada año.' },
  { comando: 'construir', nombre: 'Construir la base', texto: 'Une los módulos por hogar, apila los años y marca los hogares repetidos.' },
  { comando: 'medir', nombre: 'Medir la pobreza', texto: 'Reproduce la tasa oficial y se detiene si difiere más de 0,3 puntos.' },
  { comando: 'entrenar', nombre: 'Entrenar', texto: 'Ajusta los cinco modelos en cada pliegue, calibra y elige el umbral.' },
  { comando: 'evaluar', nombre: 'Evaluar', texto: 'Calcula métricas, errores por departamento y valores SHAP.' },
  { comando: 'reportar', nombre: 'Reportar', texto: 'Escribe tablas en Word, figuras y los datos de esta web.' },
];

/** Método: pipeline, validación temporal, hogares repetidos, fuga de datos y catálogo. */
@Component({
  selector: 'app-metodo',
  imports: [PlieguesComponent, FiguraComponent, TablaComponent],
  templateUrl: './metodo.page.html',
  styleUrl: './metodo.page.css',
})
export class MetodoPage {
  private readonly d = inject(DatosService).datos;
  readonly etapas = ETAPAS;
  readonly metodo = computed(() => this.d()!.metodologia);
  readonly anios = computed(() => this.d()!.meta.anios);

  readonly columnasPanel: Columna<FilaPanel>[] = [
    { titulo: 'Año', valor: (f) => f.anio },
    { titulo: 'Hogares', valor: (f) => entero(f.hogares), numerica: true },
    { titulo: 'Pregunta PANEL = Sí', valor: (f) => entero(f.pregunta_panel), numerica: true },
    { titulo: 'Misma llave el año anterior', valor: (f) => entero(f.llave_anio_anterior), numerica: true },
    { titulo: 'Repetidos', valor: (f) => entero(f.repetidos), numerica: true },
    { titulo: '% repetidos', valor: (f) => porcentaje(f.pct_repetidos), numerica: true },
  ];

  readonly columnasFuga: Columna<FilaFuga>[] = [
    { titulo: 'Variable', valor: (f) => f.nombre.toUpperCase() },
    { titulo: 'Por qué se excluye', valor: (f) => f.motivo },
  ];

  readonly grupos = computed(() => [...new Set(this.metodo().variables.map((v) => v.Grupo))]);
  readonly grupo = signal('todos');
  readonly busqueda = signal('');
  readonly variables = computed(() => {
    const texto = this.busqueda().trim().toLowerCase();
    return this.metodo().variables.filter((v) =>
      (this.grupo() === 'todos' || v.Grupo === this.grupo()) &&
      (!texto || `${v.Etiqueta} ${v.Variable} ${v.Definición} ${v.Teoría}`.toLowerCase().includes(texto)));
  });
  readonly columnasVariables: Columna<VariableCatalogo>[] = [
    { titulo: 'Variable', valor: (f) => f.Etiqueta },
    { titulo: 'Definición', valor: (f) => f.Definición },
    { titulo: 'Módulo', valor: (f) => f['Módulo ENAHO'] },
    { titulo: 'Teoría', valor: (f) => f.Teoría },
    { titulo: 'Signo esperado', valor: (f) => f['Signo esperado'], numerica: true },
  ];

  leer(evento: Event): string { return (evento.target as HTMLInputElement | HTMLSelectElement).value; }
}
