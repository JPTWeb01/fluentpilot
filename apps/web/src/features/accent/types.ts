export interface AccentTip {
  phrase: string;
  tip: string;
}

export interface AccentCheckRequest {
  text: string;
}

export interface AccentCheckResponse {
  tips: AccentTip[];
}
