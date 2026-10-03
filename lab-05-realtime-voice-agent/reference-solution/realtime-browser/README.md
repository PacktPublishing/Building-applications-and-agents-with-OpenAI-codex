# Browser Realtime voice agent

This is a sibling JavaScript implementation of Lab 05. It uses the TypeScript
Agents SDK `RealtimeAgent` and `RealtimeSession` to keep a live WebRTC session
open; the model handles the speech-to-speech conversation directly. This is a
different architecture from the Python `VoicePipeline`, which chains
transcription, a text-agent workflow, and speech generation. They are
alternative paths, not layers in one runtime.

## Run locally

Use Node.js 20 or newer. From this directory:

```sh
npm install
cp .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. Run the trusted token server in one terminal:

```sh
npm run start:server
```

Run the browser app in another terminal:

```sh
npm run dev
```

Open the `http://localhost:5173` URL printed by Vite and click **Start
session**. Browsers treat localhost as a secure context for microphone access,
so local HTTPS certificates are not needed. Microphone permission is requested
when the session starts. The browser calls the local `/token` endpoint and
receives only an ephemeral client secret; the standard API key stays in the
Node server.

## Runtime events

The status panel logs completed user transcripts, completed assistant audio
transcripts, audio start/stop, turn completion, interruptions, and errors. It
ignores empty user transcripts, buffers assistant transcript deltas until a
completed transcript arrives, and does not add duplicate assistant text from
agent lifecycle events or noisy `history_updated` snapshots. Realtime output
is configured with audio modality only; transcript events remain available for
captions.

## Checks

```sh
npm test
npm run typecheck
npm run build
```

All tests run locally and do not call the OpenAI API.
