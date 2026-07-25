export interface VoiceMessage {
  role: "user" | "assistant";
  content: string;
}

export interface VoiceTurnRequest {
  audio_base64: string;
  mime_type: string;
  history: VoiceMessage[];
}

export interface VoiceTurnResponse {
  transcript: string;
  reply_text: string;
  reply_audio_base64: string;
}

export interface RateLimitInfo {
  limit_requests: number | null;
  remaining_requests: number | null;
  reset_requests: string | null;
  limit_tokens: number | null;
  remaining_tokens: number | null;
  reset_tokens: string | null;
}

export interface ProviderUsage {
  chat: RateLimitInfo | null;
  stt: RateLimitInfo | null;
  tts: RateLimitInfo | null;
}

export interface UsageResponse {
  providers: Record<string, ProviderUsage>;
}
