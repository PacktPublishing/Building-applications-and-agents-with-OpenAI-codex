import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "localhost",
    proxy: { "/token": "http://localhost:5050" },
  },
});
