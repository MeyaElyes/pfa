import { Component, OnDestroy, OnInit } from '@angular/core';
import { Subject, takeUntil } from 'rxjs';
import { ReportService } from '../../../core/services/report.service';
import { StationContextService } from '../../../core/services/station-context.service';

@Component({
  selector: 'app-report-tab',  // ✅ même pattern que les autres
  templateUrl: './report.component.html',
  styleUrls: ['./report.component.css']
})
export class ReportComponent implements OnInit, OnDestroy {
  stationId = '';
  reportMarkdown = '';
  isLoading = false;
  error: string | null = null;
  generated = false;
  selectedFuel = 'Gasoil50';

  private readonly destroy$ = new Subject<void>();

  constructor(
    private readonly reportService: ReportService,
    private readonly stationContext: StationContextService
  ) {}

  ngOnInit(): void {
    this.stationContext.selectedStation$
      .pipe(takeUntil(this.destroy$))
      .subscribe(id => (this.stationId = id));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  generateReport(): void {
    if (!this.stationId) return;
    this.isLoading = true;
    this.error = null;
    this.generated = false;

    this.reportService.getReport(this.stationId, this.selectedFuel).subscribe({
      next: (data) => {
        this.reportMarkdown = data.report;
        this.isLoading = false;
        this.generated = true;
      },
      error: () => {
        this.error = 'Failed to generate report. Please try again.';
        this.isLoading = false;
      }
    });
  }

  downloadPdf(): void {
    const url = this.reportService.getReportPdfUrl(this.stationId, this.selectedFuel);
    window.open(url, '_blank');
  }

  downloadMarkdown(): void {
    const blob = new Blob([this.reportMarkdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report_${this.stationId}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }
}