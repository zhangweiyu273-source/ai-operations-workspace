import { NextRequest, NextResponse } from "next/server";

const upstreamBase = process.env.BACKEND_INTERNAL_URL ?? "http://localhost:8000/api/v1";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(`${upstreamBase}/${path.join("/")}`);
  target.search = request.nextUrl.search;
  const body =
    request.method === "GET" || request.method === "HEAD"
      ? undefined
      : await request.arrayBuffer();

  try {
    const response = await fetch(target, {
      method: request.method,
      body,
      headers: {
        "Content-Type": request.headers.get("Content-Type") ?? "application/json",
        ...(request.headers.get("X-Organization-ID")
          ? { "X-Organization-ID": request.headers.get("X-Organization-ID")! }
          : {}),
      },
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    });
    return new NextResponse(response.body, {
      status: response.status,
      headers: {
        "Content-Type": response.headers.get("Content-Type") ?? "application/json",
        ...(response.headers.get("X-Request-ID")
          ? { "X-Request-ID": response.headers.get("X-Request-ID")! }
          : {}),
      },
    });
  } catch {
    return NextResponse.json(
      { error: { code: "UPSTREAM_UNAVAILABLE", message: "后端服务暂时不可用" } },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const DELETE = proxy;
