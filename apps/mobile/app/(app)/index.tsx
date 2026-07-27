import { useMe } from "@fluentpilot/shared";
import { Text, View } from "react-native";

export default function DashboardScreen() {
  const { data: user } = useMe(true);

  return (
    <View className="flex-1 items-center justify-center bg-white px-6">
      <Text className="text-lg font-semibold">Dashboard</Text>
      <Text className="mt-2 text-sm text-neutral-500">{user?.email ?? "Loading..."}</Text>
    </View>
  );
}
