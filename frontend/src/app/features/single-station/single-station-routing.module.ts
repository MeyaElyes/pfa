import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { SingleStationComponent } from './single-station.component';

const routes: Routes = [
  { path: '', component: SingleStationComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SingleStationRoutingModule {}
