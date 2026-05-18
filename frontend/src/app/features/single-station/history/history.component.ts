import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';

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
      this.minStock = this.maxStock = 0;
      return;
    }
    let min = Infinity;
    let max = -Infinity;
    for (const row of this.rows) {
      if (row.stock_liters < min) { min = row.stock_liters; }
      if (row.stock_liters > max) { max = row.stock_liters; }
    }
    this.minStock = min;
    this.maxStock = max;
  }
}
