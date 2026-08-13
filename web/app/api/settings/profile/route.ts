import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError, assertSameOrigin } from "@/lib/http";

const schema = z.object({ markdown: z.string().max(100000) });
export async function PUT(request: NextRequest) {
  try {
    assertSameOrigin(request); const user = await requireApiUser(); const input = schema.parse(await request.json());
    const rows = await db()`
      insert into research_profiles (user_id, markdown) values (${user.id}, ${input.markdown})
      on conflict (user_id) do update set markdown = excluded.markdown, version = research_profiles.version + 1, updated_at = now()
      returning id, version, updated_at`;
    return NextResponse.json(rows[0]);
  } catch (error) { return apiError(error); }
}
