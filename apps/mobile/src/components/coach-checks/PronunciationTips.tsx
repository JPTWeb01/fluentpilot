import type { PronunciationTip } from "@fluentpilot/shared";
import { Text, View } from "react-native";

export function PronunciationTips({ tips }: { tips: PronunciationTip[] }) {
  if (!tips.length) return null;

  return (
    <View className="mt-1 gap-1">
      {tips.map((tip, index) => (
        <Text key={index} className="text-xs text-violet-600">
          &quot;{tip.word}&quot; {"— "}
          {tip.tip}
        </Text>
      ))}
    </View>
  );
}
