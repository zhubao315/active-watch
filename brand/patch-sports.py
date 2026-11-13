"""ACTIVE round-2 patches for the three sport repositories.

Mechanical, reviewable edits only: theme tokens, fonts, head metadata,
navigation order, manifest. Data and logic are never touched.
"""
import json
import re
from pathlib import Path

REPOS = Path('/oc/active')

SITES = {
    'running': {
        'key': 'running', 'zh': '跑步', 'label': 'RUNNING',
        'title': 'zhubao315 的跑步生涯',
        'html_title': 'ACTIVE / 跑步｜zhubao315 的跑步生涯',
        'desc': '2,000+ 次跑步、累计里程、个人最佳、年度热力图、GPS 轨迹与 3D 地形，全部来自 COROS 原始记录。',
        'accent': '#D9F36A',
        'repo': 'https://github.com/zhubao315/running',
    },
    'cycling': {
        'key': 'cycling', 'zh': '骑行', 'label': 'CYCLING',
        'title': 'zhubao315 的骑行生涯',
        'html_title': 'ACTIVE / 骑行｜zhubao315 的骑行生涯',
        'desc': '数千次骑行、累计里程与爬升、均速与海拔剖面、骑行足迹与 3D 地形，全部来自 COROS 原始记录。',
        'accent': '#FBBF24',
        'repo': 'https://github.com/zhubao315/cycling',
    },
    'hiking': {
        'key': 'hiking', 'zh': '徒步', 'label': 'HIKING',
        'title': 'zhubao315 的徒步与山野',
        'html_title': 'ACTIVE / 徒步｜zhubao315 的徒步与山野',
        'desc': '徒步里程、累计爬升、最高海拔、季节与省份筛选、山野轨迹与 3D 地形，全部来自 COROS 原始记录。',
        'accent': '#34D399',
        'repo': 'https://github.com/zhubao315/hiking',
    },
}

NAV_ORDER = ['running', 'cycling', 'hiking', 'health']

FACES = """/* Text faces come from the main site (zhubao315.github.io): Inter for
   reading, Manrope for display, both self-hosted variable files. Fira Code
   stays the numeral/table face — CJK falls back to the system stack. */
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/inter-latin-wght-normal.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
    U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
    U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/inter-latin-ext-wght-normal.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF,
    U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}
@font-face {
  font-family: 'Manrope Variable';
  src: url('/fonts/manrope-latin-wght-normal.woff2') format('woff2-variations');
  font-weight: 200 800;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6,
    U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+2074, U+20AC,
    U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
@font-face {
  font-family: 'Manrope Variable';
  src: url('/fonts/manrope-latin-ext-wght-normal.woff2') format('woff2-variations');
  font-weight: 200 800;
  font-style: normal;
  font-display: swap;
  unicode-range: U+0100-02AF, U+0304, U+0308, U+0329, U+1E00-1E9F, U+1EF2-1EFF,
    U+2020, U+20A0-20AB, U+20AD-20C0, U+2113, U+2C60-2C7F, U+A720-A7FF;
}
"""

DARK_MAP = [
    ("  --bg: #0b1d33;", "  --bg: #07111f;"),
    ("  --bg-soft: #0a1729;", "  --bg-soft: #0a1424;"),
    ("  --card-hover: #14344f;", "  --card-hover: #16324e;"),
    ("  --text: #f8fafc;", "  --text: #f7faff;"),
    ("  --border: #1e3a56;", "  --border: rgba(247, 250, 255, 0.16);"),
    ("  --border-strong: #2a4e70;", "  --border-strong: rgba(247, 250, 255, 0.32);"),
    ("  --font-sans: 'Fira Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,\n    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;",
     "  --font-sans: 'Inter Variable', 'Manrope Variable', 'Noto Sans CJK SC',\n    'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;\n  --font-display: 'Manrope Variable', 'Inter Variable', 'Noto Sans CJK SC',\n    'PingFang SC', sans-serif;"),
]

LIGHT_MAP = [
    ("  --bg: #eef3f9;", "  --bg: #f7faff;"),
    ("  --bg-soft: #e4ecf5;", "  --bg-soft: #eef2f7;"),
    ("  --card-hover: #f2f7fc;", "  --card-hover: #eef2f7;"),
    ("  --text: #0e1b29;", "  --text: #101828;"),
    ("  --border: #d3dfec;", "  --border: rgba(16, 24, 40, 0.14);"),
    ("  --border-strong: #b0c2d5;", "  --border-strong: rgba(16, 24, 40, 0.3);"),
]


