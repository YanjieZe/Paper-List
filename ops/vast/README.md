# Vast.ai production layout

All persistent state lives under `/workspace/paper-list-research-os`:

- `repo/`: clean checkout of `origin/main`
- `config/production.env`: non-secret runtime configuration (`0600`)
- `secrets/`: database/admin/backup secret files (`0600`)
- `data/storage/`: private PDF and HTML evidence
- `backups/`: encrypted backup archives

Supervisor manages `paper-os-web` and `paper-os-worker`. The web app listens only on
`127.0.0.1:17171`; a named Cloudflare Tunnel public hostname routes to that origin.
Cloudflare Access should protect the complete hostname in addition to the application's
single-user Argon2id login.

Run `bootstrap.sh` as root after the production checkout and secret/config files exist.
The script creates an independent PostgreSQL role/database on the existing local PostgreSQL
daemon, runs migrations and the auditable legacy import, builds the app, and installs services.
