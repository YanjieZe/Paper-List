#!/usr/bin/env bash
set -euo pipefail

base_dir=${PAPER_OS_BASE:-/workspace/paper-list-research-os}
cloudflared_bin=${CLOUDFLARED_BIN:-/opt/instance-tools/bin/cloudflared}

[[ -x "$cloudflared_bin" ]] || { echo "cloudflared is not installed" >&2; exit 1; }
[[ -s "$base_dir/config/cloudflared.yml" ]] || { echo "cloudflared config is missing" >&2; exit 1; }
[[ -s "$base_dir/secrets/cloudflare-tunnel.json" ]] || { echo "tunnel credential is missing" >&2; exit 1; }

exec "$cloudflared_bin" tunnel \
  --config "$base_dir/config/cloudflared.yml" \
  --no-autoupdate \
  --metrics 127.0.0.1:0 \
  --loglevel info \
  run
