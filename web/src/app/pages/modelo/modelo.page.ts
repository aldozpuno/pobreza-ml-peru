import { Component, computed, inject } from '@angular/core';

import { DatosService } from '../../core/datos.service';
import { decimal, entero, porcentaje, proporcion } from '../../core/formato';
import { Metricas, MetricasEstimador } from '../../core/models';
import { LineasComponent, Serie } from '../../shared/charts/lineas.component';
import { MatrizComponent } from '../../shared/charts/matriz.component';
import { FiguraComponent } from '../../shared/ui/figura.component';
import { Columna, TablaComponent } from '../../shared/ui/tabla.component';

export const NOMBRES: Record<string, string> = {
  xgboost: 'XGBoost', random_forest: 'Bosque aleatorio', probit: 'Probit', logit: 'Regresión logística', knn: 'KNN',
  xgboost_sin_alquiler: 'XGBoost sin alquiler estimado (P106)',
};

const tres = (v: number) => decimal(v, 3);

/** Desempeño del modelo: comparación, estabilidad por año, prueba, errores y calibración. */
@Component({
  selector: 'app-modelo',
  imports: [LineasComponent, MatrizComponent, FiguraComponent, TablaComponent],
  templateUrl: './modelo.page.html',
  styleUrl: './modelo.page.css',
})
export class ModeloPage {
  private readonly d = inject(DatosService).datos;
  readonly decimal = decimal;
  readonly porcentaje = porcentaje;
  readonly proporcion = proporcion;
  readonly NOMBRES = NOMBRES;

  readonly meta = computed(() => this.d()!.meta);
  readonly modelo = computed(() => this.d()!.modelo);
  readonly principal = computed(() => this.meta().estimador);
  readonly comparacion = computed(() => [...this.modelo().comparacion].sort((a, b) => b.auc_roc - a.auc_roc));
  readonly mejor = computed(() => this.comparacion()[0]);
  readonly segundo = computed(() => this.comparacion()[1]);
  readonly prueba = computed(() => this.modelo().prueba[0]);
  readonly sinAlquiler = computed(() => this.modelo().sensibilidad.find((s) => s.estimador.endsWith('sin_alquiler')));

  readonly columnasComparacion: Columna<MetricasEstimador>[] = [
    { titulo: 'Modelo', valor: (f) => NOMBRES[f.estimador] ?? f.estimador },
    { titulo: 'AUC-ROC', valor: (f) => tres(f.auc_roc), numerica: true },
    { titulo: 'AUC-PR', valor: (f) => tres(f.auc_pr), numerica: true },
    { titulo: 'Brier', valor: (f) => tres(f.brier), numerica: true },
    { titulo: 'Exhaustividad', valor: (f) => tres(f.recall), numerica: true },
    { titulo: 'Precisión', valor: (f) => tres(f.precision), numerica: true },
    { titulo: 'F1', valor: (f) => tres(f.f1), numerica: true },
  ];
  readonly esPrincipal = (f: MetricasEstimador) => f.estimador === this.principal();

  /** AUC del modelo principal en cada año de evaluación. */
  readonly porAnio = computed<Serie[]>(() => {
    const evaluacion = new Map(this.d()!.metodologia.pliegues.map((p) => [p.Pliegue, p.Evaluación]));
    const filas = this.modelo().pliegues.filter((p) => p.estimador === this.principal())
      .map((p) => ({ anio: evaluacion.get(p.pliegue ?? '') ?? this.meta().anio_prueba, p }));
    return [
      { id: 'roc', nombre: 'AUC-ROC', color: 'var(--indigo)', marcas: true, puntos: filas.map((f) => ({ x: f.anio, y: f.p.auc_roc })) },
      { id: 'pr', nombre: 'AUC-PR', color: 'var(--cochinilla)', marcas: true, puntos: filas.map((f) => ({ x: f.anio, y: f.p.auc_pr })) },
    ];
  });

  readonly aniosEvaluacion = computed(() => this.porAnio()[0].puntos.map((p) => p.x));

  readonly columnasPrueba: Columna<Metricas & { Variante: string }>[] = [
    { titulo: 'Hogares evaluados', valor: (f) => f.Variante },
    { titulo: 'Hogares', valor: (f) => entero(f.hogares), numerica: true },
    { titulo: 'AUC-ROC', valor: (f) => tres(f.auc_roc), numerica: true },
    { titulo: 'AUC-PR', valor: (f) => tres(f.auc_pr), numerica: true },
    { titulo: 'Exhaustividad', valor: (f) => tres(f.recall), numerica: true },
    { titulo: 'Precisión', valor: (f) => tres(f.precision), numerica: true },
    { titulo: 'Pobreza estimada', valor: (f) => porcentaje(f.tasa_predicha), numerica: true },
  ];

  readonly roc = computed<Serie[]>(() => [{ id: 'roc', nombre: 'Curva ROC', color: 'var(--indigo)',
    puntos: this.modelo().roc.map((p) => ({ x: p.fpr, y: p.tpr })) }]);
  readonly pr = computed<Serie[]>(() => [{ id: 'pr', nombre: 'Precisión–exhaustividad', color: 'var(--indigo)',
    puntos: [...this.modelo().pr].sort((a, b) => a.recall - b.recall).map((p) => ({ x: p.recall, y: p.precision })) }]);
  readonly calibracion = computed<Serie[]>(() => [{ id: 'cal', nombre: 'Proporción observada', color: 'var(--cochinilla)', marcas: true,
    puntos: this.modelo().calibracion.map((p) => ({ x: p.prob_media, y: p.observado })) }]);

  readonly columnasSensibilidad: Columna<MetricasEstimador>[] = [
    { titulo: 'Modelo', valor: (f) => NOMBRES[f.estimador] ?? f.estimador },
    { titulo: 'AUC-ROC', valor: (f) => tres(f.auc_roc), numerica: true },
    { titulo: 'AUC-PR', valor: (f) => tres(f.auc_pr), numerica: true },
    { titulo: 'Exhaustividad', valor: (f) => tres(f.recall), numerica: true },
    { titulo: 'Precisión', valor: (f) => tres(f.precision), numerica: true },
  ];

  readonly anio = (v: number) => String(v);
  readonly dosDecimales = (v: number) => decimal(v, 2);
  readonly unDecimal = (v: number) => decimal(v, 1);
}
