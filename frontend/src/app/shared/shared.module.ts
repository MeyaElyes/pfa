import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { EmptyStateComponent } from './components/empty-state/empty-state.component';
import { LoadingSpinnerComponent } from './components/loading-spinner/loading-spinner.component';
import { ProgressBarComponent } from './components/progress-bar/progress-bar.component';
import { StatCardComponent } from './components/stat-card/stat-card.component';
import { StatusBadgeComponent } from './components/status-badge/status-badge.component';
import { SeverityTonePipe } from './pipes/severity-tone.pipe';

const PUBLIC_API = [
  StatusBadgeComponent,
  StatCardComponent,
  ProgressBarComponent,
  EmptyStateComponent,
  LoadingSpinnerComponent,
  SeverityTonePipe
];

@NgModule({
  declarations: PUBLIC_API,
  imports: [CommonModule, FormsModule],
  exports: [CommonModule, FormsModule, ...PUBLIC_API]
})
export class SharedModule {}
