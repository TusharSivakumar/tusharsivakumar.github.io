import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";

// If deploying to https://<user>.github.io/<repo>/, set base to "/<repo>/".
// If deploying to a custom domain or a <user>.github.io root repo, use "/".
export default defineConfig({
  base: "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
