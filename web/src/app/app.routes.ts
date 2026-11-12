import { Routes } from '@angular/router';

/** Una página por pregunta de la tesis; cada una se carga solo cuando se visita. */
export const routes: Routes = [
  { path: '', title: 'Pobreza monetaria en el Perú',
    loadComponent: () => import('./pages/panorama/panorama.page').then((m) => m.PanoramaPage) },
  { path: 'territorio', title: 'Territorio | Pobreza monetaria en el Perú',
    loadComponent: () => import('./pages/territorio/territorio.page').then((m) => m.TerritorioPage) },
  { path: 'modelo', title: 'Modelo | Pobreza monetaria en el Perú',
    loadComponent: () => import('./pages/modelo/modelo.page').then((m) => m.ModeloPage) },
  { path: 'variables', title: 'Variables | Pobreza monetaria en el Perú',
    loadComponent: () => import('./pages/variables/variables.page').then((m) => m.VariablesPage) },
  { path: 'metodo', title: 'Método | Pobreza monetaria en el Perú',
    loadComponent: () => import('./pages/metodo/metodo.page').then((m) => m.MetodoPage) },
  { path: '**', redirectTo: '' },
];
