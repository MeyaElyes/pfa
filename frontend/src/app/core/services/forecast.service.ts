import { Injectable } from '@angular/core';
import { Observable, map } from 'rxjs';
import { ForecastPoint, FuelType } from '../models';
import { ApiService } from './api.service';

export interface ForecastResponse {
  forecast: ForecastPoint[];
  narrative: string;
}

@Injectable({ providedIn: 'root' })
export class ForecastService {
  constructor(private readonly api: ApiService) {}

  getPredictions(stationId: string, fuelType: FuelType, periods = 24): Observable<ForecastPoint[]> {
    return this.api.get<ForecastResponse>('/predict', {
      station_id: stationId,
      fuel_type: fuelType,
      periods
    }).pipe(map(response => response.forecast));
  }

  getPredictionsWithNarrative(stationId: string, fuelType: FuelType, periods = 24): Observable<ForecastResponse> {
    return this.api.get<ForecastResponse>('/predict', {
      station_id: stationId,
      fuel_type: fuelType,
      periods
    });
  }
}