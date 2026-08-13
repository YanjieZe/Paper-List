import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";
import { enqueueJob } from "@/lib/jobs";

const schema = z.object({ maxCostUsd: z.number().positive().max(100).optional() });
export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    assertSameOrigin(request); await requireApiUser();
    const { id } = await params; const input = schema.parse(await request.json().catch(() => ({})));
    const job = await enqueueJob("deep_read", { researchItemId: id, ...input }, { idempotencyKey: `deep-read:${id}:${Date.now()}` });
    return NextResponse.json({ jobId: job.id }, { status: 202 });
  } catch (error) { return apiError(error); }
}
