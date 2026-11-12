import { Component, input, signal } from '@angular/core';

/**
 * Marco común de cada figura: título, descripción, el gráfico y su fuente.
 * Si la figura proyecta una tabla (`[tabla]`), ofrece alternar entre gráfico y tabla,
 * de modo que ningún dato dependa solo del color o de pasar el cursor.
 */
@Component({
  selector: 'app-figura',
  template: `
    <figure class="figura">
      <div class="figura__cabeza">
        <div>
          <h3>{{ titulo() }}</h3>
          @if (descripcion()) { <p class="figura__desc">{{ descripcion() }}</p> }
        </div>
        @if (conTabla()) {
          <button type="button" class="figura__alternar" (click)="verTabla.set(!verTabla())" [attr.aria-pressed]="verTabla()">
            {{ verTabla() ? 'Ver gráfico' : 'Ver tabla' }}
          </button>
        }
      </div>
      <div [hidden]="verTabla()"><ng-content select="[grafico]" /><ng-content /></div>
      @if (conTabla()) { <div [hidden]="!verTabla()"><ng-content select="[tabla]" /></div> }
      @if (fuente()) { <figcaption>{{ fuente() }}</figcaption> }
    </figure>
  `,
  styles: `
    .figura { margin: 0; background: var(--papel); border-radius: var(--radio); padding: 1.4rem 1.5rem 1.1rem; }
    .figura__cabeza { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; margin-bottom: 1rem; }
    .figura__desc { color: var(--tinta-3); font-size: var(--t-1); margin: 0.3rem 0 0; }
    .figura__alternar {
      flex: none; background: none; border: 1px solid var(--linea); border-radius: var(--radio);
      padding: 0.3rem 0.7rem; font-size: var(--t-0); color: var(--tinta-2); cursor: pointer;
    }
    .figura__alternar:hover { border-color: var(--tinta-3); color: var(--tinta); }
    figcaption { color: var(--tinta-3); font-size: var(--t-0); margin-top: 0.9rem; max-width: 80ch; }
    @media (max-width: 600px) { .figura { padding: 1.1rem 1rem 0.9rem; } }
  `,
})
export class FiguraComponent {
  readonly titulo = input.required<string>();
  readonly descripcion = input<string>();
  readonly fuente = input<string>('Fuente: INEI, ENAHO. Elaboración propia.');
  readonly conTabla = input(false);
  readonly verTabla = signal(false);
}
