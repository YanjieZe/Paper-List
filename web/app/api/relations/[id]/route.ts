import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin, HttpError } from "@/lib/http";

const schema = z.object({ status: z.enum(["accepted", "rejected"]) });

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    assertSameOrigin(request);
    await requireApiUser();
    const { id } = await params;
    const input = schema.parse(await request.json());
    const rows = await db()`update relations set review_status=${input.status} where id=${id} returning id, review_status`;
    if (!rows[0]) throw new HttpError(404, "Relation does not exist");
    return NextResponse.json(rows[0]);
  } catch (error) { return apiError(error); }
}
