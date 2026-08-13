"use client";

import { useState } from "react";
import { JobMonitor } from "@/components/job-monitor";

type Section = { id: string; section_key: string; title: string; generated_markdown: string; edited_markdown: string | null; status: string; required: boolean };

export function ReviewEditor({ reviewId, sections: initial }: { reviewId: string; sections: Section[] }) {
  const [sections, setSections] = useState(initial); const [jobId, setJobId] = useState<string>(); const [error, setError] = useState("");
  async function decide(sectionId: string, status: "accepted" | "edited" | "rejected", markdown?: string) {
    setError(""); const response = await fetch(`/api/reviews/${reviewId}/sections/${sectionId}`, { method: "PATCH", headers: { "content-type": "application/json" }, body: JSON.stringify({ status, markdown }) });
    const body = await response.json(); if (!response.ok) return setError(body.error ?? "Update failed");
    setSections((current) => current.map((section) => section.id === sectionId ? { ...section, status, edited_markdown: status === "edited" ? markdown ?? null : null } : section));
  }
  async function publish() {
    setError(""); const response = await fetch(`/api/reviews/${reviewId}/publish`, { method: "POST" }); const body = await response.json();
    if (!response.ok) return setError(body.error ?? "Publish failed"); setJobId(body.jobId);
  }
  const unresolved = sections.filter((section) => section.required && section.status === "pending").length;
  return <div className="stack">
    {error && <div className="notice error">{error}</div>}
    {sections.map((section) => <ReviewSection key={section.id} section={section} onDecide={decide} />)}
    <section className="card card-pad row"><div><strong>{unresolved ? `${unresolved} required sections pending` : "Ready to publish"}</strong><div className="meta">Publication validates evidence, secrets and remote Git SHA.</div></div><button className="button green" disabled={unresolved > 0} onClick={publish}>Publish to main</button></section>
    {jobId && <JobMonitor jobId={jobId} />}
  </div>;
}

function ReviewSection({ section, onDecide }: { section: Section; onDecide: (id: string, status: "accepted" | "edited" | "rejected", markdown?: string) => Promise<void> }) {
  const [markdown, setMarkdown] = useState(section.edited_markdown ?? section.generated_markdown);
  return <section className="card review-section stack">
    <div className="row"><div><h2>{section.title}</h2><div className="meta"><span>{section.section_key}</span>{section.required && <span>required</span>}</div></div><span className={`badge ${section.status === "accepted" || section.status === "edited" ? "green" : section.status === "rejected" ? "red" : "amber"}`}>{section.status}</span></div>
    <textarea className="textarea" value={markdown} onChange={(event) => setMarkdown(event.target.value)} />
    <div className="row"><button className="button danger" onClick={() => onDecide(section.id, "rejected")}>Reject</button><div style={{ display: "flex", gap: 8 }}><button className="button secondary" onClick={() => onDecide(section.id, "edited", markdown)}>Save edit</button><button className="button green" onClick={() => onDecide(section.id, "accepted")}>Accept generated</button></div></div>
  </section>;
}
