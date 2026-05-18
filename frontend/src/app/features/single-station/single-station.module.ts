import { NgModule } from '@angular/core';
import { NgChartsModule } from 'ng2-charts';

import { SharedModule } from '../../shared/shared.module';
import { AlertsComponent } from './alerts/alerts.component';
import { ChatComponent } from './chat/chat.component';
import { ForecastComponent } from './forecast/forecast.component';
import { HistoryComponent } from './history/history.component';
import { OverviewComponent } from './overview/overview.component';
import { SingleStationRoutingModule } from './single-station-routing.module';
import { SingleStationComponent } from './single-station.component';
import { ReportComponent } from './report/report.component';
import { MarkdownModule } from 'ngx-markdown';

@NgModule({
  declarations: [
    SingleStationComponent,
    OverviewComponent,
    HistoryComponent,
    AlertsComponent,
    ForecastComponent,
    ChatComponent,
    ReportComponent
  ],
  imports: [SharedModule, SingleStationRoutingModule, MarkdownModule.forChild(), NgChartsModule]
})
export class SingleStationModule {}