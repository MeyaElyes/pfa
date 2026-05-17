import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';

import { Station } from '../models';

/**
 * Shared state for which station(s) the user is currently inspecting.
 * Feature components subscribe to these observables instead of passing
 * state around through @Input/@Output chains.
 */
@Injectable({ providedIn: 'root' })
export class StationContextService {
  private readonly stationsSubject = new BehaviorSubject<Station[]>([]);
  private readonly selectedStationSubject = new BehaviorSubject<string>('BI00001');
  private readonly selectedStationsSubject = new BehaviorSubject<string[]>(['BI00001']);

  readonly stations$: Observable<Station[]> = this.stationsSubject.asObservable();
  readonly selectedStation$: Observable<string> = this.selectedStationSubject.asObservable();
  readonly selectedStations$: Observable<string[]> = this.selectedStationsSubject.asObservable();

  setStations(stations: Station[]): void {
    this.stationsSubject.next(stations);
    if (stations.length > 0 && !stations.find(s => s.station_id === this.selectedStationSubject.value)) {
      this.setSelectedStation(stations[0].station_id);
    }
    if (this.selectedStationsSubject.value.length === 0 && stations.length > 0) {
      this.setSelectedStations(stations.slice(0, Math.min(3, stations.length)).map(s => s.station_id));
    }
  }

  setSelectedStation(stationId: string): void {
    this.selectedStationSubject.next(stationId);
  }

  setSelectedStations(stationIds: string[]): void {
    this.selectedStationsSubject.next(stationIds);
  }

  get currentStations(): Station[] {
    return this.stationsSubject.value;
  }

  get currentSelectedStation(): string {
    return this.selectedStationSubject.value;
  }

  get currentSelectedStations(): string[] {
    return this.selectedStationsSubject.value;
  }
}
