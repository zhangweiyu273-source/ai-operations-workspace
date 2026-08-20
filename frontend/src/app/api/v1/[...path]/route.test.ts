import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { POST } from "./route";

describe("same-origin API proxy access control", () => {
  it("blocks viewer write requests before calling FastAPI", async () => {
    const request = new NextRequest("http://localhost:3000/api/v1/accounts", {
      method: "POST",
      headers: { "x-ai-ops-role": "viewer" },
    });

    const response = await POST(request, { params: Promise.resolve({ path: ["accounts"] }) });

    expect(response.status).toBe(403);
    await expect(response.json()).resolves.toMatchObject({ error: { code: "READ_ONLY_ACCESS" } });
  });
});
