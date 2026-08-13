import postgres, { type Sql } from "postgres";

let client: Sql | undefined;

export function db(): Sql {
  const url = process.env.DATABASE_URL;
  if (!url) throw new Error("DATABASE_URL is required");
  client ??= postgres(url, {
    max: 10,
    idle_timeout: 20,
    connect_timeout: 10,
    transform: { undefined: null },
  });
  return client;
}

export async function databaseHealth() {
  const started = Date.now();
  await db()`select 1 as ok`;
  return { connected: true, latencyMs: Date.now() - started };
}
