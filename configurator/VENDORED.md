# Vendored — do not edit here

These files are a copy of the **Streamax Sales Configurator**, maintained
separately by Kevin Wang (kevinwang@streamax.com).

- Source repo: `/Users/jiachenyi/Desktop/Streamax/Product-sales-kit`
- Synced from revision: `7e1d50b`
- Last synced: 2026-08-06

Edit the source project, then run `./sync_configurator.sh` from the Sales
Toolkit repo root. Any change made directly in this folder will be overwritten
on the next sync.

The bulky `North America Sales List-FILE/` folder is the product **image
library**, not source material — ~246 files are referenced by relative path from
`catalog-data.js` and `js/`. It must ship, or every product card renders broken.
Those images are downscaled to a 1200px long edge and re-encoded on every sync
(`scripts/optimize_configurator_images.py`) — the source exports are up to
8192px for a slot the CSS renders at 240px. Fix the export upstream and this
step becomes a no-op.

Note: the configurator's beta **Annotate / Send feedback** features call
`/api/annotations`, `/api/feedback` and `/api/solutions`, which are served by
the source project's own Node server (`server/server.js`). That server is not
deployed here, so those beta features are inactive in the Sales Toolkit — the
configurator itself works fully.
