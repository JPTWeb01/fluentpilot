import { Text, View } from "react-native";

const ITEMS = [
  { label: "Grammar", className: "bg-amber-600" },
  { label: "Vocabulary", className: "bg-sky-600" },
  { label: "Pronunciation", className: "bg-violet-600" },
  { label: "Accent", className: "bg-emerald-600" },
];

export function CheckLegend() {
  return (
    <View className="flex-row flex-wrap gap-x-4 gap-y-1">
      {ITEMS.map((item) => (
        <View key={item.label} className="flex-row items-center gap-1.5">
          <View className={`size-2 rounded-full ${item.className}`} />
          <Text className="text-xs text-neutral-500">{item.label}</Text>
        </View>
      ))}
    </View>
  );
}
