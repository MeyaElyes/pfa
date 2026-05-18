import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ChartData, ChartOptions } from 'chart.js';

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
  narrative = '';

  rows: ForecastPoint[] = [];
  loading = false;
  error?: string;

  chartData: ChartData<'line'> = { labels: [], datasets: [] };
  chartOptions: ChartOptions<'line'> = {
    responsive: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      x: { ticks: { maxTicksLimit: 8 } },
      y: {
        title: { display: true, text: 'Stock (Liters)' },
        ticks: { callback: (v) => `${v}L` }
      }
    }
  };

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
    if (!this.stationId) return;
    this.loading = true;
    this.error = undefined;
    this.narrative = '';

    this.forecastService.getPredictionsWithNarrative(this.stationId, this.fuelType, this.periods).subscribe({
      next: data => {
        this.rows = data.forecast ?? [];
        this.narrative = data.narrative ?? '';
        this.buildChart();
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to generate forecast.';
        this.loading = false;
      }
    });
  }

  private buildChart(): void {
    const labels = this.rows.map(r => r.ds.substring(11, 16)); // HH:MM
    this.chartData = {
      labels,
      datasets: [
        {
          label: 'Predicted Stock',
          data: this.rows.map(r => r.yhat),
          borderColor: '#0066cc',
          backgroundColor: 'rgba(0,102,204,0.1)',
          fill: true,
          tension: 0.4
        },
        {
          label: 'Upper Bound',
          data: this.rows.map(r => r.yhat_upper),
          borderColor: 'rgba(0,180,0,0.5)',
          borderDash: [5, 5],
          fill: false,
          tension: 0.4
        },
        {
          label: 'Lower Bound',
          data: this.rows.map(r => r.yhat_lower),
          borderColor: 'rgba(255,100,0,0.5)',
          borderDash: [5, 5],
          fill: false,
          tension: 0.4
        }
      ]
    };
  }
}