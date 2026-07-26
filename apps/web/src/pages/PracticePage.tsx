import { useRef, useState } from "react";
import { Loader2, Mic, Square } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { blobToBase64, base64ToBlob } from "@/features/voice/audio";
import { useVoiceTurn, useVoiceUsage } from "@/features/voice/api";
import type { ProviderUsage, VoiceMessage } from "@/features/voice/types";
import { useGrammarCheck } from "@/features/grammar/api";
import type { GrammarCorrection } from "@/features/grammar/types";
import { useVocabularyCheck } from "@/features/vocabulary/api";
import type { VocabularySuggestion } from "@/features/vocabulary/types";
import { usePronunciationCheck } from "@/features/pronunciation/api";
import type { PronunciationTip } from "@/features/pronunciation/types";
import { useAccentCheck } from "@/features/accent/api";
import type { AccentTip } from "@/features/accent/types";

type RecorderState = "idle" | "recording" | "processing";

const CANDIDATE_MIME_TYPES = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
  "audio/ogg;codecs=opus",
];

function pickSupportedMimeType(): string | null {
  return CANDIDATE_MIME_TYPES.find((type) => MediaRecorder.isTypeSupported(type)) ?? null;
}

function formatRemaining(info: ProviderUsage[keyof ProviderUsage]): string {
  if (!info || info.remaining_requests == null) return "—";
  return info.limit_requests != null
    ? `${info.remaining_requests}/${info.limit_requests}`
    : `${info.remaining_requests}`;
}

