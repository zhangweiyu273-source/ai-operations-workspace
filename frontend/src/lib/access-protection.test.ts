import { afterEach, describe, expect, it, vi } from "vitest";

import { getAccessProtectionDiagnostics } from "./access-protection";

const previous = {
  enabled: process.env.ACCESS_PROTECTION_ENABLED,
  admin: process.env.ADMIN_ACCESS_PASSWORD,
  viewer: process.env.VIEWER_ACCESS_PASSWORD,
  runtime: process.env.NEXT_RUNTIME,
};

afterEach(() => {
  vi.unstubAllEnvs();
  process.env.ACCESS_PROTECTION_ENABLED = previous.enabled;
  process.env.ADMIN_ACCESS_PASSWORD = previous.admin;
  process.env.VIEWER_ACCESS_PASSWORD = previous.viewer;
  process.env.NEXT_RUNTIME = previous.runtime;
});

describe("access protection runtime diagnostics", () => {
  it("reports configured production credentials without exposing their values", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");
    vi.stubEnv("NEXT_RUNTIME", "nodejs");

    expect(getAccessProtectionDiagnostics()).toMatchObject({
      enabled: true,
      adminConfigured: true,
      viewerConfigured: true,
      runtime: "nodejs",
    });
  });

  it("reports a missing administrator password", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "viewer-secret");

    expect(getAccessProtectionDiagnostics()).toMatchObject({
      enabled: true,
      adminConfigured: false,
      viewerConfigured: true,
    });
  });

  it("reports a missing viewer password", () => {
    vi.stubEnv("ACCESS_PROTECTION_ENABLED", "true");
    vi.stubEnv("ADMIN_ACCESS_PASSWORD", "admin-secret");
    vi.stubEnv("VIEWER_ACCESS_PASSWORD", "");

    expect(getAccessProtectionDiagnostics()).toMatchObject({
      enabled: true,
      adminConfigured: true,
      viewerConfigured: false,
    });
  });
});
