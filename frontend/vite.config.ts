import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

const repositoryRoot = fileURLToPath(new URL("../", import.meta.url));
const buildDirectory = fileURLToPath(new URL("../static/build/", import.meta.url));
const cacheDirectory = fileURLToPath(new URL("./node_modules/.vite/", import.meta.url));
const applicationEntry = fileURLToPath(new URL("./src/app.ts", import.meta.url));

export default defineConfig({
  root: repositoryRoot,
  cacheDir: cacheDirectory,
  plugins: [tailwindcss()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
  },
  build: {
    manifest: true,
    outDir: buildDirectory,
    emptyOutDir: true,
    rolldownOptions: {
      input: {
        app: applicationEntry,
      },
    },
  },
});
