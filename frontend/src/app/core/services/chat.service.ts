import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ApiService } from './api.service';
import { ChatRequest, ChatResponse } from '../models';

@Injectable({ providedIn: 'root' })
export class ChatService {
  constructor(private readonly api: ApiService) {}

  sendMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.api.aiPost<ChatResponse>('/chat', request);
  }
}
