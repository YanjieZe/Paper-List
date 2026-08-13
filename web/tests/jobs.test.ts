import assert from "node:assert/strict";
import test from "node:test";
import type { JobType } from "@/lib/jobs";

test("public job types remain explicit", () => {
  const values: JobType[] = ["ingest_url", "deep_read", "research", "publish_review", "reindex_markdown", "refresh_roadmap"];
  assert.equal(new Set(values).size, 6);
});
