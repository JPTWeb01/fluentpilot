export interface PronunciationTip {
  word: string;
  tip: string;
}

export interface PronunciationCheckRequest {
  text: string;
}

export interface PronunciationCheckResponse {
  tips: PronunciationTip[];
}
