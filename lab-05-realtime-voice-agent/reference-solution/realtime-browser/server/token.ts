import { createHash } from "node:crypto";

export const CLIENT_SECRETS_URL = "https://api.openai.com/v1/realtime/client_secrets";
export const REALTIME_MODEL = "gpt-realtime-2";

export interface ClientSecretResponse {
  value: string;
}

export function parseClientSecretResponse(payload: unknown): ClientSecretResponse {
  if (
    typeof payload !== "object" ||
    payload === null ||
    !("value" in payload) ||
    typeof payload.value !== "string" ||
    payload.value.length === 0
  ) {
    throw new Error("OpenAI response did not contain an ephemeral client secret value");
  }
  return { value: payload.value };
}

export function buildClientSecretRequest(apiKey: string, safetyIdentifier: string) {
  if (!apiKey) throw new Error("OPENAI_API_KEY is required on the token server");
  return {
    url: CLIENT_SECRETS_URL,
    init: {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "OpenAI-Safety-Identifier": safetyIdentifier,
      },
      body: JSON.stringify({ session: { type: "realtime", model: REALTIME_MODEL } }),
    } satisfies RequestInit,
  };
}

export function localSafetyIdentifier(): string {
  return createHash("sha256").update("lab-05-realtime-browser-local-demo").digest("hex");
}

export async function createClientSecret(
  apiKey: string,
  fetcher: typeof fetch = fetch,
): Promise<ClientSecretResponse> {
  const request = buildClientSecretRequest(apiKey, localSafetyIdentifier());
  const response = await fetcher(request.url, request.init);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`OpenAI client secret request failed (${response.status}): ${detail}`);
  }
  return parseClientSecretResponse(await response.json());
}
