"use client";

import { FormEvent, useState } from "react";
import { JobMonitor } from "@/components/job-monitor";

export function ResearchForm() {
  const [jobId, setJobId] = useState<string>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setError(""); setJobId(undefined);
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/research", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ query: form.get("query"), mode: "deep", scope: "library_and_web" }),
    });
    const body = await response.json(); setLoading(false);
    if (!response.ok) return setError(body.error ?? "Research task failed");
    setJobId(body.jobId);
  }
  return (
    <div className="stack">
      <form className="card research-box" onSubmit={submit}>
        <textarea className="textarea" name="query" placeholder="问一个 Robotics 研究问题，例如：为什么 action chunking 对 VLA 很重要？" required />
        <button className="button green" disabled={loading}>{loading ? "Starting…" : "Research"}</button>
      </form>
      {error && <div className="notice error">{error}</div>}
      {jobId && <JobMonitor jobId={jobId} />}
    </div>
  );
}
