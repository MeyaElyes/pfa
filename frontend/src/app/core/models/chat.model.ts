export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface ChatRequest {
  session_id: string;
  station_id?: string;
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  response: string;
  session_id: string;
  sources_used: string[];
}
