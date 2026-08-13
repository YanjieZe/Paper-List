"use client";

import { FormEvent, useState } from "react";
import { JobMonitor } from "@/components/job-monitor";

export function ImportForm() {
  const [jobId, setJobId] = useState<string>();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setLoading(true); setError(""); setJobId(undefined);
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/items/import", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ url: form.get("url"), context: form.get("context") || undefined }),
    });
    const body = await response.json(); setLoading(false);
    if (!response.ok) return setError(body.error ?? "Import failed");
    setJobId(body.jobId);
  }
  return (
    <div className="stack">
      <form className="card card-pad stack" onSubmit={submit}>
        <div className="field"><label>Research URL</label><input className="input" name="url" type="url" placeholder="arXiv, project page, blog, GitHub…" required /></div>
        <div className="field"><label>Why it caught your attention (optional)</label><input className="input" name="context" placeholder="和 VLA action representation 有关" /></div>
        <button className="button" disabled={loading}>{loading ? "Creating task…" : "Add to Inbox"}</button>
      </form>
      {error && <div className="notice error">{error}</div>}
      {jobId && <JobMonitor jobId={jobId} />}
    </div>
  );
}
