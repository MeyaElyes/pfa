import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { Station } from '../models';
import { ApiService } from './api.service';

@Injectable({ providedIn: 'root' })
export class StationService {
  constructor(private readonly api: ApiService) {}

  getStations(): Observable<Station[]> {
    return this.api.get<Station[]>('/stations');
  }

  getCompanies(): Observable<string[]> {
    return this.api.get<string[]>('/companies');
  }
}
