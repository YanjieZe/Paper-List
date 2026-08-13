"use client";

import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";

type JobState = { status: string; progress: number; currentStage?: string; result?: Record<string, unknown>; error?: { message?: string } };

export function JobMonitor({ jobId }: { jobId: string }) {
  const [job, setJob] = useState<JobState>({ status: "queued", progress: 0 });
  useEffect(() => {
    const stream = new EventSource(`/api/jobs/${jobId}/events`);
    stream.onmessage = (event) => {
      const next = JSON.parse(event.data) as JobState;
      setJob(next);
      if (["succeeded", "failed", "dead", "cancelled"].includes(next.status)) stream.close();
    };
    stream.onerror = () => stream.close();
    return () => stream.close();
  }, [jobId]);
  const answer = job.result?.answer as { conclusion?: string; explanation_markdown?: string } | undefined;
  return (
    <section className="card card-pad stack">
      <div className="row"><strong>{job.currentStage ?? "Queued"}</strong><span className="badge">{job.status}</span></div>
      <div className="progress"><span style={{ width: `${job.progress ?? 0}%` }} /></div>
      {job.error?.message && <div className="notice error">{job.error.message}</div>}
      {answer && <div className="markdown"><h2>{answer.conclusion}</h2><ReactMarkdown>{answer.explanation_markdown ?? ""}</ReactMarkdown></div>}
      {typeof job.result?.reviewId === "string" && <a className="button green" href={`/reviews/${job.result.reviewId}`}>Review reading note</a>}
    </section>
  );
}
