import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { MultiStationComponent } from './multi-station.component';

const routes: Routes = [
  { path: '', component: MultiStationComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MultiStationRoutingModule {}
