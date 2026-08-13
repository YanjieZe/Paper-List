import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";
export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  await requireApiUser(); const { id } = await params; const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      let closed = false;
      request.signal.addEventListener("abort", () => { closed = true; try { controller.close(); } catch {} });
      while (!closed) {
        const rows = await db()`select status, progress, current_stage, result, error from jobs where id = ${id}`;
        if (!rows[0]) { controller.enqueue(encoder.encode(`data: ${JSON.stringify({ status: "missing", progress: 0 })}\n\n`)); controller.close(); break; }
        const job = rows[0];
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ status: job.status, progress: Number(job.progress), currentStage: job.current_stage, result: job.result, error: job.error })}\n\n`));
        if (["succeeded", "failed", "dead", "cancelled"].includes(String(job.status))) { controller.close(); break; }
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    },
  });
  return new Response(stream, { headers: { "content-type": "text/event-stream", "cache-control": "no-cache, no-transform", connection: "keep-alive" } });
}
