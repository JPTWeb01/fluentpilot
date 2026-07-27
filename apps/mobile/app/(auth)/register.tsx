import { ApiError, useRegister } from "@fluentpilot/shared";
import { Link, useRouter } from "expo-router";
import { useState } from "react";
import { ActivityIndicator, Pressable, Text, TextInput, View } from "react-native";

export default function RegisterScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [mismatchError, setMismatchError] = useState(false);
  const router = useRouter();
  const register = useRegister();

  const disabled = register.isPending || !email || !password || !confirmPassword;

  const handleSubmit = () => {
    if (password !== confirmPassword) {
      setMismatchError(true);
      return;
    }
    setMismatchError(false);
    register.mutate({ email, password }, { onSuccess: () => router.replace("/") });
  };

  return (
    <View className="flex-1 justify-center bg-white px-6">
      <Text className="text-2xl font-semibold text-neutral-900">Create your account</Text>
      <Text className="mt-1 text-sm text-neutral-500">
        Start practicing with your AI speaking coach.
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
            maxLength={72}
            value={password}
            onChangeText={setPassword}
          />
        </View>
        <View className="gap-1.5">
          <Text className="text-sm font-medium text-neutral-900">Confirm password</Text>
          <TextInput
            className="rounded-md border border-neutral-300 px-3 py-2 text-base"
            secureTextEntry
            maxLength={72}
            value={confirmPassword}
            onChangeText={setConfirmPassword}
          />
        </View>

        {mismatchError && <Text className="text-sm text-red-600">Passwords don&apos;t match.</Text>}
        {register.isError && (
          <Text className="text-sm text-red-600">
            {register.error instanceof ApiError ? register.error.message : "Registration failed."}
          </Text>
        )}

        <Pressable
          className={`items-center rounded-md py-3 ${disabled ? "bg-neutral-400" : "bg-neutral-900"}`}
          disabled={disabled}
          onPress={handleSubmit}
        >
          {register.isPending ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text className="font-medium text-white">Create account</Text>
          )}
        </Pressable>
      </View>

      <View className="mt-6 flex-row justify-center gap-1">
        <Text className="text-sm text-neutral-500">Already have an account?</Text>
        <Link href="/login" asChild>
          <Pressable>
            <Text className="text-sm font-medium text-neutral-900 underline">Log in</Text>
          </Pressable>
        </Link>
      </View>
    </View>
  );
}
