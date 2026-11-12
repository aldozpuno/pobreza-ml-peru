import { DestroyRef, ElementRef, Signal, afterNextRender, inject, signal } from '@angular/core';

/**
 * Ancho en píxeles del elemento anfitrión, actualizado al redimensionar.
 * Los gráficos dibujan en píxeles reales (no con viewBox escalado) para que
 * el texto conserve su tamaño en el móvil.
 */
export function anchoDelAnfitrion(inicial = 640): Signal<number> {
  const elemento = inject(ElementRef<HTMLElement>);
  const destruir = inject(DestroyRef);
  const ancho = signal(inicial);

  afterNextRender(() => {
    const nodo = elemento.nativeElement as HTMLElement;
    const medir = () => ancho.set(Math.max(240, Math.floor(nodo.getBoundingClientRect().width)));
    medir();
    const observador = new ResizeObserver(medir);
    observador.observe(nodo);
    destruir.onDestroy(() => observador.disconnect());
  });
  return ancho.asReadonly();
}
