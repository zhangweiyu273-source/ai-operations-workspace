import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiClient, apiRequest } from "./client";

afterEach(() => vi.unstubAllGlobals());

describe("apiClient", () => {
  it("returns typed JSON for a successful response", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "ok" }))));
    await expect(apiClient.get<{ status: string }>("/health/live")).resolves.toEqual({ status: "ok" });
  });

  it("normalizes API error responses", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ error: { code: "NOT_FOUND", message: "missing", request_id: "req-1" } }),
      { status: 404, headers: { "Content-Type": "application/json" } },
    )));
    await expect(apiClient.get("/missing")).rejects.toEqual(
      new ApiError("missing", 404, "NOT_FOUND", "req-1"),
    );
  });

  it("lets the browser set multipart boundaries for FormData", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ ok: true })));
    vi.stubGlobal("fetch", fetchMock);
    const body = new FormData();
    body.append("file", new File(["data"], "data.csv"));
    await apiRequest("/import", { method: "POST", body });
    expect(fetchMock.mock.calls[0][1].headers).not.toHaveProperty("Content-Type");
  });
});
