export interface GrammarCorrection {
  original: string;
  corrected: string;
  explanation: string;
}

export interface GrammarCheckRequest {
  text: string;
}

export interface GrammarCheckResponse {
  corrections: GrammarCorrection[];
}
