import { NextRequest } from "next/server";
import { afterEach, describe, expect, it, vi } from "vitest";

import { proxy } from "./proxy";

const previous = {
  enabled: process.env.ACCESS_PROTECTION_ENABLED,
  admin: process.env.ADMIN_ACCESS_PASSWORD,
  viewer: process.env.VIEWER_ACCESS_PASSWORD,
};

afterEach(() => {
  vi.unstubAllEnvs();
  process.env.ACCESS_PROTECTION_ENABLED = previous.enabled;
  process.env.ADMIN_ACCESS_PASSWORD = previous.admin;
  process.env.VIEWER_ACCESS_PASSWORD = previous.viewer;
});

describe("production access protection", () => {
  it("does not enable password protection in local development", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "false");

    expect(proxy(new NextRequest("http://localhost:3000/data")).status).toBe(200);
  });

  it("requires credentials when production protection is enabled", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    const response = proxy(new NextRequest("https://workbench.example.com/data"));

    expect(response.status).toBe(401);
    expect(response.headers.get("WWW-Authenticate")).toContain("Basic");
  });

  it("sets the administrator role after valid administrator authentication", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    const credentials = Buffer.from("admin:admin-secret").toString("base64");
    const response = proxy(
      new NextRequest("https://workbench.example.com/data", {
        headers: { authorization: `Basic ${credentials}` },
      }),
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("x-middleware-request-x-ai-ops-role")).toBe("admin");
  });

  it("sets the viewer role after valid viewer authentication", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    const credentials = Buffer.from("viewer:viewer-secret").toString("base64");
    const response = proxy(
      new NextRequest("https://workbench.example.com/data", {
        headers: { authorization: `Basic ${credentials}` },
      }),
    );

    expect(response.status).toBe(200);
    expect(response.headers.get("x-middleware-request-x-ai-ops-role")).toBe("viewer");
  });

  it("rejects production access when required passwords are missing", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    expect(proxy(new NextRequest("https://workbench.example.com/data")).status).toBe(503);
  });
});
