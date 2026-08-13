import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";
import { enqueueJob } from "@/lib/jobs";

const schema = z.object({
  query: z.string().min(3).max(12000),
  mode: z.enum(["standard", "deep"]).default("deep"),
  scope: z.literal("library_and_web").default("library_and_web"),
  conversationId: z.uuid().optional(),
  maxCostUsd: z.number().positive().max(100).optional(),
});
export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request); await requireApiUser(); const input = schema.parse(await request.json());
    const job = await enqueueJob("research", input, { idempotencyKey: `research:${crypto.randomUUID()}`, priority: 80 });
    return NextResponse.json({ jobId: job.id }, { status: 202 });
  } catch (error) { return apiError(error); }
}
