# Deployment runbook

Production uses a dedicated Unix account, PostgreSQL database/user, and private storage directory. It does not share credentials or tables with the hiring system.

1. Create the `paper-os` service account, `/opt/paper-list`, `/var/lib/paper-os`, and `/etc/paper-os/paper-os.env` with mode `0600`.
2. Create a dedicated PostgreSQL role/database and enable the `vector`, `pgcrypto`, and `pg_trgm` extensions.
3. Install dependencies with `npm ci` and `uv sync --project worker --frozen`; run `npm run build`.
4. Export `DATABASE_URL` and run `uv run --project worker paper-worker migrate` followed by `legacy-import .`.
5. Copy and adapt the systemd units and Nginx config in `ops/`; replace the example hostname and configure TLS.
6. Configure an age recipient (preferred) or OpenSSL passphrase, local backup staging path, and optional rclone remote. Enable both application services and `paper-os-backup.timer`.
7. Before announcing production, create one backup and restore it into a disposable, empty database with `ops/restore-drill.sh`. The restore credential must be allowed to recreate PostgreSQL extensions such as `vector`; use a DBA credential for the drill and drop the disposable database afterward.

The service environment must include the three `OPENAI_AGENTS_*` privacy flags from `.env.example`. The app reads `OPENAI_API_KEY` only from its environment.
