import type { GrammarCorrection } from "@fluentpilot/shared";
import { Text, View } from "react-native";

export function GrammarCorrections({ corrections }: { corrections: GrammarCorrection[] }) {
  if (!corrections.length) return null;

  return (
    <View className="mt-1 gap-1">
      {corrections.map((correction, index) => (
        <Text key={index} className="text-xs text-amber-600">
          <Text className="line-through">{correction.original}</Text> {"→ "}
          {correction.corrected} {"— "}
          {correction.explanation}
        </Text>
      ))}
    </View>
  );
}
