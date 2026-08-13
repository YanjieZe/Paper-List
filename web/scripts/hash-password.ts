import argon2 from "argon2";

async function main() {
  let password = process.argv[2];
  if (!password && !process.stdin.isTTY) {
    const chunks: Buffer[] = [];
    for await (const chunk of process.stdin) chunks.push(Buffer.from(chunk));
    password = Buffer.concat(chunks).toString("utf8").replace(/[\r\n]+$/, "");
  }
  if (!password) {
    process.stderr.write("Usage: read -s PAPER_PASSWORD; printf '%s' \"$PAPER_PASSWORD\" | npm --workspace web run hash-password\n");
    process.exit(1);
  }

  process.stdout.write(`${await argon2.hash(password, { type: argon2.argon2id })}\n`);
}

void main();
