#!/usr/bin/env python3
"""Slice ACTIVE brand assets from the supplied identity board PNG.

This does NOT draw or regenerate artwork: every output pixel comes from
ACTIVE_Brand_Identity_Board.png. It only crops regions and, where the source
sits on a flat white/navy card, converts that flat backdrop to alpha so the
mark can be placed on any surface.

Source: brand/assets/ACTIVE_Brand_Identity_Board.png
Run:    python3 brand/slice-board.py
"""

import base64
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
BOARD = ASSETS / "ACTIVE_Brand_Identity_Board.png"

im = Image.open(BOARD).convert("RGBA")


def crop(box):
    return im.crop(box)


def key_background(image, rgb, tolerance=28, feather=1):
    """Make pixels close to `rgb` transparent. Keeps anti-aliased edges."""
    px = image.load()
    target = tuple(rgb) + (255,)
    for y in range(image.height):
        for x in range(image.width):
            r, g, b, a = px[x, y]
            dist = max(abs(r - target[0]), abs(g - target[1]), abs(b - target[2]))
            if dist <= tolerance:
                px[x, y] = (r, g, b, 0)
            elif feather and dist <= tolerance + feather:
                px[x, y] = (r, g, b, int(a * 0.5))
    return image


def save(image, name):
    image.save(ASSETS / name)
    print(f"[slice] {name}  {image.size}")


# --------------------------------------------------------------------------
# 1. Master mark — from the white card (row 2, card 1). White -> transparent,
#    leaving the true gradient "A" pixels untouched.
# --------------------------------------------------------------------------
mark = crop((122, 232, 240, 312))
mark = key_background(mark, (255, 255, 255), tolerance=26)
# trim transparent margins
bbox = mark.getbbox()
if bbox:
    mark = mark.crop(bbox)
save(mark, "active-mark.png")

# Dark-tile mark (row 2, card 4) — used inside the favicon tile.
tile = crop((1200, 230, 1372, 394))
tile.thumbnail((512, 512), Image.LANCZOS)
save(tile.convert("RGB"), "active-mark-tile.png")

# --------------------------------------------------------------------------
# 2. Four sub-brand icons — from the light card (row 3). White -> transparent.
# --------------------------------------------------------------------------
icon_boxes = {
    "health": (48, 452, 133, 505),
    "running": (172, 452, 257, 505),
    "cycling": (296, 452, 381, 505),
    "hiking": (420, 452, 505, 505),
}
for key, box in icon_boxes.items():
    icon = key_background(crop(box), (255, 255, 255), tolerance=30)
    bbox = icon.getbbox()
    if bbox:
        icon = icon.crop(bbox)
    save(icon, f"icon-{key}.png")

# --------------------------------------------------------------------------
# 3. ACTIVE WATCH control-centre mark — from the navy card (row 3 right).
#    Navy backdrop -> transparent; connectors/nodes/A pixels preserved.
# --------------------------------------------------------------------------
watch = crop((1160, 462, 1295, 566))
watch = key_background(watch, (11, 29, 51), tolerance=34)
bbox = watch.getbbox()
if bbox:
    watch = watch.crop(bbox)
save(watch, "watch-mark.png")

# --------------------------------------------------------------------------
# 4. Wordmark + lockups — direct crops, kept on their original card surface.
# --------------------------------------------------------------------------
save(crop((505, 258, 752, 352)).convert("RGB"), "wordmark-dark.png")   # white on navy
save(crop((105, 328, 312, 372)).convert("RGB"), "wordmark-light.png")  # navy on white
save(crop((364, 230, 762, 394)).convert("RGB"), "lockup-dark.png")
save(crop((780, 230, 1175, 394)).convert("RGB"), "lockup-light.png")
save(crop((14, 230, 346, 394)).convert("RGB"), "lockup-stacked.png")

# --------------------------------------------------------------------------
# 5. Favicon — from the dark tile in the favicon strip (bottom area), resized
#    with high-quality downsampling. All four sites share identical bytes.
# --------------------------------------------------------------------------
favicon_source = crop((28, 814, 117, 903)).convert("RGB")
for size, name in [
    (32, "favicon-32.png"),
    (64, "favicon-64.png"),
    (180, "apple-touch-icon.png"),
    (192, "icon-192.png"),
    (512, "icon-512.png"),
]:
    favicon_source.resize((size, size), Image.LANCZOS).save(ASSETS / name)
    print(f"[slice] {name}  {size}x{size}")

# favicon.svg is an SVG wrapper around the sliced 512px tile — the pixels are
# still the board's real favicon, never a redrawn vector mark.
tile_b64 = base64.b64encode((ASSETS / "icon-512.png").read_bytes()).decode("ascii")
(ASSETS / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" '
    'viewBox="0 0 64 64"><image href="data:image/png;base64,' + tile_b64 + '" '
    'width="64" height="64"/></svg>\n'
)
print("[slice] favicon.svg  (sliced tile wrapper)")

print("[slice] done — all assets sliced from", BOARD.name)
