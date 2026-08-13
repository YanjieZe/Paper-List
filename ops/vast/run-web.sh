#!/usr/bin/env bash
set -euo pipefail

base_dir=${PAPER_OS_BASE:-/workspace/paper-list-research-os}
set -a
# shellcheck disable=SC1090
source "$base_dir/config/production.env"
# shellcheck disable=SC1090
source /home/yanjie/yze-config/secrets/api.env
set +a
export DATABASE_URL="postgresql://paper_os:$(<"$base_dir/secrets/database-password")@127.0.0.1:15432/paper_os"
export PAPER_ADMIN_PASSWORD_HASH="$(<"$base_dir/secrets/admin-password-hash")"
. /opt/nvm/nvm.sh
cd "$base_dir/repo"
exec npm --workspace web start -- --hostname 127.0.0.1 --port 17171
