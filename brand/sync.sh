#!/usr/bin/env bash
# Copy the canonical brand shell into the four repositories.
# The files in brand/sp-src are shared byte-for-byte: one change, four sites.
set -euo pipefail

BRAND=/oc/active/brand
REPOS=${REPOS:-"running cycling hiking"}
ROOT=/oc/active

for repo in $REPOS; do
  dst="$ROOT/$repo"
  [ -d "$dst" ] || { echo "skip $repo (not found)"; continue; }

  # shared components
  cp "$BRAND/sp-src/components/BrandMark.tsx" "$dst/src/components/BrandMark.tsx"
  cp "$BRAND/sp-src/components/SportIcon.tsx" "$dst/src/components/SportIcon.tsx"
  for dir in BrandNav Header Footer SiteHero Layout; do
    mkdir -p "$dst/src/components/$dir"
    cp "$BRAND/sp-src/components/$dir/"* "$dst/src/components/$dir/"
  done

  # tokens + specification
  cp "$BRAND/brand-tokens.css" "$dst/src/styles/brand-tokens.css"
  cp "$BRAND/BRAND_SYSTEM.md" "$dst/BRAND_SYSTEM.md"

  # shared self-hosted fonts (the main site's text faces)
  cp "$BRAND/fonts/"*.woff2 "$dst/public/fonts/"

  # brand assets, served as static files
  mkdir -p "$dst/public/brand/icons"
  cp "$BRAND/assets/active-logo.svg" "$BRAND/assets/active-mark.svg" \
     "$BRAND/assets/active-logo-light.svg" "$BRAND/assets/active-logo-dark.svg" \
     "$BRAND/assets/favicon.svg" "$BRAND/assets/zhubao-symbol.png" \
     "$BRAND/assets/favicon-32.png" "$BRAND/assets/favicon-64.png" \
     "$BRAND/assets/apple-touch-icon.png" "$BRAND/assets/icon-192.png" \
     "$BRAND/assets/icon-512.png" "$dst/public/brand/"
  cp "$BRAND/assets/icons/"*.svg "$dst/public/brand/icons/"

  echo "synced brand shell -> $repo"
done

# health keeps a native shell but the same tokens, spec and assets
HEALTH="$ROOT/health/dashboard"
if [ -d "$HEALTH" ]; then
  cp "$BRAND/brand-tokens.css" "$HEALTH/brand-tokens.css"
  cp "$BRAND/BRAND_SYSTEM.md" "$ROOT/health/BRAND_SYSTEM.md"
  cp "$BRAND/fonts/"*.woff2 "$HEALTH/fonts/"
  mkdir -p "$HEALTH/brand/icons"
  cp "$BRAND/assets/active-logo.svg" "$BRAND/assets/active-mark.svg" \
     "$BRAND/assets/active-logo-light.svg" "$BRAND/assets/active-logo-dark.svg" \
     "$BRAND/assets/favicon.svg" "$BRAND/assets/zhubao-symbol.png" \
     "$BRAND/assets/favicon-32.png" "$BRAND/assets/favicon-64.png" \
     "$BRAND/assets/apple-touch-icon.png" "$BRAND/assets/icon-192.png" \
     "$BRAND/assets/icon-512.png" "$HEALTH/brand/"
  cp "$BRAND/assets/icons/"*.svg "$HEALTH/brand/icons/"
  echo "synced brand shell -> health"
fi
