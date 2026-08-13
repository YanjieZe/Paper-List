#!/usr/bin/env bash
set -euo pipefail

: "${1:?usage: restore-drill.sh BACKUP.tar.age-or-enc}"
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL must point to an empty drill database}"

archive="$1"
restore_tmp="$(mktemp -d)"
trap 'rm -rf -- "$restore_tmp"' EXIT

case "$archive" in
  *.age)
    : "${PAPER_BACKUP_AGE_IDENTITY:?PAPER_BACKUP_AGE_IDENTITY is required}"
    age --decrypt --identity "$PAPER_BACKUP_AGE_IDENTITY" "$archive" | tar -C "$restore_tmp" -xf -
    ;;
  *.enc)
    : "${PAPER_BACKUP_OPENSSL_PASSPHRASE:?PAPER_BACKUP_OPENSSL_PASSPHRASE is required}"
    openssl enc -d -aes-256-cbc -pbkdf2 -pass env:PAPER_BACKUP_OPENSSL_PASSPHRASE -in "$archive" | tar -C "$restore_tmp" -xf -
    ;;
  *) echo "unsupported encrypted archive suffix" >&2; exit 1 ;;
esac
(cd "$restore_tmp" && sha256sum --check manifest.sha256)
pg_restore --clean --if-exists --no-owner --no-acl --dbname="$RESTORE_DATABASE_URL" "$restore_tmp/database.dump"
psql "$RESTORE_DATABASE_URL" -v ON_ERROR_STOP=1 -c "select count(*) as migration_records from migration_records; select count(*) as research_items from research_items; select count(*) as document_versions from document_versions;"
mkdir "$restore_tmp/restored-storage"
tar -C "$restore_tmp/restored-storage" -xzf "$restore_tmp/storage.tar.gz"
if [[ -s "$restore_tmp/storage-sha256.txt" ]]; then
  (cd "$restore_tmp/restored-storage" && sha256sum --check "$restore_tmp/storage-sha256.txt")
fi

echo "restore drill passed"