export function PracticePage() {
  const [state, setState] = useState<RecorderState>("idle");
  const [history, setHistory] = useState<VoiceMessage[]>([]);
  const [replyAudioUrl, setReplyAudioUrl] = useState<string | null>(null);
  const [corrections, setCorrections] = useState<Record<number, GrammarCorrection[]>>({});
  const [vocabSuggestions, setVocabSuggestions] = useState<Record<number, VocabularySuggestion[]>>(
    {}
  );
  const [pronunciationTips, setPronunciationTips] = useState<Record<number, PronunciationTip[]>>(
    {}
  );
  const [accentCheckEnabled, setAccentCheckEnabled] = useState(false);
  const [accentTips, setAccentTips] = useState<Record<number, AccentTip[]>>({});

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const voiceTurn = useVoiceTurn();
  const usage = useVoiceUsage();
  const grammarCheck = useGrammarCheck();
  const vocabularyCheck = useVocabularyCheck();
  const pronunciationCheck = usePronunciationCheck();
  const accentCheck = useAccentCheck();

  const startRecording = async () => {
    if (!window.isSecureContext) {
      toast.error("Voice practice requires a secure connection (HTTPS or localhost).");
      return;
    }

    const mimeType = pickSupportedMimeType();
    if (!mimeType) {
      toast.error("Your browser doesn't support any audio format this app can send.");
      return;
    }

    let stream: MediaStream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (error) {
      if (error instanceof DOMException && error.name === "NotAllowedError") {
        toast.error("Microphone access was denied. Allow it in your browser settings to practice.");
      } else if (error instanceof DOMException && error.name === "NotFoundError") {
        toast.error("No microphone was found on this device.");
      } else {
        toast.error("Couldn't access the microphone.");
      }
      return;
    }

    const recorder = new MediaRecorder(stream, { mimeType });
    chunksRef.current = [];

    recorder.ondataavailable = (event) => {
      if (event.data.size > 0) chunksRef.current.push(event.data);
    };

    recorder.onstop = () => {
      stream.getTracks().forEach((track) => track.stop());
      void handleRecordingComplete(new Blob(chunksRef.current, { type: mimeType }), mimeType);
    };

    mediaRecorderRef.current = recorder;
    recorder.start();
    setState("recording");
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setState("processing");
  };

  const handleRecordingComplete = async (audioBlob: Blob, mimeType: string) => {
    try {
      const audioBase64 = await blobToBase64(audioBlob);
      const response = await voiceTurn.mutateAsync({
        audio_base64: audioBase64,
        mime_type: mimeType,
        history,
      });

      const userMessageIndex = history.length;
      setHistory((prev) => [
        ...prev,
        { role: "user", content: response.transcript },
        { role: "assistant", content: response.reply_text },
      ]);

      grammarCheck
        .mutateAsync({ text: response.transcript })
        .then((result) => {
          if (result.corrections.length) {
            setCorrections((prev) => ({ ...prev, [userMessageIndex]: result.corrections }));
          }
        })
        .catch(() => {});

      vocabularyCheck
        .mutateAsync({ text: response.transcript })
        .then((result) => {
          if (result.suggestions.length) {
            setVocabSuggestions((prev) => ({ ...prev, [userMessageIndex]: result.suggestions }));
          }
        })
        .catch(() => {});

      pronunciationCheck
        .mutateAsync({ text: response.transcript })
        .then((result) => {
          if (result.tips.length) {
            setPronunciationTips((prev) => ({ ...prev, [userMessageIndex]: result.tips }));
          }
        })
        .catch(() => {});

      if (accentCheckEnabled) {
        accentCheck
          .mutateAsync({ text: response.transcript })
          .then((result) => {
            if (result.tips.length) {
              setAccentTips((prev) => ({ ...prev, [userMessageIndex]: result.tips }));
            }
          })
          .catch(() => {});
      }

      const replyBlob = base64ToBlob(response.reply_audio_base64, "audio/wav");
      const url = URL.createObjectURL(replyBlob);
      setReplyAudioUrl((previous) => {
        if (previous) URL.revokeObjectURL(previous);
        return url;
      });
      void new Audio(url).play();
      void usage.refetch();
    } catch {
      toast.error("Something went wrong processing your turn. Please try again.");
    } finally {
      setState("idle");
    }
  };

  return (
    <AppShell>
      <Card>
        <CardHeader>
          <CardTitle>Practice speaking</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center gap-6 py-8">
          <div className="flex items-center gap-2 self-start text-sm">
            <input
              type="checkbox"
              id="accent-check-toggle"
              checked={accentCheckEnabled}
              onChange={(event) => setAccentCheckEnabled(event.target.checked)}
              className="size-4 rounded border-input"
            />
            <Label htmlFor="accent-check-toggle" className="font-normal text-muted-foreground">
              Also check my accent clarity (opt-in)
            </Label>
          </div>

          <Button
            size="default"
            className="size-20 rounded-full"
            disabled={state === "processing"}
            onClick={state === "recording" ? stopRecording : startRecording}
          >
            {state === "processing" && <Loader2 className="size-8 animate-spin" />}
            {state === "recording" && <Square className="size-8" />}
            {state === "idle" && <Mic className="size-8" />}
          </Button>
          <p className="text-sm text-muted-foreground">
            {state === "idle" && "Tap to start speaking"}
            {state === "recording" && "Listening... tap to stop"}
            {state === "processing" && "Thinking..."}
          </p>

          {replyAudioUrl && (
            <audio controls src={replyAudioUrl} className="w-full max-w-sm">
              <track kind="captions" />
            </audio>
          )}

          <div className="w-full space-y-3">
            {history.map((message, index) => (
              <div key={index} className={message.role === "user" ? "ml-auto max-w-[80%]" : "mr-auto max-w-[80%]"}>
                <div
                  className={
                    message.role === "user"
                      ? "rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground"
                      : "rounded-lg bg-muted px-3 py-2 text-sm"
                  }
                >
                  {message.content}
                </div>
                {corrections[index] && (
                  <div className="mt-1 space-y-1 text-xs text-amber-600 dark:text-amber-400">
                    {corrections[index].map((correction, correctionIndex) => (
                      <p key={correctionIndex}>
                        <del>{correction.original}</del> → {correction.corrected} —{" "}
                        {correction.explanation}
                      </p>
                    ))}
                  </div>
                )}
                {vocabSuggestions[index] && (
                  <div className="mt-1 space-y-1 text-xs text-sky-600 dark:text-sky-400">
                    {vocabSuggestions[index].map((suggestion, suggestionIndex) => (
                      <p key={suggestionIndex}>
                        "{suggestion.original}" → "{suggestion.suggestion}" —{" "}
                        {suggestion.explanation}
                      </p>
                    ))}
                  </div>
                )}
                {pronunciationTips[index] && (
                  <div className="mt-1 space-y-1 text-xs text-violet-600 dark:text-violet-400">
                    {pronunciationTips[index].map((tip, tipIndex) => (
                      <p key={tipIndex}>
                        "{tip.word}" — {tip.tip}
                      </p>
                    ))}
                  </div>
                )}
                {accentTips[index] && (
                  <div className="mt-1 space-y-1 text-xs text-emerald-600 dark:text-emerald-400">
                    {accentTips[index].map((tip, tipIndex) => (
                      <p key={tipIndex}>
                        "{tip.phrase}" — {tip.tip}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {usage.data && Object.keys(usage.data.providers).length > 0 && (
            <div className="w-full space-y-1 border-t pt-4 text-xs text-muted-foreground">
              <p className="font-medium">API quota remaining (this server session)</p>
              {Object.entries(usage.data.providers).map(([name, providerUsage]) => (
                <div key={name} className="flex justify-between gap-4">
                  <span className="capitalize">{name}</span>
                  <span>
                    chat {formatRemaining(providerUsage.chat)} · stt{" "}
                    {formatRemaining(providerUsage.stt)} · tts {formatRemaining(providerUsage.tts)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </AppShell>
  );
}
