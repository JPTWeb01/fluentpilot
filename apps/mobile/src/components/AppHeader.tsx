import { useMe } from "@fluentpilot/shared";
import { Alert, Pressable, Text, View } from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";

import { useAuthStore } from "@/stores/auth-store";

export function AppHeader() {
  const insets = useSafeAreaInsets();
  const accessToken = useAuthStore((s) => s.accessToken);
  const clearSession = useAuthStore((s) => s.clearSession);
  const { data: user } = useMe(!!accessToken);

  const handleLogout = () => {
    Alert.alert("Log out?", "You'll need to log in again to access your dashboard.", [
      { text: "Cancel", style: "cancel" },
      { text: "Log out", style: "destructive", onPress: () => clearSession() },
    ]);
  };

  return (
    <View style={{ paddingTop: insets.top }} className="border-b border-neutral-200 bg-white">
      <View className="flex-row items-center justify-between px-4 py-3">
        <Text className="text-sm font-semibold text-neutral-900">FluentPilot</Text>
        <Pressable onPress={handleLogout}>
          <Text className="text-sm text-neutral-500">{user?.email ?? "Account"}</Text>
        </Pressable>
      </View>
    </View>
  );
}
