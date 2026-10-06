import { describe, expect, it } from "vitest";

import { languageWorlds, orbitRings } from "../../src/features/map/map-layout";


describe("map layout", () => {
  it("uses four stable non-overlapping orbital worlds and only transform-safe animation properties", () => {
    expect(languageWorlds.map((world) => world.id)).toEqual(["python", "java", "csharp", "cpp"]);
    expect(new Set(languageWorlds.map((world) => `${world.x}:${world.y}`)).size).toBe(4);
    expect(orbitRings).toEqual([28, 46, 72]);
  });
});
