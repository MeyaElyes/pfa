import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';

import { ForecastPoint, FuelType, Station } from '../../../core/models';
import { ForecastService } from '../../../core/services/forecast.service';
import { StationContextService } from '../../../core/services/station-context.service';

@Component({
  selector: 'app-forecast-tab',
  templateUrl: './forecast.component.html',
  styleUrls: ['./forecast.component.css']
})
export class ForecastComponent implements OnInit, OnDestroy {
  readonly fuelTypes: FuelType[] = ['Gasoil50', 'SansPlomb'];
  readonly horizons = [
    { label: '2 hours', value: 24 },
    { label: '4 hours', value: 48 },
    { label: '8 hours', value: 96 }
  ];

  stations: Station[] = [];
  stationId = '';
  fuelType: FuelType = 'Gasoil50';
  periods = 24;

  rows: ForecastPoint[] = [];
  loading = false;
  error?: string;

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly forecastService: ForecastService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.stations$
      .pipe(takeUntil(this.destroy$))
      .subscribe(stations => (this.stations = stations));

    this.stationContext.selectedStation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(id => (this.stationId = id));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  generate(): void {
    if (!this.stationId) {
      return;
    }
    this.loading = true;
    this.error = undefined;
    this.forecastService.getPredictions(this.stationId, this.fuelType, this.periods).subscribe({
      next: data => {
        this.rows = data ?? [];
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to generate forecast.';
        this.loading = false;
      }
    });
  }
}
