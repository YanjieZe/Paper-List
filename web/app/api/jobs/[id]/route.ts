import { NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError } from "@/lib/http";

export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  try { await requireApiUser(); const { id } = await params; const rows = await db()`select * from jobs where id = ${id}`; return NextResponse.json(rows[0] ?? null, { status: rows[0] ? 200 : 404 }); }
  catch (error) { return apiError(error); }
}
