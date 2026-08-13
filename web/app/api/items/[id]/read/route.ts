import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin } from "@/lib/http";

const schema = z.object({ status: z.enum(["read", "unread"]) });
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    assertSameOrigin(request); await requireApiUser(); const { id } = await params;
    const input = schema.parse(await request.json());
    const rows = await db()`update research_items set reading_status = ${input.status} where id = ${id} returning reading_status`;
    return NextResponse.json(rows[0]);
  } catch (error) { return apiError(error); }
}
