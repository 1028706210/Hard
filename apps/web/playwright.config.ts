import { defineConfig } from "@playwright/test";

const e2eRunId = process.env.HARD_E2E_RUN_ID ?? `run-${Date.now()}`;
process.env.HARD_E2E_RUN_ID = e2eRunId;

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4173",
    launchOptions: { executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" },
  },
  webServer: {
    command: `powershell -NoProfile -Command \"$env:HARD_E2E_RUN_ID = '${e2eRunId}'; $api = Start-Job { & 'D:/projects/1/Hard-task1/.venv/Scripts/python.exe' 'D:/projects/1/Hard-task1/apps/api/tests/e2e_server.py' }; try { for ($i = 0; $i -lt 100; $i++) { if ((Test-NetConnection 127.0.0.1 -Port 8000 -InformationLevel Quiet)) { break }; Start-Sleep -Milliseconds 100 }; pnpm exec vite --host 127.0.0.1 --port 4173 --strictPort } finally { Stop-Job $api -ErrorAction SilentlyContinue; Remove-Job $api -Force -ErrorAction SilentlyContinue }\"`,
    port: 4173,
    reuseExistingServer: false,
  },
});
