import type { VocabularySuggestion } from "@fluentpilot/shared";
import { Text, View } from "react-native";

export function VocabularySuggestions({ suggestions }: { suggestions: VocabularySuggestion[] }) {
  if (!suggestions.length) return null;

  return (
    <View className="mt-1 gap-1">
      {suggestions.map((suggestion, index) => (
        <Text key={index} className="text-xs text-sky-600">
          &quot;{suggestion.original}&quot; {"→ "}&quot;{suggestion.suggestion}&quot; {"— "}
          {suggestion.explanation}
        </Text>
      ))}
    </View>
  );
}
