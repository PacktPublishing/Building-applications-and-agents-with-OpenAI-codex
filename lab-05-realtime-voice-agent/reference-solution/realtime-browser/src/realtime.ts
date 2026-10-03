import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";

export const REALTIME_MODEL = "gpt-realtime-2";

export function createRealtimeAgent(): RealtimeAgent {
  return new RealtimeAgent({
    name: "realtime_course_assistant",
    instructions:
      "You are a concise voice assistant for an Agents SDK course. Answer only what the user says or types. If audio is unclear, ask them to repeat it; never claim to read their mind.",
  });
}

export function createRealtimeSession(): RealtimeSession {
  return new RealtimeSession(createRealtimeAgent(), {
    model: REALTIME_MODEL,
    config: {
      outputModalities: ["audio"],
      audio: {
        input: {
          transcription: { model: "gpt-4o-mini-transcribe" },
          turnDetection: { type: "semantic_vad", eagerness: "low" },
        },
        output: { format: "pcm16" },
      },
    },
  });
}

export async function parseEphemeralSecretResponse(response: Response): Promise<string> {
  if (!response.ok) {
    throw new Error(`Token server returned ${response.status}`);
  }
  const payload: unknown = await response.json();
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("client_secret" in payload) ||
    typeof payload.client_secret !== "string" ||
    payload.client_secret.length === 0
  ) {
    throw new Error("Token server response did not contain a client_secret string");
  }
  return payload.client_secret;
}

export async function requestEphemeralSecret(fetcher: typeof fetch = fetch): Promise<string> {
  const response = await fetcher("/token", { method: "POST" });
  return parseEphemeralSecretResponse(response);
}
