import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "./tests",
  testMatch: "*.spec.mjs",
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
  use: {
    baseURL: "http://127.0.0.1:8770",
    browserName: "chromium",
    channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
    reducedMotion: "reduce",
  },
  webServer: {
    command: "python3 -m http.server 8770 --bind 127.0.0.1 --directory dist",
    url: "http://127.0.0.1:8770",
    reuseExistingServer: !process.env.CI,
  },
});
