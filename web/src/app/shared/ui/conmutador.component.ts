import { Component, input, model } from '@angular/core';

export interface Opcion<T> { valor: T; nombre: string }

/** Grupo de botones excluyentes (por ejemplo, nivel de pobreza o error del modelo). */
@Component({
  selector: 'app-conmutador',
  template: `
    <div class="conmutador" role="group" [attr.aria-label]="etiqueta()">
      @for (o of opciones(); track o.valor) {
        <button type="button" [attr.aria-pressed]="valor() === o.valor" (click)="valor.set(o.valor)">{{ o.nombre }}</button>
      }
    </div>
  `,
  styles: `
    .conmutador { display: inline-flex; border: 1px solid var(--linea); border-radius: var(--radio); overflow: hidden; }
    button { background: none; border: 0; padding: 0.35rem 0.85rem; font-size: var(--t-0); color: var(--tinta-2); cursor: pointer; white-space: nowrap; }
    button + button { border-left: 1px solid var(--linea); }
    button[aria-pressed='true'] { background: var(--tinta); color: var(--papel); }
  `,
})
export class ConmutadorComponent<T> {
  readonly opciones = input.required<Opcion<T>[]>();
  readonly etiqueta = input('Opciones');
  readonly valor = model.required<T>();
}
