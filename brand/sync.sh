#!/usr/bin/env bash
# Copy the canonical brand shell into the four repositories.
# The files in brand/sp-src are shared byte-for-byte: one change, four sites.
set -euo pipefail

# Works from either location: the workspace brand/ dir or the active-watch
# checkout (https://github.com/zhubao315/active-watch). The four site repos
# are expected next to the parent dir of this script; override with ACTIVE_ROOT.
BRAND=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPOS=${REPOS:-"running cycling hiking"}
ROOT=${ACTIVE_ROOT:-$(dirname "$BRAND")}

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
  cp "$BRAND/assets/zhubao-"*.png "$BRAND/assets/zhubao-slices-manifest.json" \
     "$BRAND/assets/README-STRICT-SLICES.md" "$dst/public/brand/"
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
  cp "$BRAND/assets/zhubao-"*.png "$BRAND/assets/zhubao-slices-manifest.json" \
     "$BRAND/assets/README-STRICT-SLICES.md" "$HEALTH/brand/"
  cp "$BRAND/assets/icons/"*.svg "$HEALTH/brand/icons/"
  echo "synced brand shell -> health"
fi

# Regenerate each repo's checksum manifest — the Brand Guard workflow fails
# when a shared asset is hand-edited without going through this script.
gen_manifest() { # $1 = repo dir, $2 = site key
  local dst=$1 site=$2
  ( cd "$dst" && export LC_ALL=C && {
      if [ "$site" = health ]; then
        find dashboard/brand -type f ! -name 'hero-*.webp' ! -name "og-${site}.png"
        find dashboard/fonts -maxdepth 1 -type f -name '*.woff2'
        printf '%s\n' BRAND_SYSTEM.md dashboard/brand-tokens.css
      else
        find public/brand -type f ! -name 'hero-*.webp' ! -name "og-${site}.png"
        find public/fonts -maxdepth 1 -type f -name '*.woff2'
        find src/components/BrandNav src/components/Header src/components/Footer \
             src/components/Layout src/components/SiteHero -maxdepth 1 -type f \
             \( -name '*.tsx' -o -name '*.css' \)
        printf '%s\n' BRAND_SYSTEM.md src/styles/brand-tokens.css \
                      src/components/BrandMark.tsx src/components/SportIcon.tsx
      fi
    } | sort -u | xargs sha256sum > BRAND_MANIFEST.sha256 )
  echo "manifest regenerated -> $site/BRAND_MANIFEST.sha256"
}
for repo in $REPOS; do
  [ -d "$ROOT/$repo" ] && gen_manifest "$ROOT/$repo" "$repo"
done
[ -d "$ROOT/health" ] && gen_manifest "$ROOT/health" health
