import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

type AccessRole = "admin" | "viewer";

function unauthorized() {
  return new NextResponse("需要有效的访问账号与密码。", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="ai-ops-workbench", charset="UTF-8"' },
  });
}

function unavailable() {
  return new NextResponse("访问保护尚未完成服务器配置。", { status: 503 });
}

function resolveRole(request: NextRequest): AccessRole | null {
  const authorization = request.headers.get("authorization");
  if (!authorization?.startsWith("Basic ")) return null;

  try {
    const [username, password] = atob(authorization.slice(6)).split(":", 2);
    if (username === "admin" && password === process.env.ADMIN_ACCESS_PASSWORD) return "admin";
    if (username === "viewer" && password === process.env.VIEWER_ACCESS_PASSWORD) return "viewer";
  } catch {
    return null;
  }
  return null;
}

export function proxy(request: NextRequest) {
  const protectionEnabled = process.env.ACCESS_PROTECTION_ENABLED === "true";
  const requestHeaders = new Headers(request.headers);

  if (!protectionEnabled) {
    requestHeaders.set("x-ai-ops-role", "admin");
    return NextResponse.next({ request: { headers: requestHeaders } });
  }

  if (!process.env.ADMIN_ACCESS_PASSWORD || !process.env.VIEWER_ACCESS_PASSWORD) {
    return unavailable();
  }

  const role = resolveRole(request);
  if (!role) return unauthorized();

  requestHeaders.set("x-ai-ops-role", role);
  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("Referrer-Policy", "same-origin");
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
