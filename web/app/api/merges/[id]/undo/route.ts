import { NextRequest, NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin, HttpError } from "@/lib/http";

export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    assertSameOrigin(request);
    await requireApiUser();
    const { id } = await params;
    await db().begin(async (sql) => {
      const events = await sql`select * from merge_events where id = ${id} for update`;
      const event = events[0];
      if (!event) throw new HttpError(404, "Merge event does not exist");
      if (event.undone_at) throw new HttpError(409, "Merge event is already undone");
      const itemIds = event.before_snapshot?.source_item_ids ?? [];
      if (itemIds.length) await sql`update research_items set work_id = ${event.source_work_id} where id = any(${itemIds}::uuid[])`;
      await sql`update works set status = 'active', merged_into_id = null where id = ${event.source_work_id}`;
      await sql`update merge_events set undone_at = now() where id = ${id}`;
    });
    return NextResponse.json({ undone: true });
  } catch (error) { return apiError(error); }
}
