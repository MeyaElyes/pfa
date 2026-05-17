import { Component, OnDestroy, OnInit } from '@angular/core';
import { NavigationEnd, Router } from '@angular/router';
import { filter, Subject, takeUntil } from 'rxjs';

import { Station } from './core/models';
import { StationContextService } from './core/services/station-context.service';
import { StationService } from './core/services/station.service';

type ViewMode = 'single' | 'multi';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  readonly title = 'AGIL Fuel Monitor';

  stations: Station[] = [];
  selectedStation = '';
  viewMode: ViewMode = 'single';

  now = new Date();
  backendConnected = true;
  errorMessage = '';

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly router: Router,
    private readonly stationService: StationService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.stations$
      .pipe(takeUntil(this.destroy$))
      .subscribe(stations => (this.stations = stations));

    this.stationContext.selectedStation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(id => (this.selectedStation = id));

    this.router.events
      .pipe(
        filter((event): event is NavigationEnd => event instanceof NavigationEnd),
        takeUntil(this.destroy$)
      )
      .subscribe(event => {
        this.viewMode = event.urlAfterRedirects.startsWith('/multi') ? 'multi' : 'single';
      });

    this.loadStations();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  loadStations(): void {
    this.errorMessage = '';
    this.stationService.getStations().subscribe({
      next: stations => {
        const list = Array.isArray(stations) ? stations : [];
        this.backendConnected = true;
        this.stationContext.setStations(list);
      },
      error: () => {
        this.backendConnected = false;
        this.errorMessage = 'Unable to connect to the backend API.';
      }
    });
  }

  onStationChange(stationId: string): void {
    this.stationContext.setSelectedStation(stationId);
  }

  switchView(mode: ViewMode): void {
    this.viewMode = mode;
    this.router.navigateByUrl(`/${mode}`);
  }

  refresh(): void {
    this.now = new Date();
    this.loadStations();
  }
}
