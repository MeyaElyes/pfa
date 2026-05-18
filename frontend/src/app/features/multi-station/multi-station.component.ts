import { Component, OnDestroy, OnInit } from '@angular/core';
import { forkJoin, Subject, takeUntil } from 'rxjs';

import { FuelAlert, FuelData, Station } from '../../core/models';
import { AlertService } from '../../core/services/alert.service';
import { FuelDataService } from '../../core/services/fuel-data.service';
import { StationContextService } from '../../core/services/station-context.service';
import { StatusLevel } from '../../shared/components/status-badge/status-badge.component';

interface StationSummary {
  stationId: string;
  location: string;
  rows: FuelData[];
  totalStock: number;
  totalCapacity: number;
  utilization: number;
  status: StatusLevel;
  statusLabel: string;
}

@Component({
  selector: 'app-multi-station',
  templateUrl: './multi-station.component.html',
  styleUrls: ['./multi-station.component.css']
})
export class MultiStationComponent implements OnInit, OnDestroy {
  stations: Station[] = [];
  selectedIds: string[] = [];
  summaries: StationSummary[] = [];
  flatRows: (FuelData & { utilization: number })[] = [];
  alerts: FuelAlert[] = [];

  loading = false;
  error?: string;

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly fuelDataService: FuelDataService,
    private readonly alertService: AlertService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.stations$
      .pipe(takeUntil(this.destroy$))
      .subscribe(stations => (this.stations = stations));

    this.stationContext.selectedStations$
      .pipe(takeUntil(this.destroy$))
      .subscribe(ids => {
        this.selectedIds = ids;
        this.load();
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  toggleStation(stationId: string, checked: boolean): void {
    const set = new Set(this.selectedIds);
    if (checked) {
      set.add(stationId);
    } else {
      set.delete(stationId);
    }
    this.stationContext.setSelectedStations(Array.from(set));
  }

  isSelected(stationId: string): boolean {
    return this.selectedIds.includes(stationId);
  }

  refresh(): void {
    this.load();
  }

  private load(): void {
    if (this.selectedIds.length === 0) {
      this.summaries = [];
      this.flatRows = [];
      return;
    }
    this.loading = true;
    this.error = undefined;
    const requests = this.selectedIds.map(id => this.fuelDataService.getCurrent(id));

    forkJoin(requests).subscribe({
      next: results => {
        this.summaries = results.map((rows, i) =>
          this.buildSummary(this.selectedIds[i], rows ?? [])
        );
        this.flatRows = results.flatMap((rows, i) =>
          (rows ?? []).map(row => ({
            ...row,
            station_id: row.station_id ?? this.selectedIds[i],
            utilization: row.capacity_liters > 0
              ? (row.stock_liters / row.capacity_liters) * 100
              : 0
          }))
        );
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load multi-station data.';
        this.loading = false;
      }
    });

    this.alertService.getAlerts(undefined, 100).subscribe({
      next: alerts => {
        const selected = new Set(this.selectedIds);
        this.alerts = (alerts ?? [])
          .filter(a => !a.station_id || selected.has(a.station_id))
          .sort((a, b) => (b.timestamp || '').localeCompare(a.timestamp || ''))
          .slice(0, 50);
      },
      error: () => { /* non-fatal */ }
    });
  }

  private buildSummary(stationId: string, rows: FuelData[]): StationSummary {
    const totalStock = rows.reduce((s, r) => s + (r.stock_liters || 0), 0);
    const totalCapacity = rows.reduce((s, r) => s + (r.capacity_liters || 0), 0);
    const utilization = totalCapacity > 0 ? (totalStock / totalCapacity) * 100 : 0;
    const status: StatusLevel = utilization > 20 ? 'ok' : utilization > 10 ? 'warn' : 'critical';
    const statusLabel = status === 'ok' ? 'Healthy' : status === 'warn' ? 'Low stock' : 'Critical';
    const station = this.stations.find(s => s.station_id === stationId);

    return {
      stationId,
      location: station?.location ?? '',
      rows,
      totalStock,
      totalCapacity,
      utilization,
      status,
      statusLabel
    };
  }
}
