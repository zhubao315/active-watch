#!/usr/bin/env python3
"""Build the ZB ACTIVE Navigation Icon 1.0 asset set from the base SVG glyphs.

For each icon: base .svg, -mono.svg (currentColor), -active.svg (single bright
brand colour, no dimmed alphas), plus 24px / 48px PNG previews rendered by the
companion JS script. This is deterministic; glyphs are hand-authored vectors,
never traced from a bitmap.
"""
import re, pathlib

HERE = pathlib.Path(__file__).resolve().parent
COLORS = {
    'health': ('#38BDF8', '#0EA5E9'),
    'running': ('#D9F36A', '#A3B82F'),
    'cycling': ('#FBBF24', '#F59E0B'),
    'hiking': ('#34D399', '#10B981'),
}

for key, (primary, secondary) in COLORS.items():
    src = (HERE / f'{key}.svg').read_text()

    # mono: every brand colour -> currentColor
    mono = src
    for c in (primary, secondary):
        mono = mono.replace(c, 'currentColor')
    (HERE / f'{key}-mono.svg').write_text(mono)

    # active: secondary -> primary, remove dimmed opacity so the glyph is
    # uniformly bright when this site is the current one.
    active = src.replace(secondary, primary)
    active = re.sub(r' opacity="0\.[0-9]+"', '', active)
    (HERE / f'{key}-active.svg').write_text(active)

    print(f'{key}: base + mono + active')
print('done')
