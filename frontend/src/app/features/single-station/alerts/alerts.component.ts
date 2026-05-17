import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';

import { FuelAlert } from '../../../core/models';
import { AlertService } from '../../../core/services/alert.service';
import { StationContextService } from '../../../core/services/station-context.service';

@Component({
  selector: 'app-alerts-tab',
  templateUrl: './alerts.component.html',
  styleUrls: ['./alerts.component.css']
})
export class AlertsComponent implements OnInit, OnDestroy {
  alerts: FuelAlert[] = [];
  loading = false;
  error?: string;

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly alertService: AlertService,
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
    this.alertService.getAlerts(stationId, 100).subscribe({
      next: data => {
        this.alerts = (data ?? []).sort(
          (a, b) => (b.timestamp || '').localeCompare(a.timestamp || '')
        );
        this.loading = false;
      },
      error: () => {
        this.error = 'Unable to load alerts.';
        this.loading = false;
      }
    });
  }
}
