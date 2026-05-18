import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'single' },
  {
    path: 'single',
    loadChildren: () =>
      import('./features/single-station/single-station.module').then(m => m.SingleStationModule)
  },
  {
    path: 'multi',
    loadChildren: () =>
      import('./features/multi-station/multi-station.module').then(m => m.MultiStationModule)
  },
  { path: '**', redirectTo: 'single' }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
