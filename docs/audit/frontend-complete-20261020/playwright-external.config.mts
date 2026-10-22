// Audit-only configuration: the evidence runner owns and reclaims both servers.
import baseline from "../../../apps/web/playwright.config.ts";

export default {
  ...baseline,
  testDir: "../../../apps/web/tests/e2e",
  webServer: undefined,
};
