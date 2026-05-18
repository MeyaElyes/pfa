import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';

export interface ReportResponse {
  station_id: string;
  report: string;
}

@Injectable({ providedIn: 'root' })
export class ReportService {
  constructor(private readonly api: ApiService) {}

  getReport(stationId: string): Observable<ReportResponse> {
    return this.api.get<ReportResponse>('/report', { station_id: stationId });
  }

  getReportPdfUrl(stationId: string): string {
    return `http://localhost:8000/report/pdf?station_id=${stationId}`;
  }
}