import { createHash, randomBytes } from "node:crypto";
import argon2 from "argon2";
import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";
import { db } from "@/lib/db";
import { HttpError } from "@/lib/http";

const COOKIE_NAME = "paper_os_session";
const SESSION_DAYS = 30;

function tokenHash(value: string) {
  return createHash("sha256").update(value).digest("hex");
}

async function configuredAdmin() {
  const username = process.env.PAPER_ADMIN_USERNAME;
  const passwordHash = process.env.PAPER_ADMIN_PASSWORD_HASH;
  if (!username || !passwordHash) throw new Error("Admin login is not configured");
  const rows = await db()`
    insert into app_users (username, password_hash)
    values (${username.toLowerCase()}, ${passwordHash})
    on conflict (username) do update set password_hash = excluded.password_hash
    returning id, username, password_hash
  `;
  return rows[0] as { id: string; username: string; password_hash: string };
}

export async function login(username: string, password: string) {
  const admin = await configuredAdmin();
  if (username.toLowerCase() !== admin.username || !(await argon2.verify(admin.password_hash, password))) {
    throw new HttpError(401, "Invalid username or password");
  }
  const token = randomBytes(32).toString("base64url");
  const expiresAt = new Date(Date.now() + SESSION_DAYS * 24 * 60 * 60 * 1000);
  const requestHeaders = await headers();
  await db()`
    insert into sessions (user_id, token_hash, expires_at, user_agent)
    values (${admin.id}, ${tokenHash(token)}, ${expiresAt}, ${requestHeaders.get("user-agent")})
  `;
  const jar = await cookies();
  jar.set(COOKIE_NAME, token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    path: "/",
    expires: expiresAt,
  });
  return { id: admin.id, username: admin.username };
}

export async function logout() {
  const jar = await cookies();
  const token = jar.get(COOKIE_NAME)?.value;
  if (token) await db()`delete from sessions where token_hash = ${tokenHash(token)}`;
  jar.delete(COOKIE_NAME);
}

export async function currentUser() {
  const jar = await cookies();
  const token = jar.get(COOKIE_NAME)?.value;
  if (!token) return null;
  const rows = await db()`
    select u.id, u.username
    from sessions s join app_users u on u.id = s.user_id
    where s.token_hash = ${tokenHash(token)} and s.expires_at > now() and u.disabled_at is null
  `;
  if (!rows[0]) return null;
  await db()`update sessions set last_seen_at = now() where token_hash = ${tokenHash(token)}`;
  return rows[0] as { id: string; username: string };
}

export async function requireUser() {
  const user = await currentUser();
  if (!user) redirect("/login");
  return user;
}

export async function requireApiUser() {
  const user = await currentUser();
  if (!user) throw new HttpError(401, "Authentication required");
  return user;
}
