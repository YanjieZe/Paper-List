import { NextRequest, NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin, HttpError } from "@/lib/http";

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request);
    await requireApiUser();
    const body = await request.json();
    const { targetWorkId, sourceWorkId, reason, confidence = 1, evidence = [] } = body;
    if (!targetWorkId || !sourceWorkId || !reason) throw new HttpError(400, "targetWorkId, sourceWorkId, and reason are required");
    if (targetWorkId === sourceWorkId) throw new HttpError(400, "A Work cannot be merged into itself");
    if (confidence < 0 || confidence > 1) throw new HttpError(400, "confidence must be between 0 and 1");
    const result = await db().begin(async (sql) => {
      const works = await sql`select id, canonical_title, slug, status, merged_into_id from works where id in (${targetWorkId}, ${sourceWorkId}) for update`;
      if (works.length !== 2) throw new HttpError(404, "Both Works must exist");
      const source = works.find((work) => work.id === sourceWorkId);
      if (source?.status === "merged") throw new HttpError(409, "Source Work is already merged");
      const items = await sql`select id from research_items where work_id = ${sourceWorkId}`;
      const before = { works, source_item_ids: items.map((item) => item.id) };
      await sql`update research_items set work_id = ${targetWorkId} where work_id = ${sourceWorkId}`;
      await sql`update works set status = 'merged', merged_into_id = ${targetWorkId} where id = ${sourceWorkId}`;
      const events = await sql`
        insert into merge_events (target_work_id, source_work_id, reason, confidence, evidence, before_snapshot, after_snapshot)
        values (${targetWorkId}, ${sourceWorkId}, ${reason}, ${confidence}, ${sql.json(evidence)}, ${sql.json(before)}, ${sql.json({ target_work_id: targetWorkId, source_work_id: sourceWorkId })})
        returning id
      `;
      return events[0];
    });
    return NextResponse.json({ mergeEventId: result.id }, { status: 201 });
  } catch (error) { return apiError(error); }
}
