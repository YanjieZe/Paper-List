import { randomUUID } from "node:crypto";
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin } from "@/lib/http";
import { enqueueJob } from "@/lib/jobs";

const schema = z.object({ url: z.url(), context: z.string().max(2000).optional() });

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request); await requireApiUser();
    const input = schema.parse(await request.json());
    const existing = await db()`select id from research_items where canonical_url = ${input.url} limit 1`;
    if (existing[0]) {
      const job = await enqueueJob("ingest_url", { url: input.url, context: input.context, candidateItemId: existing[0].id }, { idempotencyKey: `ingest:${input.url}` });
      return NextResponse.json({ jobId: job.id, candidateItemId: existing[0].id }, { status: 202 });
    }
    const itemId = randomUUID(); const workId = randomUUID();
    const hostname = new URL(input.url).hostname.replace(/^www\./, "");
    const slug = `candidate-${itemId.slice(0, 8)}`;
    await db().begin(async (sql) => {
      await sql`insert into works (id, canonical_title, slug) values (${workId}, ${`Pending · ${hostname}`}, ${slug})`;
      await sql`insert into research_items (id, work_id, item_type, title, canonical_url, source_kind, added_context)
        values (${itemId}, ${workId}, 'project', ${`Pending · ${hostname}`}, ${input.url}, 'user', ${input.context ?? null})`;
    });
    const job = await enqueueJob("ingest_url", { url: input.url, context: input.context, candidateItemId: itemId }, { idempotencyKey: `ingest:${input.url}` });
    return NextResponse.json({ jobId: job.id, candidateItemId: itemId }, { status: 202 });
  } catch (error) { return apiError(error); }
}
