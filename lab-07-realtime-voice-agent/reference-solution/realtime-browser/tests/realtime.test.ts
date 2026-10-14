import assert from "node:assert/strict";
import test from "node:test";
import { RealtimeAgent, RealtimeSession } from "@openai/agents/realtime";
import { createRealtimeAgent, createRealtimeSession, parseEphemeralSecretResponse } from "../src/realtime";
import { buildClientSecretRequest, parseClientSecretResponse } from "../server/token";

test("creates SDK RealtimeAgent and RealtimeSession without connecting", () => {
  const agent = createRealtimeAgent();
  const session = createRealtimeSession();
  assert.ok(agent instanceof RealtimeAgent);
  assert.equal(agent.name, "realtime_course_assistant");
  assert.ok(session instanceof RealtimeSession);
  session.close();
});

test("parses only an ephemeral client_secret for the browser", async () => {
  assert.equal(
    await parseEphemeralSecretResponse(new Response(JSON.stringify({ client_secret: "ek_test" }))),
    "ek_test",
  );
  await assert.rejects(
    parseEphemeralSecretResponse(new Response(JSON.stringify({ value: "standard-looking" }))),
    /client_secret/,
  );
});

test("parses OpenAI client secret value on the trusted server", () => {
  assert.deepEqual(parseClientSecretResponse({ value: "ek_test" }), { value: "ek_test" });
  assert.throws(() => parseClientSecretResponse({}), /ephemeral client secret/);
});

test("builds server-only token request with model and safety identifier", () => {
  const { url, init } = buildClientSecretRequest("sk-server-only", "stable-hashed-id");
  assert.equal(url, "https://api.openai.com/v1/realtime/client_secrets");
  assert.equal(init.method, "POST");
  assert.equal(new Headers(init.headers).get("Authorization"), "Bearer sk-server-only");
  assert.equal(new Headers(init.headers).get("OpenAI-Safety-Identifier"), "stable-hashed-id");
  assert.deepEqual(JSON.parse(String(init.body)), {
    session: { type: "realtime", model: "gpt-realtime-2" },
  });
});
