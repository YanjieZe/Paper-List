import { NextResponse } from "next/server";
import { databaseHealth } from "@/lib/db";

export async function GET() {
  try { return NextResponse.json({ ok: true, database: await databaseHealth() }); }
  catch (error) { return NextResponse.json({ ok: false, database: { connected: false }, error: error instanceof Error ? error.message : "unknown" }, { status: 503 }); }
}
