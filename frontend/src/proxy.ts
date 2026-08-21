import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { getAccessProtectionConfig, getAccessProtectionDiagnostics, type AccessProtectionConfig } from "@/lib/access-protection";

type AccessRole = "admin" | "viewer";

function unauthorized() {
  return new NextResponse("需要有效的访问账号与密码。", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="ai-ops-workbench", charset="UTF-8"' },
  });
}

function unavailable(config: AccessProtectionConfig) {
  console.error("Access protection server configuration is incomplete", {
    ...getAccessProtectionDiagnostics(config),
    execution: "src/proxy.ts:unavailable",
  });
  return new NextResponse("访问保护尚未完成服务器配置。", { status: 503 });
}

function resolveRole(request: NextRequest, config: AccessProtectionConfig): AccessRole | null {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Basic ")) return null;

  try {
    const [username, password] = atob(authorization.slice(6)).split(":", 2);
    if (username === "admin" && password === config.adminPassword) return "admin";
    if (username === "viewer" && password === config.viewerPassword) return "viewer";
  } catch {
    return null;
  }
  return null;
}

export function proxy(request: NextRequest) {
  const config = getAccessProtectionConfig();
  const requestHeaders = new Headers(request.headers);

  if (!config.enabled) {
    requestHeaders.set("x-ai-ops-role", "admin");
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  if (!config.adminPassword || !config.viewerPassword) {
    return unavailable(config);
  }

  const role = resolveRole(request, config);
  if (!role) return unauthorized();

  requestHeaders.set("x-ai-ops-role", role);
  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "same-origin");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|api/access-status).*)"],
};
