import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ChartData, ChartOptions } from 'chart.js';

import { FuelData, FuelType } from '../../../core/models';
import { FuelDataService } from '../../../core/services/fuel-data.service';
import { StationContextService } from '../../../core/services/station-context.service';

@Component({
  selector: 'app-history-tab',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent implements OnInit, OnDestroy {
  readonly fuelTypes: FuelType[] = ['Gasoil50', 'SansPlomb'];

  rows: FuelData[] = [];
  fuelType: FuelType = 'Gasoil50';
  loading = false;
  error?: string;

  minStock = 0;
  maxStock = 0;
  recordCount = 0;
  avgStock = 0;

  // Chart data
  stockChartData: ChartData<'line'> = { labels: [], datasets: [] };
  stockChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      y: {
        title: { display: true, text: 'Stock (L)' },
        ticks: { callback: (v) => `${v}L` }
      }
    }
  };

  priceChartData: ChartData<'line'> = { labels: [], datasets: [] };
  priceChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      y: {
        title: { display: true, text: 'Price (TND)' },
        ticks: { callback: (v) => `${v} TND` }
      }
    }
  };

  salesChartData: ChartData<'bar'> = { labels: [], datasets: [] };
  salesChartOptions: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top' }
    },
    scales: {
      y: {
        title: { display: true, text: 'Sales (L / 5 min)' },
        ticks: { callback: (v) => `${v}L` }
      }
    }
  };

  capacityChartData: ChartData<'line'> = { labels: [], datasets: [] };
  capacityChartOptions: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { position: 'top' },
      tooltip: { mode: 'index', intersect: false }
    },
    scales: {
      y: {
        title: { display: true, text: 'Liters' },
        ticks: { callback: (v) => `${v}L` }
      }
    }
  };

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly fuelDataService: FuelDataService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.selectedStation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(() => this.reload());
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onFuelTypeChange(fuelType: FuelType): void {
    this.fuelType = fuelType;
    this.reload();
  }

  reload(): void {
    const stationId = this.stationContext.currentSelectedStation;
    if (!stationId) {
      return;
    }
    this.loading = true;
    this.error = undefined;
    this.fuelDataService.getHistory(stationId, this.fuelType).subscribe({
      next: data => {
        this.rows = data ?? [];
        this.summarize();
        this.buildCharts();
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load history data.';
        this.loading = false;
      }
    });
  }

  private summarize(): void {
    this.recordCount = this.rows.length;
    if (this.recordCount === 0) {
      this.minStock = this.maxStock = this.avgStock = 0;
      return;
    }
    let min = Infinity;
    let max = -Infinity;
    let sum = 0;
    for (const row of this.rows) {
      if (row.stock_liters < min) { min = row.stock_liters; }
      if (row.stock_liters > max) { max = row.stock_liters; }
      sum += row.stock_liters;
    }
    this.minStock = min;
    this.maxStock = max;
    this.avgStock = Math.round(sum / this.recordCount);
  }

  private buildCharts(): void {
    const labels = this.rows.map(r => {
      const date = new Date(r.timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    });

    const stockData = this.rows.map(r => r.stock_liters);
    const priceData = this.rows.map(r => r.price_tnd);
    const salesData = this.rows.map(r => r.sales_last_5min_liters);
    const capacityData = this.rows.map(r => r.capacity_liters);

    // Stock Level Chart
    this.stockChartData = {
      labels,
      datasets: [
        {
          label: 'Stock Level',
          data: stockData,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 3,
          pointBackgroundColor: '#2563eb'
        }
      ]
    };

    // Price Trend Chart
    this.priceChartData = {
      labels,
      datasets: [
        {
          label: 'Price (TND)',
          data: priceData,
          borderColor: '#7c3aed',
          backgroundColor: 'rgba(124, 58, 237, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 3,
          pointBackgroundColor: '#7c3aed'
        }
      ]
    };

    // Sales Activity Chart
    this.salesChartData = {
      labels,
      datasets: [
        {
          label: 'Sales (L / 5 min)',
          data: salesData,
          backgroundColor: '#06b6d4',
          borderColor: '#0891b2',
          borderWidth: 1
        }
      ]
    };

    // Capacity vs Stock Chart
    this.capacityChartData = {
      labels,
      datasets: [
        {
          label: 'Capacity',
          data: capacityData,
          borderColor: '#ec4899',
          backgroundColor: 'rgba(236, 72, 153, 0.05)',
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          borderWidth: 2
        },
        {
          label: 'Current Stock',
          data: stockData,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.05)',
          tension: 0.4,
          fill: true,
          pointRadius: 2,
          borderWidth: 2
        }
      ]
    };
  }
}
