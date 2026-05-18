import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { FuelData, FuelType } from '../models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class FuelDataService {
  constructor(private readonly api: ApiService) {}

  getCurrent(stationId: string): Observable<FuelData[]> {
    return this.api.get<FuelData[]>('/current', { station_id: stationId });
  }

  getHistory(stationId: string, fuelType: FuelType, limit = 500): Observable<FuelData[]> {
    return this.api.get<FuelData[]>('/history', {
      station_id: stationId,
      fuel_type: fuelType,
      limit
    });
  }
}
