import { useRef, useState } from "react";
import { Loader2, Mic, Square } from "lucide-react";
import { toast } from "sonner";

import { AppShell } from "@/components/layout/AppShell";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { blobToBase64, base64ToBlob } from "@/features/voice/audio";
import { useVoiceTurn } from "@/features/voice/api";
import type { VoiceMessage } from "@/features/voice/types";

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

export function PracticePage() {
  const [state, setState] = useState<RecorderState>("idle");
  const [history, setHistory] = useState<VoiceMessage[]>([]);
  const [replyAudioUrl, setReplyAudioUrl] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const voiceTurn = useVoiceTurn();

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

      setHistory((prev) => [
        ...prev,
        { role: "user", content: response.transcript },
        { role: "assistant", content: response.reply_text },
      ]);

      const replyBlob = base64ToBlob(response.reply_audio_base64, "audio/wav");
      const url = URL.createObjectURL(replyBlob);
      setReplyAudioUrl((previous) => {
        if (previous) URL.revokeObjectURL(previous);
        return url;
      });
      void new Audio(url).play();
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
              <div
                key={index}
                className={
                  message.role === "user"
                    ? "ml-auto max-w-[80%] rounded-lg bg-primary px-3 py-2 text-sm text-primary-foreground"
                    : "mr-auto max-w-[80%] rounded-lg bg-muted px-3 py-2 text-sm"
                }
              >
                {message.content}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </AppShell>
  );
}
