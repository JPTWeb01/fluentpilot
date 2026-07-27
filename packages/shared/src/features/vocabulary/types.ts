export interface VocabularySuggestion {
  original: string;
  suggestion: string;
  explanation: string;
}

export interface VocabularyCheckRequest {
  text: string;
}

export interface VocabularyCheckResponse {
  suggestions: VocabularySuggestion[];
}
