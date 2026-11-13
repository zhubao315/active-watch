"""ACTIVE round-2 patches for the health dashboard (index.html shell only).

No chart, data or calculation code is touched here — that is app.js's job.
"""
import json
import re
from pathlib import Path

DASH = Path('/oc/active/health/dashboard')
p = DASH / 'index.html'
s = p.read_text()

# ------------------------------------------------------------------ head ----
old_start = s.index('<meta charset')
old_end = s.index('</title>') + len('</title>')
head_new = """<meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="theme-color" content="#07111f" />
    <meta
      name="description"
      content="zhubao315 的健康数据：睡眠、HRV、静息心率、压力、步数与训练负荷，全部对比个人 7 天均值与 28 天基线；COROS MCP 每天自动同步，缺失不等于零，相关不等于因果。"
    />
    <title>ACTIVE / 健康｜zhubao315 的健康数据</title>
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="ACTIVE" />
    <meta property="og:title" content="ACTIVE / 健康｜zhubao315 的健康数据" />
    <meta property="og:description" content="睡眠、HRV、静息心率、压力与训练负荷，全部对比个人 7 天均值与 28 天基线，不做跨人群评判。" />
    <meta property="og:url" content="https://zhubao315.github.io/health/" />
    <meta property="og:image" content="https://zhubao315.github.io/health/brand/og-health.png" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="ACTIVE / 健康｜zhubao315 的健康数据" />
    <meta name="twitter:description" content="睡眠、HRV、静息心率、压力与训练负荷，全部对比个人 7 天均值与 28 天基线，不做跨人群评判。" />
    <link rel="canonical" href="https://zhubao315.github.io/health/" />
    <link rel="manifest" href="./site.webmanifest" />
    <link rel="icon" type="image/svg+xml" href="./brand/favicon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="./brand/favicon-32.png" />
    <link rel="icon" type="image/png" sizes="64x64" href="./brand/favicon-64.png" />
    <link rel="apple-touch-icon" href="./brand/apple-touch-icon.png" />
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebSite",
      "name": "ACTIVE / HEALTH",
      "alternateName": "zhubao315 的健康数据",
      "url": "https://zhubao315.github.io/health/",
      "inLanguage": "zh-CN"
    }
    </script>"""
s = s[:old_start] + head_new + s[old_end:]

# --------------------------------------------------------------- brand ------
s = s.replace('ZB ACTIVE', 'ACTIVE')
assert 'ZB ACTIVE' not in s

# ---------------------------------------------------- four-site navigation --
# capture the existing per-site blocks (icon + labels) and the old order
blocks = {}
for key in ('health', 'running', 'cycling', 'hiking'):
    m = re.search(
        r'( *)<a data-site="%s" href="[^"]+"[^>]*>\n(.*?)</a>' % key, s, re.S)
    assert m, key
    blocks[key] = m.group(2)

GITHUB = ('<svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">'
          '<path d="M9 19c-4.5 1.5-4.5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61'
          'c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1'
          'S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77'
          'a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>'
          'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>\n'
          '          <span>GitHub</span>')

ORDER = ['running', 'cycling', 'hiking', 'health']


def nav_items(indent: str, mobile: bool) -> str:
    out = []
    for key in ORDER:
        current = ' aria-current="page"' if key == 'health' else ''
        inner = blocks[key]
        if mobile:
            # the mobile bar keeps only the icon and the Chinese word
            icon = re.search(r'<svg class="site-icon".*?</svg>', inner, re.S).group(0)
            zh = re.search(r'<span class="nav-zh">([^<]+)</span>', inner).group(1)
            inner = f'{icon}\n          <span>{zh}</span>'
        out.append(f'{indent}<a data-site="{key}" href="https://zhubao315.github.io/{key}/"{current}>\n'
                   f'{inner}\n{indent}</a>')
    out.append(f'{indent}<a data-site="github" href="https://github.com/zhubao315/health"\n'
               f'{indent}  target="_blank" rel="noreferrer" aria-label="本站源码 GitHub">\n'
               f'{indent}  {GITHUB}\n{indent}</a>')
    return '\n'.join(out)


# desktop nav: replace the children of <nav class="nav">
m = re.search(r'(<nav class="nav" aria-label="运动与健康站点导航">\n)(.*?)( *</nav>)', s, re.S)
assert m, 'desktop nav'
s = s[:m.start()] + m.group(1) + nav_items('          ', mobile=False) + '\n' + m.group(3) + s[m.end():]

# mobile bottom bar
m = re.search(r'(<nav class="mobile-nav" aria-label="四站导航">\n)(.*?)(\n    </nav>)', s, re.S)
assert m, 'mobile nav'
s = s[:m.start()] + m.group(1) + nav_items('        ', mobile=True) + m.group(3) + s[m.end():]

p.write_text(s)
print('health index.html patched')

# ---------------------------------------------------------------- manifest --
manifest = {
    'name': 'ACTIVE / 健康｜zhubao315 的健康数据',
    'short_name': 'ACTIVE',
    'description': '睡眠、HRV、静息心率、压力与训练负荷的个人趋势与健康驾驶舱。',
    'start_url': './',
    'scope': './',
    'display': 'standalone',
    'lang': 'zh-CN',
    'theme_color': '#38bdf8',
    'background_color': '#07111f',
    'icons': [
        {'src': './brand/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': './brand/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
    ],
}
(DASH / 'site.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('health manifest written')
