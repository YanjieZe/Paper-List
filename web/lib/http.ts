import { NextRequest, NextResponse } from "next/server";

export function assertSameOrigin(request: NextRequest) {
  const origin = request.headers.get("origin");
  const publicUrl = process.env.PAPER_PUBLIC_URL;
  if (!origin || !publicUrl) return;
  if (new URL(origin).origin !== new URL(publicUrl).origin) {
    throw new HttpError(403, "Cross-origin write rejected");
  }
}

export class HttpError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

export function apiError(error: unknown) {
  if (error instanceof HttpError) {
    return NextResponse.json({ error: error.message }, { status: error.status });
  }
  const message = error instanceof Error ? error.message : "Unexpected error";
  return NextResponse.json({ error: message }, { status: 500 });
}
