"use client";

import { useState } from "react";
import { JobMonitor } from "@/components/job-monitor";

export function DeepReadButton({ itemId }: { itemId: string }) {
  const [jobId, setJobId] = useState<string>(); const [error, setError] = useState("");
  async function start() {
    setError(""); const response = await fetch(`/api/items/${itemId}/deep-read`, { method: "POST", headers: { "content-type": "application/json" }, body: "{}" });
    const body = await response.json(); if (!response.ok) return setError(body.error ?? "Unable to start"); setJobId(body.jobId);
  }
  return <div className="stack"><button className="button green" onClick={start}>Deep read · up to $5</button>{error && <div className="notice error">{error}</div>}{jobId && <JobMonitor jobId={jobId} />}</div>;
}
