#!/usr/bin/env bash
# Esegue tutti i gate di qualità in sequenza. Stop al primo errore.
clear

set -euo pipefail

cd "$(dirname "$0")/.."

find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo "▶ removed __pcache__"

rm -rf .mypy_cache
echo "▶ removed .mypy_cache"

echo "▶ ruff check --fix"
uv run ruff check --fix .

echo "▶ ruff format"
uv run ruff format .

echo "▶ ruff check"
uv run ruff check .

echo "▶ ruff format --check"
uv run ruff format --check .

echo "▶ mypy"
uv run mypy simai/

echo "✅ Tutti i gate passati"