import { useMe } from "@fluentpilot/shared";
import { Link } from "expo-router";
import { Pressable, Text, View } from "react-native";

import { useAuthStore } from "@/stores/auth-store";

export default function DashboardScreen() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const { data: user, isLoading } = useMe(!!accessToken);

  return (
    <View className="flex-1 bg-white px-4 py-6">
      <Text className="text-xl font-semibold text-neutral-900">
        Welcome{user?.full_name ? `, ${user.full_name}` : ""}
      </Text>
      <Text className="mt-1 text-sm text-neutral-500">
        {isLoading ? "Loading your profile..." : `Signed in as ${user?.email}`}
      </Text>

      <Text className="mt-6 text-sm text-neutral-500">
        Ready to practice speaking English out loud?
      </Text>
      <View className="mt-3 flex-row gap-2">
        <Link href="/practice" asChild>
          <Pressable className="items-center rounded-md bg-neutral-900 px-4 py-2.5">
            <Text className="text-sm font-medium text-white">Start practicing</Text>
          </Pressable>
        </Link>
        <Link href="/interview" asChild>
          <Pressable className="items-center rounded-md border border-neutral-300 px-4 py-2.5">
            <Text className="text-sm font-medium text-neutral-900">Try a mock interview</Text>
          </Pressable>
        </Link>
      </View>
    </View>
  );
}
