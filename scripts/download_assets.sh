#!/usr/bin/env bash
# Scarica gli asset UI in simai/ui/static/ (una volta sola).
#
# I file NON vengono serviti da CDN: dopo questo script, l'app li carica
# dal disco locale. Richiede connessione internet solo la prima volta.

set -euo pipefail

cd "$(dirname "$0")/.."

STATIC="simai/ui/static"
CSS="${STATIC}/css"
JS="${STATIC}/js"
FONTS="${CSS}/fonts"

mkdir -p "$CSS" "$JS" "$FONTS"

echo "▶ Bootstrap 5.3"
curl -fsSL -o "$CSS/bootstrap.min.css" \
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
curl -fsSL -o "$JS/bootstrap.bundle.min.js" \
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"

echo "▶ Bootstrap Icons 1.13"
curl -fsSL -o "$CSS/bootstrap-icons.css" \
    "https://raw.githubusercontent.com/twbs/icons/refs/heads/main/font/bootstrap-icons.min.css"
curl -fsSL -o "$FONTS/bootstrap-icons.woff2" \
    "https://github.com/twbs/icons/raw/refs/heads/main/font/fonts/bootstrap-icons.woff2"
curl -fsSL -o "$FONTS/bootstrap-icons.woff" \
    "https://github.com/twbs/icons/raw/refs/heads/main/font/fonts/bootstrap-icons.woff"

echo "▶ htmx 2.0.10"
curl -fsSL -o "$JS/htmx.min.js" \
    "https://unpkg.com/htmx.org@2.0.10/dist/htmx.min.js"

echo "▶ Alpine.js 3.17.4"
curl -fsSL -o "$JS/alpine.min.js" \
    "https://cdn.jsdelivr.net/npm/alpinejs@3.17.4/dist/cdn.min.js"

echo "▶ D3.js 7.9.0"
curl -fsSL -o "$JS/d3.min.js" \
    "https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"

echo "▶ Chart.js 4"
curl -fsSL -o "$JS/chart.umd.min.js" \
    "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"

echo ""
echo "✅ Asset scaricati in ${STATIC}/"
echo ""
ls -lh "$CSS" "$JS"