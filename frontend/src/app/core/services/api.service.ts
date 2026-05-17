import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';

/**
 * Thin wrapper around HttpClient that centralizes the backend base URL
 * and HttpParams construction. Feature services consume this service
 * instead of HttpClient directly.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = environment.apiUrl;
  private readonly aiUrl   = environment.aiUrl;

  constructor(private readonly http: HttpClient) {}

  get<T>(path: string, params?: Record<string, string | number | undefined>): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${path}`, {
      params: this.buildParams(params)
    });
  }

  post<T>(path: string, body: unknown, params?: Record<string, string | number | undefined>): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${path}`, body, {
      params: this.buildParams(params)
    });
  }

  aiGet<T>(path: string, params?: Record<string, string | number | undefined>): Observable<T> {
    return this.http.get<T>(`${this.aiUrl}${path}`, {
      params: this.buildParams(params)
    });
  }

  aiPost<T>(path: string, body: unknown): Observable<T> {
    return this.http.post<T>(`${this.aiUrl}${path}`, body);
  }

  private buildParams(params?: Record<string, string | number | undefined>): HttpParams {
    let httpParams = new HttpParams();
    if (!params) {
      return httpParams;
    }
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '') {
        httpParams = httpParams.set(key, String(value));
      }
    }
    return httpParams;
  }
}
