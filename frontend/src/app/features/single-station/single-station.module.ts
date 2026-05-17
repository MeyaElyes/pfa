import { NgModule } from '@angular/core';

import { SharedModule } from '../../shared/shared.module';
import { AlertsComponent } from './alerts/alerts.component';
import { ChatComponent } from './chat/chat.component';
import { ForecastComponent } from './forecast/forecast.component';
import { HistoryComponent } from './history/history.component';
import { OverviewComponent } from './overview/overview.component';
import { SingleStationRoutingModule } from './single-station-routing.module';
import { SingleStationComponent } from './single-station.component';

@NgModule({
  declarations: [
    SingleStationComponent,
    OverviewComponent,
    HistoryComponent,
    AlertsComponent,
    ForecastComponent,
    ChatComponent
  ],
  imports: [SharedModule, SingleStationRoutingModule]
})
export class SingleStationModule {}
