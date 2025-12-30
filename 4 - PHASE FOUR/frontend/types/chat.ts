/**
 * TypeScript types for chat functionality.
 *
 * Task: T022 - Define TypeScript types for chat messages
 * Spec: specs/003-phase3-ai-chatbot/contracts/chat-endpoint.md
 */

export interface Message {
  id?: number;
  role: 'user' | 'assistant';
  content: string;
  created_at?: string;
}

export interface Conversation {
  id: number;
  user_id: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  conversation_id: number;
  message: string;
  created_at: string;
}

export interface ConversationHistoryResponse {
  conversation_id: number;
  messages: Message[];
}

export interface ChatError {
  detail: string;
}
