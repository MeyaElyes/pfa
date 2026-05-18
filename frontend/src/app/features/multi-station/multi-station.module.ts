import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { MultiStationRoutingModule } from './multi-station-routing.module';
import { MultiStationComponent } from './multi-station.component';

@NgModule({
  declarations: [MultiStationComponent],
  imports: [SharedModule, MultiStationRoutingModule]
})
export class MultiStationModule {}
