import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';

import { FuelDataService } from '../../../core/services/fuel-data.service';
import { StationContextService } from '../../../core/services/station-context.service';
import { FuelData } from '../../../core/models';
import { StatusLevel } from '../../../shared/components/status-badge/status-badge.component';

interface OverviewRow extends FuelData {
  utilization: number;
  stockLevel: StatusLevel;
  priceDeviation: number;
  priceCompliant: boolean;
  dailySalesEstimate: number;
}

@Component({
  selector: 'app-overview-tab',
  templateUrl: './overview.component.html',
  styleUrls: ['./overview.component.css']
})
export class OverviewComponent implements OnInit, OnDestroy {
  rows: OverviewRow[] = [];
  loading = false;
  error?: string;

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly fuelDataService: FuelDataService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.selectedStation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(stationId => this.load(stationId));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  refresh(): void {
    this.load(this.stationContext.currentSelectedStation);
  }

  private load(stationId: string): void {
    if (!stationId) {
      return;
    }
    this.loading = true;
    this.error = undefined;
    this.fuelDataService.getCurrent(stationId).subscribe({
      next: data => {
        this.rows = (data ?? []).map(record => this.decorate(record));
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load current station data.';
        this.loading = false;
      }
    });
  }

  private decorate(record: FuelData): OverviewRow {
    const utilization = record.capacity_liters > 0
      ? (record.stock_liters / record.capacity_liters) * 100
      : 0;
    const priceDeviation = record.price_tnd - record.official_price_tnd;
    const priceCompliant = Math.abs(priceDeviation) <= 0.01;
    const stockLevel: StatusLevel = utilization > 20 ? 'ok' : utilization > 10 ? 'warn' : 'critical';

    return {
      ...record,
      utilization,
      stockLevel,
      priceDeviation,
      priceCompliant,
      dailySalesEstimate: record.sales_last_5min_liters * 288
    };
  }
}
