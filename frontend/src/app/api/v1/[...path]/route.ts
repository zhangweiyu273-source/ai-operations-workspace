import { NextRequest, NextResponse } from "next/server";

const upstreamBase =
  process.env.BACKEND_INTERNAL_URL ??
  (process.env.BACKEND_HOSTPORT ? `http://${process.env.BACKEND_HOSTPORT}/api/v1` : "http://localhost:8000/api/v1");

function readOnlyResponse() {
  return NextResponse.json(
    { error: { code: "READ_ONLY_ACCESS", message: "当前为只读访问，不能修改运营数据或系统配置。" } },
    { status: 403 },
  );
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const isReadRequest = request.method === "GET" || request.method === "HEAD";
  if (request.headers.get("x-ai-ops-role") === "viewer" && !isReadRequest) {
    return readOnlyResponse();
  }

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
