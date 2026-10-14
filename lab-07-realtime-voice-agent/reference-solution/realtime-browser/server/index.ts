import "dotenv/config";
import express from "express";
import { createClientSecret } from "./token";

const app = express();
const port = Number(process.env.PORT ?? 5050);

app.post("/token", async (_request, response) => {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    response.status(503).json({ error: "OPENAI_API_KEY is not configured on the token server" });
    return;
  }
  try {
    const { value } = await createClientSecret(apiKey);
    response.json({ client_secret: value });
  } catch (error) {
    console.error("Unable to create Realtime client secret:", error);
    response.status(502).json({ error: "Could not create a Realtime client secret" });
  }
});

app.listen(port, "localhost", () => {
  console.log(`Realtime token server listening at http://localhost:${port}`);
});
