import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin, HttpError } from "@/lib/http";

const schema = z.object({ status: z.enum(["accepted", "edited", "rejected"]), markdown: z.string().max(200000).optional() });
export async function PATCH(request: NextRequest, { params }: { params: Promise<{ id: string; sectionId: string }> }) {
  try {
    assertSameOrigin(request); await requireApiUser(); const { id, sectionId } = await params;
    const input = schema.parse(await request.json());
    if (input.status === "edited" && !input.markdown?.trim()) throw new HttpError(400, "Edited sections require Markdown");
    const editedMarkdown = input.status === "edited" ? (input.markdown ?? "") : null;
    const rows = await db()`
      update review_sections set status = ${input.status}, edited_markdown = ${editedMarkdown}, updated_at = now()
      where id = ${sectionId} and review_item_id = ${id} returning id, status, edited_markdown`;
    if (!rows[0]) throw new HttpError(404, "Review section not found");
    await db()`update review_items set status = 'in_review' where id = ${id} and status = 'pending'`;
    return NextResponse.json(rows[0]);
  } catch (error) { return apiError(error); }
}
