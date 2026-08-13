import { NextRequest, NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";
import { enqueueJob } from "@/lib/jobs";

export async function POST(request: NextRequest, { params }: { params: Promise<{ id: string }> }) {
  try {
    assertSameOrigin(request); await requireApiUser(); const { id } = await params;
    const job = await enqueueJob("publish_review", { reviewId: id }, { idempotencyKey: `publish:${id}`, priority: 50 });
    return NextResponse.json({ jobId: job.id }, { status: 202 });
  } catch (error) { return apiError(error); }
}
