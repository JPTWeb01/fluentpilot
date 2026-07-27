import type {
  AccentTip,
  GrammarCorrection,
  PronunciationTip,
  VocabularySuggestion,
} from "@fluentpilot/shared";
import {
  useAccentCheck,
  useGrammarCheck,
  usePronunciationCheck,
  useVocabularyCheck,
} from "@fluentpilot/shared";
import { useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Switch, Text, TextInput, View } from "react-native";

import {
  AccentTips,
  CheckLegend,
  GrammarCorrections,
  PronunciationTips,
  VocabularySuggestions,
} from "@/components/coach-checks";

export default function PracticeScreen() {
  const [text, setText] = useState("");
  const [accentCheckEnabled, setAccentCheckEnabled] = useState(false);
  const [corrections, setCorrections] = useState<GrammarCorrection[]>([]);
  const [suggestions, setSuggestions] = useState<VocabularySuggestion[]>([]);
  const [pronunciationTips, setPronunciationTips] = useState<PronunciationTip[]>([]);
  const [accentTips, setAccentTips] = useState<AccentTip[]>([]);

  const grammarCheck = useGrammarCheck();
  const vocabularyCheck = useVocabularyCheck();
  const pronunciationCheck = usePronunciationCheck();
  const accentCheck = useAccentCheck();

  const isChecking =
    grammarCheck.isPending ||
    vocabularyCheck.isPending ||
    pronunciationCheck.isPending ||
    accentCheck.isPending;

  const handleCheck = () => {
    if (!text.trim()) return;

    grammarCheck
      .mutateAsync({ text })
      .then((result) => setCorrections(result.corrections))
      .catch(() => {});

    vocabularyCheck
      .mutateAsync({ text })
      .then((result) => setSuggestions(result.suggestions))
      .catch(() => {});

    pronunciationCheck
      .mutateAsync({ text })
      .then((result) => setPronunciationTips(result.tips))
      .catch(() => {});

    if (accentCheckEnabled) {
      accentCheck
        .mutateAsync({ text })
        .then((result) => setAccentTips(result.tips))
        .catch(() => {});
    } else {
      setAccentTips([]);
    }
  };

  return (
    <ScrollView className="flex-1 bg-white" contentContainerClassName="px-4 py-6">
      <Text className="text-xl font-semibold text-neutral-900">Practice speaking</Text>
      <Text className="mt-1 text-sm text-neutral-500">
        Voice recording lands in a follow-up PR. For now, type what you&apos;d say and get
        instant feedback.
      </Text>

      <View className="mt-4 flex-row items-center gap-2">
        <Switch value={accentCheckEnabled} onValueChange={setAccentCheckEnabled} />
        <Text className="text-sm text-neutral-500">Also check my accent clarity (opt-in)</Text>
      </View>

      <View className="mt-3">
        <CheckLegend />
      </View>

      <TextInput
        className="mt-4 min-h-[100px] rounded-md border border-neutral-300 px-3 py-2 text-base"
        multiline
        placeholder="Type a sentence to check..."
        value={text}
        onChangeText={setText}
      />

      <Pressable
        className={`mt-3 items-center rounded-md py-3 ${
          !text.trim() || isChecking ? "bg-neutral-400" : "bg-neutral-900"
        }`}
        disabled={!text.trim() || isChecking}
        onPress={handleCheck}
      >
        {isChecking ? (
          <ActivityIndicator color="white" />
        ) : (
          <Text className="font-medium text-white">Check my English</Text>
        )}
      </Pressable>

      <View className="mt-4 gap-3">
        <GrammarCorrections corrections={corrections} />
        <VocabularySuggestions suggestions={suggestions} />
        <PronunciationTips tips={pronunciationTips} />
        <AccentTips tips={accentTips} />
      </View>
    </ScrollView>
  );
}
