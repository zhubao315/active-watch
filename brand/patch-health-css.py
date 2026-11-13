"""ACTIVE round-2 patches for health/dashboard/style.css.

Shell tokens only (surfaces, type, shell geometry). The dashboard's scientific
metric colours (--chart-*) are untouched by design.
"""
import re
from pathlib import Path

p = Path('/oc/active/health/dashboard/style.css')
s = p.read_text()

# ------------------------------------------------------------- fonts --------
old_faces = """@font-face {
  font-family: 'Fira Sans';
  src: url('./fonts/fira-sans-400.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('./fonts/fira-sans-500.woff2') format('woff2');
  font-weight: 500;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('./fonts/fira-sans-600.woff2') format('woff2');
  font-weight: 600;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('./fonts/fira-sans-700.woff2') format('woff2');
  font-weight: 700;
  font-display: swap;
}"""
new_faces = """/* Text faces come from the main site (zhubao315.github.io): Inter for
   reading, Manrope for display, self-hosted variable files. Fira Code stays
   the numeral/table face — CJK falls back to the system stack. */
@font-face {
  font-family: 'Inter Variable';
  src: url('./fonts/inter-latin-wght-normal.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
    U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
    U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Inter Variable';
  src: url('./fonts/inter-latin-ext-wght-normal.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF,
    U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}
@font-face {
  font-family: 'Manrope Variable';
  src: url('./fonts/manrope-latin-wght-normal.woff2') format('woff2-variations');
  font-weight: 200 800;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
    U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
    U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Manrope Variable';
  src: url('./fonts/manrope-latin-ext-wght-normal.woff2') format('woff2-variations');
  font-weight: 200 800;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF,
    U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}"""
assert old_faces in s
s = s.replace(old_faces, new_faces, 1)

# ------------------------------------------------------------- dark faces ---
DARK = [
    ("  --bg: #0b1d33;", "  --bg: #07111f;"),
    ("  --bg-soft: #0a1729;", "  --bg-soft: #0a1424;"),
    ("  --surface-1: #0e2339;", "  --surface-1: #13263d;"),
    ("  --text: #f8fafc;", "  --text: #f7faff;"),
    ("  --text-strong: #f8fafc;", "  --text-strong: #f7faff;"),
    ("  --border: rgba(148, 163, 184, 0.16);", "  --border: rgba(247, 250, 255, 0.16);"),
    ("  --border-strong: rgba(148, 163, 184, 0.28);", "  --border-strong: rgba(247, 250, 255, 0.32);"),
    ("  --card-border: rgba(148, 163, 184, 0.16);", "  --card-border: rgba(247, 250, 255, 0.16);"),
    ("  --card-border-strong: rgba(148, 163, 184, 0.28);", "  --card-border-strong: rgba(247, 250, 255, 0.32);"),
    ("  --grid: rgba(148, 163, 184, 0.1);", "  --grid: rgba(247, 250, 255, 0.1);"),
    ("  --bar-bg: rgba(11, 29, 51, 0.86);", "  --bar-bg: rgba(7, 17, 31, 0.88);"),
    ("  --bar-bg-strong: rgba(11, 29, 51, 0.97);", "  --bar-bg-strong: rgba(7, 17, 31, 0.97);"),
    ("  --bar-bg-soft: rgba(11, 29, 51, 0.78);", "  --bar-bg-soft: rgba(7, 17, 31, 0.8);"),
    ("  --header-h: 63px; /* header min-height 62 + 1px border */",
     "  --header-h: 64px; /* unified four-site header: 63px content + 1px border */"),
    ("  --font-sans: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,\n    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;",
     "  --font-sans: 'Inter Variable', 'Manrope Variable', 'Noto Sans CJK SC',\n    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;\n  --font-display: 'Manrope Variable', 'Inter Variable', 'Noto Sans CJK SC',\n    'PingFang SC', sans-serif;"),
]
for old, new in DARK:
    assert old in s, old[:44]
    s = s.replace(old, new, 1)

# ------------------------------------------------------------- light faces --
LIGHT = [
    ("  --bg: #eef3f9;", "  --bg: #f7faff;"),
    ("  --bg-soft: #e4ecf5;", "  --bg-soft: #eef2f7;"),
    ("  --text: #0e1b29;", "  --text: #101828;"),
    ("  --text-strong: #0e1b29;", "  --text-strong: #101828;"),
    ("  --card-border: rgba(15, 35, 60, 0.12);", "  --card-border: rgba(16, 24, 40, 0.14);"),
    ("  --card-border-strong: rgba(15, 35, 60, 0.22);", "  --card-border-strong: rgba(16, 24, 40, 0.3);"),
    ("  --border: rgba(15, 35, 60, 0.13);", "  --border: rgba(16, 24, 40, 0.14);"),
    ("  --border-strong: rgba(15, 35, 60, 0.24);", "  --border-strong: rgba(16, 24, 40, 0.3);"),
]
for old, new in LIGHT:
    assert old in s, old[:44]
    s = s.replace(old, new, 1)

# ------------------------------------------------------------- shell --------
old_shell = """  width: min(1180px, 100% - 2rem);
  margin: 0 auto;"""
new_shell = """  width: min(var(--active-shell, 1440px), 100% - 2 * var(--active-gutter, 1rem));
  margin: 0 auto;"""
assert old_shell in s
s = s.replace(old_shell, new_shell, 1)

p.write_text(s)
print('health style.css patched')
