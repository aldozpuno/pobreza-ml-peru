import { Component, computed, inject, signal } from '@angular/core';

import { DatosService } from '../../core/datos.service';
import { decimal } from '../../core/formato';
import { ImportanciaShap } from '../../core/models';
import { BarrasComponent, FilaBarra } from '../../shared/charts/barras.component';
import { FilaPesas, PesasComponent } from '../../shared/charts/pesas.component';
import { FiguraComponent } from '../../shared/ui/figura.component';
import { Columna, TablaComponent } from '../../shared/ui/tabla.component';

type FilaTeoria = { teoria: string; variables: string; coinciden: string };

const tieneSigno = (v: ImportanciaShap) => v.signo_esperado === '+' || v.signo_esperado === '-';
const coincide = (v: ImportanciaShap) => tieneSigno(v) && v.signo_observado === v.signo_esperado;

/** Explicabilidad: importancia SHAP, concordancia con la teoría y cambio con la pandemia. */
@Component({
  selector: 'app-variables',
  imports: [BarrasComponent, PesasComponent, FiguraComponent, TablaComponent],
  templateUrl: './variables.page.html',
  styleUrl: './variables.page.css',
})
export class VariablesPage {
  private readonly d = inject(DatosService).datos;
  readonly decimal = decimal;
  readonly todas = signal(false);

  readonly anioPrueba = computed(() => this.d()!.meta.anio_prueba);
  readonly importancia = computed(() => this.d()!.explicabilidad.importancia);
  readonly conSigno = computed(() => this.importancia().filter(tieneSigno));
  readonly concordantes = computed(() => this.conSigno().filter(coincide));
  readonly discordantes = computed(() => this.conSigno().filter((v) => !coincide(v)).slice(0, 4));

  readonly barras = computed<FilaBarra[]>(() =>
    this.importancia().slice(0, this.todas() ? undefined : 15).map((v) => ({
      clave: v.variable,
      etiqueta: v.etiqueta,
      detalle: v.teoria ?? undefined,
      valor: v.importancia,
      tono: v.signo_observado === '+' ? 'cochinilla' : v.signo_observado === '-' ? 'indigo' : 'neutro',
      nota: !tieneSigno(v) ? 'Sin signo esperado' : coincide(v) ? 'Coincide' : `No coincide (esperado ${v.signo_esperado})`,
    })));

  readonly teorias = computed<FilaTeoria[]>(() =>
    this.d()!.metodologia.puente.map((p) => {
      const variables = this.importancia().filter((v) => v.teoria === p.Teoría && tieneSigno(v));
      return { teoria: p.Teoría, variables: p.Variables,
               coinciden: variables.length ? `${variables.filter(coincide).length} de ${variables.length}` : '—' };
    }));
  readonly columnasTeoria: Columna<FilaTeoria>[] = [
    { titulo: 'Teoría', valor: (f) => f.teoria },
    { titulo: 'Variables del modelo', valor: (f) => f.variables },
    { titulo: 'Signo como predice', valor: (f) => f.coinciden, numerica: true },
  ];

  readonly periodos = computed<FilaPesas[]>(() =>
    [...this.d()!.explicabilidad.periodos]
      .sort((a, b) => b.importancia_despues - a.importancia_despues).slice(0, 14)
      .map((p) => ({ clave: p.variable, etiqueta: p.etiqueta, a: p.importancia_antes, b: p.importancia_despues })));
  readonly mayorCambio = computed(() =>
    [...this.d()!.explicabilidad.periodos].sort((a, b) => Math.abs(b.cambio) - Math.abs(a.cambio))[0]);

  readonly formatoShap = (v: number) => decimal(v, 2);
  readonly formatoCambio = (v: number) => (v > 0 ? '+' : '') + decimal(v, 2);
}
