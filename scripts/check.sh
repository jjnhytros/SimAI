#!/usr/bin/env bash

set -euo pipefail
unset VIRTUAL_ENV

cd "$(dirname "$0")/.."

# --- Argument parsing ----------------------------------------------------

WITH_TESTS=0
FAST=0

while (($# > 0)); do
    case "$1" in
        --with-tests) WITH_TESTS=1 ;;
        --fast)       FAST=1 ;;
        -h|--help)
            sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
            exit 0
            ;;
        *)
            echo "Unknown flag: $1" >&2
            echo "Try '$0 --help'." >&2
            exit 2
            ;;
    esac
    shift
done

if [[ "${simai_CHECK_WITH_TESTS:-0}" == "1" ]]; then
    WITH_TESTS=1
fi

# --- Helpers -------------------------------------------------------------

step() {
    echo
    echo "▶ $1"
}

done_msg() {
    echo
    echo "✅ All gates passed"
}

# --- 1. Cleanup ----------------------------------------------------------

step "Removing __pycache__ directories"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

step "Removing tool caches (.mypy_cache, .ruff_cache, .pytest_cache)"
rm -rf .mypy_cache .ruff_cache .pytest_cache

step "Removing temporary databases (/tmp/simai*.db, /tmp/test*.db)"
rm -vf /tmp/simai*.db /tmp/test*.db 2>/dev/null || true

# --- 2. Environment ------------------------------------------------------

if (( FAST )); then
    step "Skipping uv sync / uv lock (--fast)"
else
    step "Syncing dependencies (uv sync --all-extras)"
    uv sync --all-extras

    step "Updating lockfile (uv lock)"
    uv lock
fi

# --- 3. Sanity -----------------------------------------------------------

step "SimAI version"
uv run simai version

step "i18n parity (SimAI i18n check)"
uv run simai i18n check

# --- 4. Ruff (whole repository) ------------------------------------------

step "ruff check --fix ."
uv run ruff check --fix .

step "ruff format ."
uv run ruff format .

step "ruff check . (no-fix)"
uv run ruff check .

step "ruff format --check ."
uv run ruff format --check .

# --- 5. mypy -------------------------------------------------------------

step "mypy --strict src/simai/"
uv run mypy src/simai/

# --- 6. Tests (optional) -------------------------------------------------

if (( WITH_TESTS )); then
    step "pytest (full suite)"
    uv run pytest
else
    step "Skipping pytest (pass --with-tests to include it)"
fi

# --- Done ----------------------------------------------------------------

done_msg

step "setting up..."
unset VIRTUAL_ENV
rm -rf data/
uv run simai db upgrade
uv run simai world seed
