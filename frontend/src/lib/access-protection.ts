export type AccessProtectionConfig = {
  enabled: boolean;
  adminPassword?: string;
  viewerPassword?: string;
};

export type AccessProtectionDiagnostics = {
  enabled: boolean;
  adminConfigured: boolean;
  viewerConfigured: boolean;
  runtime: string;
  nodeEnv: string | null;
};

export function getAccessProtectionConfig(): AccessProtectionConfig {
  // Computed access keeps these server-only values runtime-resolved in Docker hosts.
  // Do not rename them with NEXT_PUBLIC_: credentials must never enter the browser bundle.
  const environment = process.env;
  return {
    enabled: environment["ACCESS_PROTECTION_ENABLED"] === "true",
    adminPassword: environment["ADMIN_ACCESS_PASSWORD"],
    viewerPassword: environment["VIEWER_ACCESS_PASSWORD"],
  };
}

export function getAccessProtectionDiagnostics(
  config: AccessProtectionConfig = getAccessProtectionConfig(),
): AccessProtectionDiagnostics {
  const environment = process.env;
  return {
    enabled: config.enabled,
    adminConfigured: Boolean(config.adminPassword),
    viewerConfigured: Boolean(config.viewerPassword),
    runtime: environment["NEXT_RUNTIME"] ?? "nodejs",
    nodeEnv: environment["NODE_ENV"] ?? null,
  };
}
