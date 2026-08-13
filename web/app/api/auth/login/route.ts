import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { login } from "@/lib/auth";
import { apiError, assertSameOrigin } from "@/lib/http";

const schema = z.object({ email: z.email(), password: z.string().min(1).max(1024) });

export async function POST(request: NextRequest) {
  try {
    assertSameOrigin(request);
    const input = schema.parse(await request.json());
    const user = await login(input.email, input.password);
    return NextResponse.json({ user });
  } catch (error) { return apiError(error); }
}