def patch_theme(repo: Path) -> None:
    p = repo / 'src/styles/theme.css'
    s = p.read_text()
    # swap the Fira Sans faces for the main site's variable faces
    s = s.replace(
        """/* Self-hosted type: Fira Sans (UI/latin) + Fira Code (numerals/tables).
   CJK falls back to the system stack — Fira has no CJK coverage. */
@font-face {
  font-family: 'Fira Sans';
  src: url('/fonts/fira-sans-400.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('/fonts/fira-sans-500.woff2') format('woff2');
  font-weight: 500;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('/fonts/fira-sans-600.woff2') format('woff2');
  font-weight: 600;
  font-display: swap;
}
@font-face {
  font-family: 'Fira Sans';
  src: url('/fonts/fira-sans-700.woff2') format('woff2');
  font-weight: 700;
  font-display: swap;
}""",
        FACES.strip(),
    )
    for old, new in DARK_MAP + LIGHT_MAP:
        assert old in s, (repo.name, old[:40])
        s = s.replace(old, new, 1)
    # theme.css may still mention ZB ACTIVE in comments
    s = s.replace('ZB ACTIVE', 'ACTIVE')
    p.write_text(s)


def patch_metadata(repo: Path) -> None:
    p = repo / 'src/static/site-metadata.ts'
    s = p.read_text()
    # reorder the four-site nav: run → ride → hike → health, extras last
    entries = dict(re.findall(
        r"\{\s*\n\s*name: '(health|running|cycling|hiking)',\s*\n\s*url: '([^']+)',\s*\n\s*\}", s))
    assert len(entries) == 4, repo.name
    for key, url in entries.items():
        s = s.replace(f"{{\n      name: '{key}',\n      url: '{url}',\n    }},", f"__NAV_{key}__", 1)
    keys_in_order = [k for k in re.findall(r'__NAV_(\w+)__', s)]
    assert set(keys_in_order) == set(NAV_ORDER), (repo.name, keys_in_order)
    block = ',\n    '.join(f"{{\n      name: '{k}',\n      url: '{entries[k]}',\n    }}" for k in NAV_ORDER)
    # the placeholders were written at identical indentation; splice as a unit
    first = s.index('__NAV_')
    last_at = s.rindex('__NAV_')
    last_end = s.index('__', last_at + len('__NAV_')) + 2
    start = s.rfind('\n', 0, first) + 1
    end = s.find('\n', last_end) + 1
    s = s[:start] + block + ',' + s[end:]
    assert '__NAV' not in s, repo.name
    p.write_text(s)


def patch_profile(repo: Path) -> None:
    for dash in ('RunningDashboard', 'CyclingDashboard', 'HikingDashboard'):
        p = repo / 'src/components' / dash / 'Profile.tsx'
        if not p.exists():
            continue
        s = p.read_text()
        s = s.replace('ZB ACTIVE /', 'ACTIVE /')
        p.write_text(s)


def patch_head(repo: Path, meta: dict) -> None:
    p = repo / 'index.html'
    s = p.read_text()
    key = meta['key']
    url = f"https://zhubao315.github.io/{key}/"
    head_new = f"""    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/brand/favicon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="/brand/favicon-32.png" />
    <link rel="icon" type="image/png" sizes="64x64" href="/brand/favicon-64.png" />
    <link rel="apple-touch-icon" href="/brand/apple-touch-icon.png" />
    <link rel="manifest" href="/site.webmanifest" />
    <link rel="canonical" href="{url}" />

    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="ACTIVE" />
    <meta property="og:title" content="{meta['html_title']}" />
    <meta property="og:description" content="{meta['desc']}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{url}brand/og-{key}.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{meta['html_title']}" />
    <meta name="twitter:description" content="{meta['desc']}" />
    <meta name="theme-color" content="#07111f" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{meta['html_title']}</title>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "ACTIVE / {meta['label']}",
      "alternateName": "{meta['title']}",
      "url": "{url}",
      "inLanguage": "zh-CN"
    }}
    </script>"""
    # replace from <meta charset> up to and including the old <title> line
    start = s.find('<meta charset')
    end = s.find('</title>') + len('</title>')
    assert start != -1 and end > start
    s = s[:start] + head_new + s[end:]
    p.write_text(s)


def write_manifest(repo: Path, meta: dict) -> None:
    manifest = {
        'name': f"ACTIVE / {meta['label']}｜{meta['title']}",
        'short_name': 'ACTIVE',
        'description': meta['desc'],
        'start_url': f"/{meta['key']}/",
        'scope': f"/{meta['key']}/",
        'display': 'standalone',
        'lang': 'zh-CN',
        'theme_color': meta['accent'],
        'background_color': '#07111f',
        'icons': [
            {'src': '/brand/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
            {'src': '/brand/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        ],
    }
    (repo / 'public/site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')


def patch_layout(repo: Path) -> None:
    p = repo / 'src/components/Layout/index.tsx'
    s = p.read_text()
    # the brand's canvas is the theme colour of the browser chrome
    s = s.replace("accent || '#0b1d33'", "accent || '#07111f'")
    p.write_text(s)


def patch_smoke(repo: Path) -> None:
    p = repo / 'scripts/smoke-theme.mjs'
    s = p.read_text()
    s = s.replace('ZB ACTIVE', 'ACTIVE')
    p.write_text(s)


for name, meta in SITES.items():
    repo = REPOS / name
    patch_theme(repo)
    patch_metadata(repo)
    patch_profile(repo)
    patch_head(repo, meta)
    patch_layout(repo)
    patch_smoke(repo)
    write_manifest(repo, meta)
    print(name, 'patched')
