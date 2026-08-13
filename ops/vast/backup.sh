#!/usr/bin/env bash
set -euo pipefail

base_dir=${PAPER_OS_BASE:-/workspace/paper-list-research-os}
set -a
# shellcheck disable=SC1090
source "$base_dir/config/production.env"
DATABASE_URL="postgresql://paper_os:$(<"$base_dir/secrets/database-password")@127.0.0.1:15432/paper_os"
PAPER_BACKUP_OPENSSL_PASSPHRASE="$(<"$base_dir/secrets/backup-passphrase")"
export DATABASE_URL PAPER_BACKUP_OPENSSL_PASSPHRASE
set +a
exec "$base_dir/repo/ops/backup.sh"
