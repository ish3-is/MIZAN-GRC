import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  workers: 1,
  use: {
    baseURL: "http://localhost:5173",
    browserName: "chromium",
    viewport: { width: 1440, height: 1050 },
  },
  reporter: [["list"]],
  timeout: 45000,
});
