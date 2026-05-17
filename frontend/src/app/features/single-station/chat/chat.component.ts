import { Component } from '@angular/core';
import { StationContextService } from '../../../core/services/station-context.service';
import { ChatService } from '../../../core/services/chat.service';
import { ChatMessage } from '../../../core/models';

@Component({
  selector: 'app-chat-tab',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  userInput = '';
  isLoading = false;
  sessionId = `chat-${Math.random().toString(36).slice(2, 10)}`;
  messages: ChatMessage[] = [];
  sourcesUsed: string[] = [];
  selectedStationId = '';

  constructor(
    private readonly stationContext: StationContextService,
    private readonly chatService: ChatService
  ) {
    this.stationContext.selectedStation$.subscribe(id => {
      this.selectedStationId = id;
    });
  }

  sendMessage(): void {
    const trimmed = this.userInput.trim();
    if (!trimmed || this.isLoading) {
      return;
    }

    const userMessage: ChatMessage = { role: 'user', content: trimmed };
    const history = this.messages.filter(message => message.role !== 'system');

    this.messages = [...this.messages, userMessage];
    this.userInput = '';
    this.isLoading = true;
    this.sourcesUsed = [];

    this.chatService
      .sendMessage({
        session_id: this.sessionId,
        station_id: this.selectedStationId,
        message: trimmed,
        history
      })
      .subscribe({
        next: response => {
          this.messages = [...this.messages, { role: 'assistant', content: response.response }];
          this.sourcesUsed = response.sources_used || [];
          this.isLoading = false;
        },
        error: () => {
          this.messages = [...this.messages, { role: 'assistant', content: 'Sorry, I could not reach the chat service at this time.' }];
          this.isLoading = false;
        }
      });
  }
}
