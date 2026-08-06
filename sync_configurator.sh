#!/usr/bin/env bash
# Refresh the vendored Streamax Sales Configurator from its source repo.
#
# The configurator is a SEPARATE project (owner: Kevin Wang) that lives at
# ~/Desktop/Streamax/Product-sales-kit. We vendor only its runtime files here so
# it deploys with the Sales Toolkit at /configurator — Render builds from THIS
# repo and cannot see the other checkout.
#
# Because it is vendored, it will drift. Re-run this after Kevin ships changes:
#   ./sync_configurator.sh
#
# Only runtime files are copied. The 73 MB "North America Sales List-FILE"
# source folder, the 13 MB source .xlsx, server/, scripts/ and docs/ are
# deliberately excluded — they are not needed to run the configurator.
set -euo pipefail

SRC="${1:-$HOME/Desktop/Streamax/Product-sales-kit}"
DEST="$(cd "$(dirname "$0")" && pwd)/configurator"

if [ ! -d "$SRC" ]; then
  echo "ERROR: source not found: $SRC" >&2
  echo "Pass the path explicitly: ./sync_configurator.sh /path/to/Product-sales-kit" >&2
  exit 1
fi

mkdir -p "$DEST"
for item in index.html styles.css catalog-data.js js data vendor assets; do
  if [ -e "$SRC/$item" ]; then
    rm -rf "${DEST:?}/$item"
    cp -R "$SRC/$item" "$DEST/$item"
    echo "  synced $item"
  else
    echo "  skipped $item (missing in source)"
  fi
done

REV="$(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo unknown)"
DATE="$(date +%Y-%m-%d)"
cat > "$DEST/VENDORED.md" <<EOF
# Vendored — do not edit here

These files are a copy of the **Streamax Sales Configurator**, maintained
separately by Kevin Wang (kevinwang@streamax.com).

- Source repo: \`$SRC\`
- Synced from revision: \`$REV\`
- Last synced: $DATE

Edit the source project, then run \`./sync_configurator.sh\` from the Sales
Toolkit repo root. Any change made directly in this folder will be overwritten
on the next sync.

Note: the configurator's beta **Annotate / Send feedback** features call
\`/api/annotations\`, \`/api/feedback\` and \`/api/solutions\`, which are served by
the source project's own Node server (\`server/server.js\`). That server is not
deployed here, so those beta features are inactive in the Sales Toolkit — the
configurator itself works fully.
EOF

echo "synced from revision $REV ($DATE)"
du -sh "$DEST"
