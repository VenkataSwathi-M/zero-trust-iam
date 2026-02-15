import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001, // keep same as your current frontend port if needed
    proxy: {
      "/api": {
        target: "http://192.168.31.211:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/ws": {
        target: "ws://192.168.31.211:8000",
        ws: true,
        changeOrigin: true,
      },
    },
  },
});