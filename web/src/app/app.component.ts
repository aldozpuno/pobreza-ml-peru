import { Component, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { DatosService } from './core/datos.service';

/** Estructura común: cabecera con navegación, contenido de la página y pie con la fuente. */
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  private readonly servicio = inject(DatosService);
  readonly estado = this.servicio.estado;
  readonly sintetico = this.servicio.esSintetico;
  readonly meta = computed(() => this.servicio.datos()?.meta);

  readonly secciones = [
    { ruta: '/', nombre: 'Panorama' },
    { ruta: '/territorio', nombre: 'Territorio' },
    { ruta: '/modelo', nombre: 'Modelo' },
    { ruta: '/variables', nombre: 'Variables' },
    { ruta: '/metodo', nombre: 'Método' },
  ];

  readonly fecha = computed(() => {
    const generado = this.meta()?.generado;
    return generado ? new Date(generado).toLocaleDateString('es-PE', { dateStyle: 'long' }) : '';
  });
}
