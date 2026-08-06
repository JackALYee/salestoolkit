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
# Only runtime files are copied. server/, scripts/, docs/ and the 13 MB source
# .xlsx are deliberately excluded — they are not needed to run the configurator.
#
# "North America Sales List-FILE" IS required despite its size (~72 MB): it is
# not a source folder, it is the product image library. catalog-data.js,
# js/02-dom-state.js and js/04-product-meta.js reference ~246 files inside it by
# relative path, so leaving it out renders every product card with a broken
# image. It was excluded on the first vendoring pass and that is exactly what
# went wrong. Verify after syncing with ./sync_configurator.sh --check.
set -euo pipefail

SRC="${1:-$HOME/Desktop/Streamax/Product-sales-kit}"
DEST="$(cd "$(dirname "$0")" && pwd)/configurator"

if [ ! -d "$SRC" ]; then
  echo "ERROR: source not found: $SRC" >&2
  echo "Pass the path explicitly: ./sync_configurator.sh /path/to/Product-sales-kit" >&2
  exit 1
fi

mkdir -p "$DEST"
for item in index.html styles.css catalog-data.js js data vendor assets \
             "North America Sales List-FILE"; do
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

The bulky \`North America Sales List-FILE/\` folder is the product **image
library**, not source material — ~246 files are referenced by relative path from
\`catalog-data.js\` and \`js/\`. It must ship, or every product card renders broken.

Note: the configurator's beta **Annotate / Send feedback** features call
\`/api/annotations\`, \`/api/feedback\` and \`/api/solutions\`, which are served by
the source project's own Node server (\`server/server.js\`). That server is not
deployed here, so those beta features are inactive in the Sales Toolkit — the
configurator itself works fully.
EOF

echo "synced from revision $REV ($DATE)"
du -sh "$DEST"

# Every image path the app references must exist, or product cards render
# broken. Cheap to check, and the failure is invisible until someone opens the
# page — so always check.
echo ""
echo "verifying referenced assets..."
python3 - "$DEST" <<'PYEOF'
import pathlib, re, sys
dest = pathlib.Path(sys.argv[1])
blob = ""
for f in ["catalog-data.js", "index.html"] + sorted(str(p.relative_to(dest)) for p in dest.glob("js/*.js")):
    fp = dest / f
    if fp.is_file():
        blob += fp.read_text(encoding="utf-8", errors="ignore")
refs = sorted(set(re.findall(r'"(North America Sales List-FILE/[^"]*)"', blob)))
files = [r for r in refs if pathlib.Path(r).suffix]
missing = [r for r in files if not (dest / r).is_file()]
print(f"  {len(files)} referenced asset paths, {len(missing)} missing")
for m in missing[:20]:
    print(f"    MISSING  {m}")
sys.exit(1 if missing else 0)
PYEOF
echo "  OK — every referenced asset is present"
