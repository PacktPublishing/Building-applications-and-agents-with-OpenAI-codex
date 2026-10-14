import "./style.css";
import { createRealtimeSession, requestEphemeralSecret } from "./realtime";

const startButton = document.querySelector<HTMLButtonElement>("#start")!;
const stopButton = document.querySelector<HTMLButtonElement>("#stop")!;
const messageInput = document.querySelector<HTMLInputElement>("#message")!;
const sendButton = document.querySelector<HTMLButtonElement>("#send")!;
const form = document.querySelector<HTMLFormElement>("#text-form")!;
const log = document.querySelector<HTMLOListElement>("#log")!;

let session: ReturnType<typeof createRealtimeSession> | null = null;
let assistantTranscriptDraft = "";

function writeLog(message: string): void {
  const item = document.createElement("li");
  item.textContent = message;
  log.append(item);
  item.scrollIntoView({ block: "nearest" });
}

function setConnected(connected: boolean): void {
  startButton.disabled = connected;
  stopButton.disabled = !connected;
  messageInput.disabled = !connected;
  sendButton.disabled = !connected;
}

startButton.addEventListener("click", async () => {
  startButton.disabled = true;
  try {
    const permission = await navigator.mediaDevices.getUserMedia({ audio: true });
    permission.getTracks().forEach((track) => track.stop());
    writeLog("Requesting a secure realtime session…");
    const clientSecret = await requestEphemeralSecret();
    session = createRealtimeSession();
    session.on("audio_start", () => writeLog("Assistant audio started"));
    session.on("audio_stopped", () => writeLog("Assistant audio stopped"));
    session.on("audio_interrupted", () => writeLog("Assistant audio interrupted"));
    session.on("error", (error) => writeLog(`Realtime error: ${String(error)}`));
    session.on("transport_event", (rawEvent) => {
      const event = rawEvent as { type?: string; transcript?: string; delta?: string; error?: unknown };
      if (event.type === "conversation.item.input_audio_transcription.completed") {
        const transcript = event.transcript?.trim();
        if (transcript) writeLog(`You said: ${transcript}`);
      } else if (event.type === "response.output_audio_transcript.delta") {
        assistantTranscriptDraft += event.delta ?? "";
      } else if (event.type === "response.output_audio_transcript.done") {
        const transcript = (event.transcript || assistantTranscriptDraft).trim();
        assistantTranscriptDraft = "";
        if (transcript) writeLog(`Assistant said: ${transcript}`);
      } else if (event.type === "response.done") {
        assistantTranscriptDraft = "";
        writeLog("Realtime turn complete");
      } else if (event.type === "error") {
        writeLog(`Realtime transport error: ${String(event.error ?? "unknown error")}`);
      }
    });
    await session.connect({ apiKey: clientSecret });
    setConnected(true);
    writeLog("Realtime session connected. You can speak now.");
  } catch (error) {
    session?.close();
    session = null;
    setConnected(false);
    writeLog(`Could not start session: ${error instanceof Error ? error.message : String(error)}`);
  }
});

stopButton.addEventListener("click", () => {
  session?.close();
  session = null;
  assistantTranscriptDraft = "";
  setConnected(false);
  writeLog("Realtime session stopped.");
});

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message || !session) return;
  session.sendMessage(message);
  writeLog(`You typed: ${message}`);
  messageInput.value = "";
});
