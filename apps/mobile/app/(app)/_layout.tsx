import { Redirect, Stack } from "expo-router";
import { View } from "react-native";

import { AppHeader } from "@/components/AppHeader";
import { useAuthHydrated, useAuthStore } from "@/stores/auth-store";

export default function AppLayout() {
  const accessToken = useAuthStore((s) => s.accessToken);
  const hydrated = useAuthHydrated();

  if (!hydrated) {
    return <View className="flex-1 bg-white" />;
  }

  if (!accessToken) {
    return <Redirect href="/login" />;
  }

  return <Stack screenOptions={{ header: () => <AppHeader /> }} />;
}
