#!/usr/bin/env bash
set -euo pipefail

base_dir=${PAPER_OS_BASE:-/workspace/paper-list-research-os}
repo_dir="$base_dir/repo"
hiring_env=/workspace/hiring-intelligence/config/production.env

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run bootstrap as root." >&2
  exit 1
fi
for required in "$repo_dir/.git" "$base_dir/config/production.env" \
  "$base_dir/secrets/database-password" "$base_dir/secrets/admin-password-hash" \
  "$base_dir/secrets/backup-passphrase" "$hiring_env"; do
  [[ -e "$required" ]] || { echo "Missing $required" >&2; exit 1; }
done

install -d -o yanjie -g yanjie -m 700 "$base_dir/config" "$base_dir/secrets" \
  "$base_dir/data/storage" "$base_dir/backups"
chmod 600 "$base_dir/config/production.env" "$base_dir/secrets/"*
chown -R yanjie:yanjie "$base_dir/config" "$base_dir/secrets" "$base_dir/data" "$base_dir/backups"

set -a
# shellcheck disable=SC1090
source "$hiring_env"
set +a
db_password="$(<"$base_dir/secrets/database-password")"
PGPASSWORD="$(<"$POSTGRES_SUPERUSER_PASSWORD_FILE")" psql \
  -v ON_ERROR_STOP=1 -v app_password="$db_password" \
  -h 127.0.0.1 -p 15432 -U postgres -d postgres <<'SQL'
select format('create role paper_os login password %L', :'app_password')
where not exists (select 1 from pg_roles where rolname = 'paper_os')
\gexec
alter role paper_os password :'app_password';
select 'create database paper_os owner paper_os'
where not exists (select 1 from pg_database where datname = 'paper_os')
\gexec
SQL
PGPASSWORD="$(<"$POSTGRES_SUPERUSER_PASSWORD_FILE")" psql \
  -v ON_ERROR_STOP=1 -h 127.0.0.1 -p 15432 -U postgres -d paper_os \
  -c "CREATE EXTENSION IF NOT EXISTS pgcrypto; CREATE EXTENSION IF NOT EXISTS vector; CREATE EXTENSION IF NOT EXISTS pg_trgm;"

set -a
# shellcheck disable=SC1090
source "$base_dir/config/production.env"
# shellcheck disable=SC1090
source /home/yanjie/yze-config/secrets/api.env
set +a
export DATABASE_URL="postgresql://paper_os:${db_password}@127.0.0.1:15432/paper_os"
export PAPER_ADMIN_PASSWORD_HASH="$(<"$base_dir/secrets/admin-password-hash")"

cd "$repo_dir"
. /opt/nvm/nvm.sh
runuser -u yanjie -- env PATH="$PATH" npm ci --include=dev
runuser -u yanjie -- env PATH="$PATH" /usr/local/bin/uv sync --project worker --frozen
runuser -u yanjie -- env PATH="$PATH" /usr/local/bin/uv run --project worker paper-worker migrate
runuser -u yanjie -- env PATH="$PATH" /usr/local/bin/uv run --project worker paper-worker legacy-import --root .
runuser -u yanjie -- env PATH="$PATH" npm run build

chmod 755 "$repo_dir/ops/vast/run-web.sh" "$repo_dir/ops/vast/run-worker.sh" \
  "$repo_dir/ops/vast/backup.sh"
install -m 644 "$repo_dir/ops/vast/paper-os-web.conf" /etc/supervisor/conf.d/paper-os-web.conf
install -m 644 "$repo_dir/ops/vast/paper-os-worker.conf" /etc/supervisor/conf.d/paper-os-worker.conf
install -m 644 "$repo_dir/ops/vast/paper-os-backup.cron" /etc/cron.d/paper-os-backup
supervisorctl reread
supervisorctl update

for attempt in $(seq 1 30); do
  if curl -fsS http://127.0.0.1:17171/api/health >/dev/null; then
    echo "Paper OS is healthy on 127.0.0.1:17171"
    exit 0
  fi
  sleep 1
done
echo "Paper OS failed its local health check." >&2
exit 1
