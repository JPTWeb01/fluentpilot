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
