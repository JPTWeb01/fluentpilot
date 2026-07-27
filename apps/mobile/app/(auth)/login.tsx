import { ApiError, useLogin } from "@fluentpilot/shared";
import { Link, useRouter } from "expo-router";
import { useState } from "react";
import { ActivityIndicator, Pressable, Text, TextInput, View } from "react-native";

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const router = useRouter();
  const login = useLogin();

  const disabled = login.isPending || !email || !password;

  const handleSubmit = () => {
    login.mutate({ email, password }, { onSuccess: () => router.replace("/") });
  };

  return (
    <View className="flex-1 justify-center bg-white px-6">
      <Text className="text-2xl font-semibold text-neutral-900">Log in to FluentPilot</Text>
      <Text className="mt-1 text-sm text-neutral-500">
        Practice your spoken English with an AI coach.
      </Text>

      <View className="mt-6 gap-4">
        <View className="gap-1.5">
          <Text className="text-sm font-medium text-neutral-900">Email</Text>
          <TextInput
            className="rounded-md border border-neutral-300 px-3 py-2 text-base"
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="email-address"
            value={email}
            onChangeText={setEmail}
          />
        </View>
        <View className="gap-1.5">
          <Text className="text-sm font-medium text-neutral-900">Password</Text>
          <TextInput
            className="rounded-md border border-neutral-300 px-3 py-2 text-base"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />
        </View>

        {login.isError && (
          <Text className="text-sm text-red-600">
            {login.error instanceof ApiError ? login.error.message : "Login failed."}
          </Text>
        )}

        <Pressable
          className={`items-center rounded-md py-3 ${disabled ? "bg-neutral-400" : "bg-neutral-900"}`}
          disabled={disabled}
          onPress={handleSubmit}
        >
          {login.isPending ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text className="font-medium text-white">Log in</Text>
          )}
        </Pressable>
      </View>

      <View className="mt-6 flex-row justify-center gap-1">
        <Text className="text-sm text-neutral-500">No account?</Text>
        <Link href="/register" asChild>
          <Pressable>
            <Text className="text-sm font-medium text-neutral-900 underline">Register</Text>
          </Pressable>
        </Link>
      </View>
    </View>
  );
}
