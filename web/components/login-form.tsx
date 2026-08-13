"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

export function LoginForm() {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true); setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ email: form.get("email"), password: form.get("password") }),
    });
    const body = await response.json();
    setLoading(false);
    if (!response.ok) return setError(body.error ?? "Login failed");
    router.push("/"); router.refresh();
  }

  return (
    <form className="stack" onSubmit={submit}>
      {error && <div className="notice error">{error}</div>}
      <div className="field"><label>Email</label><input className="input" name="email" type="email" required /></div>
      <div className="field"><label>Password</label><input className="input" name="password" type="password" required /></div>
      <button className="button green" disabled={loading}>{loading ? "Signing in…" : "Enter Research OS"}</button>
    </form>
  );
}
