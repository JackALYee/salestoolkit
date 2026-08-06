#!/usr/bin/env python3
"""Shrink the vendored Sales Configurator product images.

Why
---
The configurator's product library (`configurator/North America Sales List-FILE/`)
ships photos at source-export resolution — up to 8192x5464 / 14.9 MB — while the
CSS never renders one larger than 240px (`.host-photo`), and there is no zoom or
lightbox anywhere in the app. That is ~34x more pixels than any screen shows, on
a page a rep may open on mobile data at a customer site.

This pass caps the long edge at MAX_EDGE and re-encodes the PNG. Nothing is
cropped, alpha is preserved, filenames and paths are untouched (the catalog
references them by exact relative path), and PNG re-encoding is lossless — so
running this twice is a no-op, not a second generation of quality loss.

It runs from `sync_configurator.sh` after the copy, NOT as a one-off edit of the
vendored tree: anything hand-edited under `configurator/` is overwritten by the
next sync, so the optimisation has to be part of the sync to survive.

The upstream fix is for Kevin Wang to export at a sane resolution in
`Product-sales-kit`; until then this keeps the deployed copy sensible.

Usage
-----
    python3 scripts/optimize_configurator_images.py            # optimise in place
    python3 scripts/optimize_configurator_images.py --check    # report only, exit 1 if work pending
    python3 scripts/optimize_configurator_images.py --max-edge 1600

Needs Pillow. If it isn't installed:
    python3 -m venv /tmp/imgvenv && /tmp/imgvenv/bin/pip install Pillow
    /tmp/imgvenv/bin/python scripts/optimize_configurator_images.py
"""
from __future__ import annotations

import argparse
import io
import pathlib
import sys

# The image library the catalog references. `assets/` is deliberately NOT
# touched: it is UI chrome (home-screen previews, diagram parts, brand marks)
# rendered at or near its native size, where downscaling would soften the UI for
# ~6 MB of no real benefit.
IMAGE_SUBDIR = "North America Sales List-FILE"

# Long-edge cap in pixels. The largest on-screen image in styles.css is
# `.host-photo { height: 240px }`, so 1200 leaves 5x linear headroom — 2.5x even
# on a 2x-DPR display, and enough for a future lightbox.
MAX_EDGE = 1200

# Selection is by MAGIC BYTES, not by extension. Five files in this library are
# named `*.gif` but are actually PNG data (`89 50 4E 47`) — browsers sniff the
# content so they render fine, and an extension whitelist silently skips ~8.8 MB
# of them. Real (possibly animated) GIFs, JPEGs and PDFs are left alone.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def is_png(path: pathlib.Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return fh.read(8) == PNG_MAGIC
    except OSError:
        return False


def optimise(path: pathlib.Path, max_edge: int, dry_run: bool) -> tuple[int, int]:
    """Return (bytes_before, bytes_after). after == before when nothing helped."""
    from PIL import Image

    before = path.stat().st_size
    with Image.open(path) as im:
        im.load()
        w, h = im.size
        # Palette images with transparency lose it through resize unless promoted.
        if im.mode == "P":
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        if max(w, h) > max_edge:
            scale = max_edge / max(w, h)
            im = im.resize((max(1, round(w * scale)), max(1, round(h * scale))),
                           Image.LANCZOS)
        buf = io.BytesIO()
        # Always re-encode as PNG — including the mislabelled `*.gif` files,
        # which are PNG data already. The filename is never changed, because the
        # catalog references every asset by exact relative path.
        im.save(buf, format="PNG", optimize=True)

    after = buf.tell()
    if after >= before:          # already optimal — leave the original bytes alone
        return before, before
    if not dry_run:
        path.write_bytes(buf.getvalue())
    return before, after


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=None,
                    help="configurator directory (default: ../configurator relative to this script)")
    ap.add_argument("--max-edge", type=int, default=MAX_EDGE)
    ap.add_argument("--check", action="store_true",
                    help="report what would change and exit 1 if anything would; write nothing")
    args = ap.parse_args()

    try:
        import PIL  # noqa: F401
    except ImportError:
        print("ERROR: Pillow is required.\n"
              "  python3 -m venv /tmp/imgvenv && /tmp/imgvenv/bin/pip install Pillow\n"
              "  /tmp/imgvenv/bin/python scripts/optimize_configurator_images.py",
              file=sys.stderr)
        return 2

    root = pathlib.Path(args.root) if args.root else pathlib.Path(__file__).resolve().parent.parent / "configurator"
    target = root / IMAGE_SUBDIR
    if not target.is_dir():
        print(f"ERROR: not found: {target}", file=sys.stderr)
        return 2

    files = sorted(p for p in target.rglob("*") if p.is_file() and is_png(p))
    if not files:
        print(f"  no images under {IMAGE_SUBDIR}/ — nothing to do")
        return 0

    total_before = total_after = 0
    changed = []
    for p in files:
        before, after = optimise(p, args.max_edge, dry_run=args.check)
        total_before += before
        total_after += after
        if after < before:
            changed.append((before - after, p))

    saved = total_before - total_after
    verb = "would shrink" if args.check else "shrank"
    print(f"  {verb} {len(changed)}/{len(files)} images  "
          f"{total_before / 1048576:.1f} MB -> {total_after / 1048576:.1f} MB  "
          f"(saved {saved / 1048576:.1f} MB, {100 * saved / total_before:.0f}%)")
    for delta, p in sorted(changed, reverse=True)[:5]:
        print(f"    -{delta / 1048576:5.2f} MB  {p.relative_to(root)}")

    if args.check and changed:
        print("  run without --check to apply", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
