import { Component, computed, input } from '@angular/core';

/** Cien marcas finas con las primeras `n` en color: lectura de "n de cada 100". */
@Component({
  selector: 'app-cien',
  template: `
    <span class="cien" role="img" [attr.aria-label]="redondeado() + ' de cada 100'">
      @for (i of marcas; track i) { <i [class.llena]="i < redondeado()"></i> }
    </span>
  `,
  styles: `
    .cien { display: grid; grid-template-columns: repeat(100, 1fr); gap: 1px; height: 22px; width: 100%; }
    i { background: var(--linea); border-radius: 1px; }
    i.llena { background: var(--indigo); }
  `,
})
export class CienComponent {
  readonly valor = input.required<number>(); // proporción 0–1
  readonly marcas = Array.from({ length: 100 }, (_, i) => i);
  readonly redondeado = computed(() => Math.round(this.valor() * 100));
}
