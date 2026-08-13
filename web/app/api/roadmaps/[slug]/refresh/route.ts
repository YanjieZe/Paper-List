import { NextRequest, NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";
import { enqueueJob } from "@/lib/jobs";

export async function POST(request: NextRequest, { params }: { params: Promise<{ slug: string }> }) {
  try {
    assertSameOrigin(request); await requireApiUser(); const { slug } = await params;
    const job = await enqueueJob("refresh_roadmap", { slug }, { idempotencyKey: `roadmap:${slug}:${Date.now()}`, priority: 90 });
    return NextResponse.json({ jobId: job.id }, { status: 202 });
  } catch (error) { return apiError(error); }
}
