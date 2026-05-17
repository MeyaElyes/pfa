import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { FuelAlert } from '../models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class AlertService {
  constructor(private readonly api: ApiService) {}

  getAlerts(stationId?: string, limit = 50): Observable<FuelAlert[]> {
    return this.api.get<FuelAlert[]>('/alerts', {
      station_id: stationId,
      limit
    });
  }
}
