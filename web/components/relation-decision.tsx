"use client";

import { useState } from "react";

export function RelationDecision({ id, initial }: { id: string; initial: string }) {
  const [status, setStatus] = useState(initial);
  const [error, setError] = useState("");
  async function decide(next: "accepted" | "rejected") {
    setError("");
    const response = await fetch(`/api/relations/${id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ status: next }),
    });
    const body = await response.json();
    if (!response.ok) return setError(body.error ?? "Relation review failed");
    setStatus(next);
  }
  return <div className="stack">
    <div className="row"><span className="badge">{status}</span>{status === "pending" && <div style={{display:"flex",gap:8}}><button className="button danger" onClick={() => decide("rejected")}>Reject</button><button className="button green" onClick={() => decide("accepted")}>Accept</button></div>}</div>
    {error && <div className="notice error">{error}</div>}
  </div>;
}
