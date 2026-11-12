// Contrato de datos con el pipeline de Python (src/pobreza/reporting/dashboard_export.py).
// Si cambia un campo allá, debe cambiar aquí.

export interface Meta {
  generado: string;
  origen: "enaho" | "sintetico";
  version: string;
  anios: number[];
  anio_prueba: number;
  estimador: string;
  umbral: number;
  pliegue_final: string;
}

export interface IncidenciaAnual {
  anio: number;
  hogares_muestra: number;
  poblacion_expandida: number;
  tasa_personas: number;
  tasa_hogares: number;
  tasa_muestral: number;
  tasa_oficial_inei: number | null;
  diferencia_pp: number | null;
}

export interface IncidenciaArea { anio: number; rural: number; tasa_personas: number }

export interface Resumen {
  kpis: {
    tasa_reproducida: number;
    tasa_oficial: number | null;
    tasa_predicha: number;
    tasa_clasificados: number;
    auc_roc: number;
    auc_pr: number;
    recall: number;
    precision: number;
    hogares_total: number;
    pct_repetidos: number;
  };
  serie_anual: IncidenciaAnual[];
  serie_area: IncidenciaArea[];
}

export interface IncidenciaDepartamento {
  anio: number;
  departamento: string;
  nombre: string;
  tasa_personas: number;
  hogares_muestra: number;
}

export interface SesgoDepartamento {
  codigo: string;
  departamento: string;
  hogares: number;
  tasa_observada: number;
  tasa_predicha: number;
  tasa_clasificados: number;
  sesgo_pp: number;
}

export interface Territorio { incidencia: IncidenciaDepartamento[]; sesgo_prueba: SesgoDepartamento[] }

export interface Metricas {
  hogares: number;
  auc_roc: number;
  auc_pr: number;
  brier: number;
  f1: number;
  precision: number;
  recall: number;
  exactitud: number;
  tasa_real: number;
  tasa_predicha: number;
  tasa_clasificados: number;
  falsos_negativos: number;
  falsos_positivos: number;
}

export type MetricasEstimador = Metricas & { estimador: string; pliegue?: string };

export interface Modelo {
  comparacion: MetricasEstimador[];
  pliegues: MetricasEstimador[];
  prueba: (Metricas & { Variante: string })[];
  sensibilidad: MetricasEstimador[];
  confusion: { Celda: string; Hogares: number; "Personas expandidas": number }[];
  calibracion: { grupo: number; prob_media: number; observado: number; hogares: number }[];
  roc: { fpr: number; tpr: number }[];
  pr: { recall: number; precision: number }[];
  sesgo_regional: Record<string, number>;
}

export interface ImportanciaShap {
  variable: string;
  etiqueta: string;
  importancia: number;
  direccion: number | null;
  signo_observado: "+" | "-" | "±";
  signo_esperado: string | null;
  definicion: string | null;
  teoria: string | null;
}

export interface Explicabilidad {
  importancia: ImportanciaShap[];
  periodos: { variable: string; etiqueta: string; importancia_antes: number; importancia_despues: number; cambio: number }[];
  muestra: { variable: string; etiqueta: string; shap: number; valor: number | null }[];
}

export interface VariableCatalogo {
  Variable: string;
  Etiqueta: string;
  "Módulo ENAHO": string;
  Grupo: string;
  Definición: string;
  Teoría: string;
  "Signo esperado": string;
}

export interface Metodologia {
  pliegues: { Pliegue: string; Entrenamiento: string; Calibración: number; Evaluación: number }[];
  variables: VariableCatalogo[];
  puente: { Teoría: string; Variables: string; Cantidad: number }[];
  fuga: { nombre: string; motivo: string }[];
  panel: { anio: number; hogares: number; pregunta_panel: number; llave_anio_anterior: number; repetidos: number; pct_repetidos: number }[];
  vif: { Variable: string; VIF: number; Diagnóstico: string }[];
}

export interface DatosTablero {
  meta: Meta;
  resumen: Resumen;
  territorio: Territorio;
  modelo: Modelo;
  explicabilidad: Explicabilidad;
  metodologia: Metodologia;
}
