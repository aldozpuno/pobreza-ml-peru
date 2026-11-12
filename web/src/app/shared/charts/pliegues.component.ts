import { Component, computed, input } from '@angular/core';

interface Pliegue { Pliegue: string; Entrenamiento: string; Calibración: number; Evaluación: number }
type Uso = 'entrena' | 'calibra' | 'evalua' | null;

/** Esquema de la validación temporal: qué hace cada año en cada pliegue. */
@Component({
  selector: 'app-pliegues',
  template: `
    <div class="tabla-envoltura">
      <table class="esquema">
        <thead><tr><th></th>@for (a of anios(); track a) { <th scope="col">{{ a }}</th> }</tr></thead>
        <tbody>
          @for (f of filas(); track f.nombre) {
            <tr>
              <th scope="row">{{ f.nombre }}</th>
              @for (u of f.usos; track $index) {
                <td><span [class]="'uso ' + (u ?? 'nada')" [attr.title]="titulo(u)"></span></td>
              }
            </tr>
          }
        </tbody>
      </table>
    </div>
    <ul class="leyenda">
      <li><i class="uso entrena"></i>Entrena</li>
      <li><i class="uso calibra"></i>Calibra y elige el umbral</li>
      <li><i class="uso evalua"></i>Evalúa</li>
    </ul>
  `,
  styles: `
    .esquema { border-collapse: separate; border-spacing: 4px; font-size: var(--t-0); }
    th { font-weight: 500; color: var(--tinta-3); text-align: center; padding: 0 0.2rem; }
    th[scope='row'] { text-align: left; color: var(--tinta-2); padding-right: 0.8rem; white-space: nowrap; }
    td { padding: 0; }
    .uso { display: block; width: 3.2rem; height: 1.4rem; border-radius: 2px; }
    .entrena { background: var(--indigo); }
    .calibra { background: repeating-linear-gradient(135deg, var(--neutro) 0 3px, transparent 3px 6px); border: 1px solid var(--neutro); }
    .evalua { background: var(--cochinilla); }
    .nada { background: var(--linea-suave); }
    .leyenda { list-style: none; display: flex; flex-wrap: wrap; gap: 0.4rem 1.3rem; padding: 0; margin: 0.8rem 0 0; font-size: var(--t-0); color: var(--tinta-2); }
    .leyenda i { display: inline-block; width: 1.1rem; height: 0.8rem; margin-right: 0.4rem; vertical-align: -1px; }
    @media (max-width: 600px) { .uso { width: 1.9rem; } }
  `,
})
export class PlieguesComponent {
  readonly pliegues = input.required<Pliegue[]>();
  readonly anios = input.required<number[]>();

  readonly filas = computed(() => this.pliegues().map((p) => {
    const [desde, hasta] = p.Entrenamiento.split('–').map(Number);
    const nombre = p.Pliegue.startsWith('Prueba') ? 'Prueba final' : p.Pliegue;
    const usos: Uso[] = this.anios().map((a) =>
      a >= desde && a <= (hasta || desde) ? 'entrena' : a === p.Calibración ? 'calibra' : a === p.Evaluación ? 'evalua' : null);
    return { nombre, usos };
  }));

  titulo(u: Uso): string {
    return u ? { entrena: 'Entrena', calibra: 'Calibra', evalua: 'Evalúa' }[u] : 'No se usa';
  }
}
