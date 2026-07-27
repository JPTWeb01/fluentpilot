import type { AccentTip } from "@fluentpilot/shared";
import { Text, View } from "react-native";

export function AccentTips({ tips }: { tips: AccentTip[] }) {
  if (!tips.length) return null;

  return (
    <View className="mt-1 gap-1">
      {tips.map((tip, index) => (
        <Text key={index} className="text-xs text-emerald-600">
          &quot;{tip.phrase}&quot; {"— "}
          {tip.tip}
        </Text>
      ))}
    </View>
  );
}
