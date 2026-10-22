import { defineConfig } from "@playwright/test";
import { existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const e2eRunId = process.env.HARD_E2E_RUN_ID ?? `run-${Date.now()}`;
process.env.HARD_E2E_RUN_ID = e2eRunId;
const webRoot = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(webRoot, "../..");
const python = process.env.HARD_E2E_PYTHON ?? resolve(projectRoot, ".venv/Scripts/python.exe");
const e2eServer = resolve(projectRoot, "apps/api/tests/e2e_server.py");

if (!existsSync(python)) {
  throw new Error("HARD_E2E_PYTHON must point to an existing project Python runtime.");
}

export default defineConfig({
  testDir: "./tests/e2e",
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4173",
    launchOptions: { executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" },
  },
  webServer: {
    command: `powershell -NoProfile -Command \"$env:HARD_E2E_RUN_ID = '${e2eRunId}'; $api = Start-Job { & '${python.replaceAll("'", "''")}' '${e2eServer.replaceAll("'", "''")}' }; try { for ($i = 0; $i -lt 100; $i++) { if ((Test-NetConnection 127.0.0.1 -Port 8000 -InformationLevel Quiet)) { break }; Start-Sleep -Milliseconds 100 }; if (-not (Test-NetConnection 127.0.0.1 -Port 8000 -InformationLevel Quiet)) { throw 'E2E API failed to start.' }; & '${process.execPath.replaceAll("'", "''")}' '${resolve(webRoot, "node_modules/vite/bin/vite.js").replaceAll("'", "''")}' --host 127.0.0.1 --port 4173 --strictPort } finally { Stop-Job $api -ErrorAction SilentlyContinue; Remove-Job $api -Force -ErrorAction SilentlyContinue }\"`,
    port: 4173,
    reuseExistingServer: false,
  },
});
