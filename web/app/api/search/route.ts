import { NextRequest, NextResponse } from "next/server";
import { requireApiUser } from "@/lib/auth";
import { db } from "@/lib/db";
import { apiError } from "@/lib/http";

export async function GET(request: NextRequest) {
  try {
    await requireApiUser(); const query = request.nextUrl.searchParams.get("q")?.trim() ?? "";
    if (!query) return NextResponse.json({ results: [] });
    const results = await db()`
      select ri.id, ri.title, ri.item_type, ri.year, ri.reading_status, ri.lifecycle_status,
        greatest(similarity(ri.title, ${query}), case when ri.title ilike ${`%${query}%`} then 1 else 0 end) as score
      from research_items ri where ri.title ilike ${`%${query}%`} or coalesce(ri.abstract, '') ilike ${`%${query}%`}
      order by score desc, ri.year desc nulls last limit 30`;
    return NextResponse.json({ results });
  } catch (error) { return apiError(error); }
}
