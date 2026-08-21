import { describe, expect, it, vi } from "vitest";

import { GET } from "./route";

describe("GET /api/access-status", () => {
  it("returns safe runtime configuration booleans only", async () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    const response = await GET();
    const payload = await response.json();

    expect(response.status).toBe(200);
    expect(response.headers.get("Cache-Control")).toBe("no-store");
    expect(payload).toMatchObject({
      enabled: true,
      adminConfigured: true,
      viewerConfigured: true,
      runtime: "nodejs",
    });
    expect(JSON.stringify(payload)).not.toContain("admin-secret");
    expect(JSON.stringify(payload)).not.toContain("viewer-secret");
  });
});
