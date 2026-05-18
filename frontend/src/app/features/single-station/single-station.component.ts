import { Component } from '@angular/core';

type Tab = 'overview' | 'history' | 'alerts' | 'forecast' | 'chat' | 'report';

interface TabDef {
  id: Tab;
  label: string;
}

@Component({
  selector: 'app-single-station',
  templateUrl: './single-station.component.html',
  styleUrls: ['./single-station.component.css']
})
export class SingleStationComponent {
  readonly tabs: TabDef[] = [
    { id: 'overview', label: 'Real-Time Overview' },
    { id: 'history',  label: 'Analytics & Trends' },
    { id: 'alerts',   label: 'Incident Log' },
    { id: 'forecast', label: 'AI Forecast' },
    { id: 'chat',     label: 'Station Chat' },
    { id: 'report',   label: '📋 AI Report' }
  ];

  activeTab: Tab = 'overview';

  selectTab(id: Tab): void {
    this.activeTab = id;
  }
}