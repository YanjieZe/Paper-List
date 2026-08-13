import { NextRequest, NextResponse } from "next/server";
import { logout } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";

export async function POST(request: NextRequest) {
  try { assertSameOrigin(request); await logout(); return NextResponse.json({ ok: true }); }
  catch (error) { return apiError(error); }
}
