import { expect, test } from "@playwright/test";

test("starts the isolated worktree API through the complete FastAPI lifespan", async ({ request }) => {
  const response = await request.get("/api/_e2e/lifecycle");

  expect(response.status()).toBe(200);
  expect(await response.json()).toEqual({
    lifespan: "started",
    clients: ["default", "desktop", "mobile"],
    application_count: 3,
  });
});
