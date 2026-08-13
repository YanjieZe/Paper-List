#!/usr/bin/env bash
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${PAPER_STORAGE_DIR:?PAPER_STORAGE_DIR is required}"
: "${PAPER_REPOSITORY_ROOT:?PAPER_REPOSITORY_ROOT is required}"
: "${PAPER_BACKUP_DIR:?PAPER_BACKUP_DIR is required}"

backup_stamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_tmp="$(mktemp -d)"
trap 'rm -rf -- "$backup_tmp"' EXIT

pg_dump --format=custom --no-owner --no-acl --dbname="$DATABASE_URL" --file="$backup_tmp/database.dump"
git -C "$PAPER_REPOSITORY_ROOT" rev-parse HEAD > "$backup_tmp/git-sha.txt"
(cd "$PAPER_STORAGE_DIR" && find . -type f -print0 | sort -z | xargs -0 -r sha256sum) > "$backup_tmp/storage-sha256.txt"
tar -C "$PAPER_STORAGE_DIR" -czf "$backup_tmp/storage.tar.gz" .
(cd "$backup_tmp" && sha256sum database.dump storage.tar.gz git-sha.txt) > "$backup_tmp/manifest.sha256"

mkdir -p "$PAPER_BACKUP_DIR"
if [[ -n "${PAPER_BACKUP_AGE_RECIPIENT:-}" ]]; then
  command -v age >/dev/null || { echo "age is required for age-recipient backups" >&2; exit 1; }
  archive="$PAPER_BACKUP_DIR/paper-os-$backup_stamp.tar.age"
  tar -C "$backup_tmp" -cf - database.dump storage.tar.gz storage-sha256.txt git-sha.txt manifest.sha256 \
    | age --recipient "$PAPER_BACKUP_AGE_RECIPIENT" --output "$archive"
else
  : "${PAPER_BACKUP_OPENSSL_PASSPHRASE:?Configure an age recipient or an OpenSSL passphrase}"
  archive="$PAPER_BACKUP_DIR/paper-os-$backup_stamp.tar.enc"
  tar -C "$backup_tmp" -cf - database.dump storage.tar.gz storage-sha256.txt git-sha.txt manifest.sha256 \
    | openssl enc -aes-256-cbc -pbkdf2 -salt -pass env:PAPER_BACKUP_OPENSSL_PASSPHRASE -out "$archive"
fi

if [[ -n "${PAPER_BACKUP_RCLONE_REMOTE:-}" ]]; then
  rclone copyto "$archive" "$PAPER_BACKUP_RCLONE_REMOTE/$(basename "$archive")"
fi

echo "$archive"
