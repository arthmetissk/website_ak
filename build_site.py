#!/usr/bin/env python3
"""Build the Alvin Kallicharran website.

    python3 build_site.py            # build  -> dist/index.html + dist/photos/
    python3 build_site.py serve      # build, then preview at http://localhost:8000
    python3 build_site.py optimize PATH   # resize new photos into src/photos (needs Pillow)

The page itself lives in src/page.html (title, styles, markup and the small
scripts for the photo viewer and the copy-email button). This script wraps it in
a full HTML document, copies only the photos the page uses, and writes the
result to dist/, which is what you host. Only the Python standard library is
needed for build and serve.
"""
import argparse
import functools
import http.server
import re
import shutil
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DIST = ROOT / "dist"

# Everything in page.html before this marker goes in <head>; the rest goes in <body>.
SPLIT_MARKER = '<header class="top">'

DESCRIPTION = (
    "Alvin Kallicharran BEM: West Indies and Warwickshire batsman, two-time World Cup winner, "
    "author of Colour Blind and youth coach in North Carolina."
)
FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
    "%3Crect width='64' height='64' rx='8' fill='%236E1627'/%3E"
    "%3Ctext x='32' y='45' font-family='Arial,sans-serif' font-size='40' font-weight='700' "
    "text-anchor='middle' fill='%23F6F2EC'%3EK%3C/text%3E%3C/svg%3E"
)

SKELETON = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{description}">
<link rel="icon" href="{favicon}">
<style>
:root {{ color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }}
body {{ margin: 0; }}
img {{ max-width: 100%; }}
[hidden] {{ display: none !important; }}
</style>
{head}
</head>
<body>
{body}
</body>
</html>
"""


def build() -> None:
    page_path = SRC / "page.html"
    if not page_path.exists():
        sys.exit(f"Missing {page_path}")
    page = page_path.read_text(encoding="utf-8")
    if SPLIT_MARKER not in page:
        sys.exit(f"Could not find {SPLIT_MARKER!r} in src/page.html")
    i = page.index(SPLIT_MARKER)
    head, body = page[:i].strip(), page[i:].strip()

    used = sorted(set(re.findall(r'(?:src|data-full)="(photos/[^"]+)"', page)))
    missing = [p for p in used if not (SRC / p).exists()]
    if missing:
        sys.exit("These photos are used in page.html but missing from src/:\n  " + "\n  ".join(missing))

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "photos").mkdir(parents=True)
    for p in used:
        shutil.copy2(SRC / p, DIST / p)

    html = SKELETON.format(description=DESCRIPTION, favicon=FAVICON, head=head, body=body)
    (DIST / "index.html").write_text(html, encoding="utf-8")
    (DIST / ".nojekyll").write_text("", encoding="utf-8")  # tell GitHub Pages not to run Jekyll

    on_disk = {f"photos/{p.name}" for p in (SRC / "photos").glob("*") if p.is_file()}
    unused = sorted(on_disk - set(used))
    size_mb = sum(f.stat().st_size for f in DIST.rglob("*") if f.is_file()) / 1_000_000
    print(f"Built {DIST / 'index.html'}  ({len(used)} photos, {size_mb:.1f} MB total)")
    if unused:
        print("Not used by the page, so not copied:", ", ".join(unused))


def serve(port: int) -> None:
    build()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Preview at http://localhost:{port}  (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def optimize(folder: str, full_edge: int = 1500, thumb_width: int = 640) -> None:
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Install Pillow first:  pip install Pillow")
    src = Path(folder)
    out = SRC / "photos"
    out.mkdir(parents=True, exist_ok=True)
    exts = {".jpg", ".jpeg", ".png", ".webp"}
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in exts)
    if not files:
        sys.exit(f"No images found in {src}")
    for p in files:
        im = Image.open(p).convert("RGB")
        w, h = im.size
        s = min(1.0, full_edge / max(w, h))
        full = im.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else im
        s = min(1.0, thumb_width / w)
        thumb = im.resize((round(w * s), round(h * s)), Image.LANCZOS) if s < 1 else im
        stem = re.sub(r"[^a-z0-9]+", "-", p.stem.lower()).strip("-")
        full.save(out / f"{stem}-full.webp", "WEBP", quality=80, method=6)
        thumb.save(out / f"{stem}-thumb.webp", "WEBP", quality=78, method=6)
        print(f"{p.name}: thumb {thumb.size[0]}x{thumb.size[1]}  full {full.size[0]}x{full.size[1]}")
    print("\nNow add a gallery button to src/page.html (see README, 'Adding photos').")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("build", help="build dist/ (default)")
    sp = sub.add_parser("serve", help="build and preview locally")
    sp.add_argument("--port", type=int, default=8000)
    op = sub.add_parser("optimize", help="turn original photos into web-ready thumbnails and full-size images")
    op.add_argument("folder")
    args = ap.parse_args()
    if args.cmd == "serve":
        serve(args.port)
    elif args.cmd == "optimize":
        optimize(args.folder)
    else:
        build()


if __name__ == "__main__":
    main()
