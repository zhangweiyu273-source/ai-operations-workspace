import { NextResponse } from "next/server";

import { getAccessProtectionDiagnostics } from "@/lib/access-protection";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

/**
 * Temporary production-safe diagnostic endpoint for Railway access protection.
 * It intentionally exposes configuration booleans only, never secret values.
 */
export async function GET() {
  return NextResponse.json(getAccessProtectionDiagnostics(), {
    headers: { "Cache-Control": "no-store" },
  });
}
