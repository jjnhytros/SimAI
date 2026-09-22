#!/usr/bin/env bash
# Installa gli hook Git locali (symlink in .git/hooks/).

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel)"
hook_src="$repo_root/scripts/hooks/commit-msg"
hook_dst="$repo_root/.git/hooks/commit-msg"

if [[ ! -f "$hook_src" ]]; then
    echo "❌ Hook sorgente non trovato: $hook_src"
    exit 1
fi

chmod +x "$hook_src"
ln -sf "$hook_src" "$hook_dst"
echo "✅ Hook installato: $hook_dst -> $hook_src"