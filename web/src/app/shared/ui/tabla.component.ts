import { Component, input } from '@angular/core';

export interface Columna<T> {
  titulo: string;
  valor: (fila: T) => string | number | null;
  numerica?: boolean;
}

/** Tabla de datos genérica: columnas declarativas, números alineados a la derecha. */
@Component({
  selector: 'app-tabla',
  template: `
    <div class="tabla-envoltura">
      <table class="datos">
        @if (leyenda()) { <caption>{{ leyenda() }}</caption> }
        <thead>
          <tr>@for (c of columnas(); track c.titulo) { <th scope="col" [class.num]="c.numerica">{{ c.titulo }}</th> }</tr>
        </thead>
        <tbody>
          @for (fila of filas(); track $index) {
            <tr [class.destacada]="destacar()(fila)">
              @for (c of columnas(); track c.titulo) { <td [class.num]="c.numerica">{{ c.valor(fila) }}</td> }
            </tr>
          }
        </tbody>
      </table>
    </div>
  `,
})
export class TablaComponent<T> {
  readonly columnas = input.required<Columna<T>[]>();
  readonly filas = input.required<T[]>();
  readonly leyenda = input<string>();
  readonly destacar = input<(fila: T) => boolean>(() => false);
}
