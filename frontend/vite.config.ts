import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules")) {
            return "vendor";
          }
          if (id.includes("/components/EOY") || id.includes("/components/EOYAdminPanel") || id.includes("/components/Performance") || id.includes("/components/Insurance")) {
            return "admin";
          }
          if (id.includes("/components/Recruit") || id.includes("/recruit") || id.includes("/Candidate")) {
            return "recruitment";
          }
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
  server: {
    port: 5000,
    host: "0.0.0.0",
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
