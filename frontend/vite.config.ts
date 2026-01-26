import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// Log environment variables during build (for debugging)
console.log('[Vite Build] VITE_API_URL:', process.env.VITE_API_URL || 'NOT SET');
console.log('[Vite Build] All VITE_ env vars:', Object.keys(process.env).filter(k => k.startsWith('VITE_')));

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: "::",
    port: 8080,
    hmr: {
      overlay: false,
    },
  },
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
