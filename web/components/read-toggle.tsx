"use client";

import { useState } from "react";

export function ReadToggle({ itemId, initial }: { itemId: string; initial: "read" | "unread" }) {
  const [status, setStatus] = useState(initial);
  async function toggle() {
    const next = status === "read" ? "unread" : "read";
    const response = await fetch(`/api/items/${itemId}/read`, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ status: next }) });
    if (response.ok) setStatus(next);
  }
  return <button className="button secondary" onClick={toggle}>{status === "read" ? "Mark unread" : "Mark read"}</button>;
}
