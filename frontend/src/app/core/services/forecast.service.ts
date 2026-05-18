import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ForecastPoint, FuelType } from '../models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class ForecastService {
  constructor(private readonly api: ApiService) {}

  getPredictions(stationId: string, fuelType: FuelType, periods = 24): Observable<ForecastPoint[]> {
    return this.api.get<ForecastPoint[]>('/predict', {
      station_id: stationId,
      fuel_type: fuelType,
      periods
    });
  }
}
