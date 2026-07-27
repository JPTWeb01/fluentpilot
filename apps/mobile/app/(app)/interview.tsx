import type { ProviderUsage, VoiceMessage } from "@fluentpilot/shared";
import { useVoiceTurn, useVoiceUsage } from "@fluentpilot/shared";
import {
  RecordingPresets,
  requestRecordingPermissionsAsync,
  setAudioModeAsync,
  useAudioPlayer,
  useAudioRecorder,
} from "expo-audio";
import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Alert, Pressable, ScrollView, Text, View } from "react-native";

import { fileUriToBase64, writeBase64ToCacheFile } from "@/features/voice/audio";

type RecorderScreenState = "idle" | "recording" | "processing";

function formatRemaining(info: ProviderUsage[keyof ProviderUsage]): string {
  if (!info || info.remaining_requests == null) return "—";
  return info.limit_requests != null
    ? `${info.remaining_requests}/${info.limit_requests}`
    : `${info.remaining_requests}`;
}

export default function InterviewScreen() {
  const [state, setState] = useState<RecorderScreenState>("idle");
  const [history, setHistory] = useState<VoiceMessage[]>([]);

  const historyScrollRef = useRef<ScrollView>(null);
  const recorder = useAudioRecorder(RecordingPresets.HIGH_QUALITY);
  const player = useAudioPlayer(null);

  const voiceTurn = useVoiceTurn();
  const usage = useVoiceUsage();

  useEffect(() => {
    historyScrollRef.current?.scrollToEnd({ animated: true });
  }, [history]);

  const startRecording = async () => {
    const permission = await requestRecordingPermissionsAsync();
    if (!permission.granted) {
      Alert.alert(
        "Microphone access needed",
        "Allow microphone access in your device settings to answer."
      );
      return;
    }

    await setAudioModeAsync({ allowsRecording: true, playsInSilentMode: true });
    await recorder.prepareToRecordAsync();
    recorder.record();
    setState("recording");
  };

  const stopRecording = async () => {
    setState("processing");
    await recorder.stop();

    const uri = recorder.uri;
    if (!uri) {
      setState("idle");
      Alert.alert("Recording failed", "Please try again.");
      return;
    }

    await handleRecordingComplete(uri);
  };

  const handleRecordingComplete = async (uri: string) => {
    try {
      const audioBase64 = await fileUriToBase64(uri);
      const response = await voiceTurn.mutateAsync({
        audio_base64: audioBase64,
        mime_type: "audio/mp4",
        history,
        mode: "interview",
      });

      setHistory((prev) => [
        ...prev,
        { role: "user", content: response.transcript },
        { role: "assistant", content: response.reply_text },
      ]);

      const replyUri = writeBase64ToCacheFile(response.reply_audio_base64, ".wav");
      player.replace(replyUri);
      player.play();

      void usage.refetch();
    } catch {
      Alert.alert("Something went wrong", "We couldn't process that turn. Please try again.");
    } finally {
      setState("idle");
    }
  };

  return (
    <ScrollView className="flex-1 bg-white" contentContainerClassName="px-4 py-6">
      <Text className="text-xl font-semibold text-neutral-900">Mock interview</Text>
      <Text className="mt-1 text-sm text-neutral-500">
        Answer out loud. The interviewer replies and keeps the conversation going.
      </Text>

      <View className="mt-6 items-center gap-3">
        <Pressable
          className={`size-20 items-center justify-center rounded-full ${
            state === "recording" ? "bg-red-600" : "bg-neutral-900"
          }`}
          disabled={state === "processing"}
          onPress={state === "recording" ? stopRecording : startRecording}
        >
          {state === "processing" ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text className="text-2xl text-white">{state === "recording" ? "■" : "●"}</Text>
          )}
        </Pressable>
        <Text className="text-sm text-neutral-500">
          {state === "idle" && "Tap to answer"}
          {state === "recording" && "Listening... tap to stop"}
          {state === "processing" && "Thinking..."}
        </Text>
      </View>

      <View className="mt-6 h-64 rounded-md border border-neutral-300 bg-neutral-50">
        <ScrollView ref={historyScrollRef} contentContainerClassName="gap-3 p-3">
          {history.length === 0 ? (
            <Text className="mt-16 text-center text-sm text-neutral-400">
              Tap the mic below to start the interview.
            </Text>
          ) : (
            history.map((message, index) => (
              <View
                key={index}
                className={message.role === "user" ? "ml-auto max-w-[85%]" : "mr-auto max-w-[85%]"}
              >
                <View
                  className={
                    message.role === "user"
                      ? "rounded-lg bg-neutral-900 px-3 py-2"
                      : "rounded-lg bg-neutral-200 px-3 py-2"
                  }
                >
                  <Text
                    className={message.role === "user" ? "text-sm text-white" : "text-sm text-neutral-900"}
                  >
                    {message.content}
                  </Text>
                </View>
              </View>
            ))
          )}
        </ScrollView>
      </View>

      {usage.data && Object.keys(usage.data.providers).length > 0 && (
        <View className="mt-4 gap-1 border-t border-neutral-200 pt-4">
          <Text className="text-xs font-medium text-neutral-500">
            API quota remaining (this server session)
          </Text>
          {Object.entries(usage.data.providers).map(([name, providerUsage]) => (
            <View key={name} className="flex-row justify-between gap-4">
              <Text className="text-xs capitalize text-neutral-500">{name}</Text>
              <Text className="text-xs text-neutral-500">
                chat {formatRemaining(providerUsage.chat)} · stt {formatRemaining(providerUsage.stt)} · tts{" "}
                {formatRemaining(providerUsage.tts)}
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}
