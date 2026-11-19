import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwind from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  const target = env.VITE_API_BASE_URL || "http://localhost:8000";
  const proxy = { "/api": { target }, "/media": { target } };
  return {
    plugins: [react(), tailwind()],
    server: { proxy },
    preview: { proxy },
    build: {
      rolldownOptions: {
        output: {
          codeSplitting: {
            groups: [
              {
                name: "react-vendor",
                test: /\/node_modules\/(react|react-dom|react-router|react-router-dom|scheduler)\//,
              },
              {
                name: "forms-vendor",
                test: /\/node_modules\/(zod|react-hook-form|@hookform)\//,
              },
            ],
          },
        },
      },
    },
  };
});
