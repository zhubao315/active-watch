"""Apply the ZB ACTIVE brand shell to the health dashboard.

The health site keeps its own stack (native HTML/CSS/JS + Chart.js); only the
brand layer is added: the mark, the sub-brand icons, the mobile bottom bar,
the generated backdrop and the social card. No data, no calculation and no
chart logic is touched.
"""

from pathlib import Path

DASH = Path('/oc/active/health/dashboard')

MARK = """<svg class="brand-mark" viewBox="0 0 32 32" fill="none" role="img" aria-label="ZB ACTIVE">
            <path d="M7 9h18L7 23h18" stroke="currentColor" stroke-width="2.8"
              stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="16" cy="16" r="2.4" fill="#FBBF24" />
          </svg>"""

ICONS = {
    'health': """<svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M2.5 12.5h4.2l2.1-6.4 3.5 12.2 2.6-7 1.9 3.2h4.7"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>""",
    'running': """<svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M2.5 18.8c3.7 0 4-9.3 8.8-9.3 3.1 0 4.2 4 7.2 4"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M15.6 10.9 18.7 13.5l-3.1 2.6"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>""",
    'cycling': """<svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <circle cx="5.6" cy="16.4" r="3.6" stroke="currentColor" stroke-width="2" />
              <circle cx="18.4" cy="16.4" r="3.6" stroke="currentColor" stroke-width="2" />
              <path d="M5.6 16.4 10.4 8.2h3.8l1.9 3.4M10.4 8.2l2.6 8.2h5.4M14.2 8.2h2.6"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>""",
    'hiking': """<svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M2.2 18.6 8.4 8.2l4.1 7 2.4-3.9 4.7 7.3"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M2.2 18.6h17.6" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.55" />
              <path d="M6.1 13.2c1.9-1.3 3.9-1.3 5.8 0" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" opacity="0.55" />
            </svg>""",
}

SITES = [
    ('health', '健康', 'HEALTH', 'https://zhubao315.github.io/health/', True),
    ('running', '跑步', 'RUNNING', 'https://zhubao315.github.io/running/', False),
    ('cycling', '骑行', 'CYCLING', 'https://zhubao315.github.io/cycling/', False),
    ('hiking', '徒步', 'HIKING', 'https://zhubao315.github.io/hiking/', False),
]

html_path = DASH / 'index.html'
s = html_path.read_text()

# ---------------------------------------------------------------- head ----
s = s.replace(
    '<meta name="theme-color" content="#22d3ee" />',
    '<meta name="theme-color" content="#0b1d33" />',
)
s = s.replace(
    '<title>zhubao315 的健康数据</title>',
    '<title>zhubao315 的健康驾驶舱 · ZB ACTIVE</title>\n'
    '    <meta property="og:type" content="website" />\n'
    '    <meta property="og:site_name" content="ZB ACTIVE" />\n'
    '    <meta property="og:title" content="zhubao315 的健康驾驶舱 · ZB ACTIVE" />\n'
    '    <meta property="og:description" content="睡眠、HRV、静息心率、压力与训练负荷，全部对比个人 7 天均值与 28 天基线，不做跨人群评判。" />\n'
    '    <meta property="og:url" content="https://zhubao315.github.io/health/" />\n'
    '    <meta property="og:image" content="https://zhubao315.github.io/health/brand/og-health.png" />\n'
    '    <meta name="twitter:card" content="summary_large_image" />',
)
s = s.replace(
    '<link rel="icon" type="image/png" href="./favicon.png" />',
    '<link rel="icon" type="image/svg+xml" href="./brand/favicon.svg" />\n'
    '    <link rel="icon" type="image/png" href="./favicon.png" />',
)
s = s.replace(
    '<link rel="stylesheet" href="./style.css?v=__BUILD_HASH__" />',
    '<link rel="stylesheet" href="./style.css?v=__BUILD_HASH__" />\n'
    '    <link rel="stylesheet" href="./brand-tokens.css?v=__BUILD_HASH__" />',
)

# ------------------------------------------------------------- header ----
old_brand = """        <a class="brand" href="./">
          <img class="brand-logo" src="https://avatars.githubusercontent.com/u/1206487?v=4"
            alt="" width="34" height="34" />
          <span>zhubao315 的健康数据</span>
        </a>"""
new_brand = f"""        <a class="brand" href="./">
          {MARK}
          <span class="brand-wordmark">ZB ACTIVE</span>
          <span class="brand-rule" aria-hidden="true"></span>
          <span class="brand-site">
            <span class="brand-site-zh">健康</span>
            <span class="brand-site-en">HEALTH</span>
          </span>
        </a>"""
assert old_brand in s
s = s.replace(old_brand, new_brand)

# nav items get their sub-brand icon
for key, zh, en, url, current in SITES:
    attr = ' aria-current="page"' if current else ''
    old = f"""          <a data-site="{key}" href="{url}"{attr}>
            <span class="nav-zh">{zh}</span><span class="nav-en">{en}</span>
          </a>"""
    new = f"""          <a data-site="{key}" href="{url}"{attr}>
            {ICONS[key]}
            <span class="nav-text"><span class="nav-zh">{zh}</span><span class="nav-en">{en}</span></span>
          </a>"""
    assert old in s, key
    s = s.replace(old, new)

# --------------------------------------------------------------- hero ----
old_hero = """      <section class="hero hero-compact">
        <div class="hero-main">
          <h1>健康驾驶舱</h1>"""
new_hero = """      <section class="hero hero-compact">
        <div class="hero-main">
          <p class="hero-brand">
            <svg class="site-icon" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              <path d="M2.5 12.5h4.2l2.1-6.4 3.5 12.2 2.6-7 1.9 3.2h4.7"
                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>ZB ACTIVE</span>
            <span class="hero-brand-slash" aria-hidden="true">/</span>
            <span>HEALTH</span>
          </p>
          <h1>健康驾驶舱</h1>"""
assert old_hero in s
s = s.replace(old_hero, new_hero)

# ----------------------------------------------------- mobile bottom bar ----
mobile_items = []
for key, zh, en, url, current in SITES:
    attr = ' aria-current="page"' if current else ''
    mobile_items.append(
        f"""        <a data-site="{key}" href="{url}"{attr}>
          {ICONS[key]}
          <span>{zh}</span>
        </a>"""
    )
mobile_nav = """
    <nav class="mobile-nav" aria-label="四站导航">
""" + '\n'.join(mobile_items) + """
    </nav>
"""
s = s.replace('    <button type="button" id="back-to-top"', mobile_nav + '    <button type="button" id="back-to-top"')

# ------------------------------------------------------------- footer ----
old_footer = """      <div class="footer-inner">
        <span>数据来自 COROS · 每天 08:00（北京时间）自动同步 · 坐标：睡眠/HRV 按醒来日，其余按自然日</span>"""
new_footer = """      <div class="footer-inner">
        <span class="footer-brand">
          <svg class="brand-mark" viewBox="0 0 32 32" fill="none" role="img" aria-label="ZB ACTIVE">
            <path d="M7 9h18L7 23h18" stroke="currentColor" stroke-width="2.8"
              stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="16" cy="16" r="2.4" fill="#FBBF24" />
          </svg>
          <span class="brand-wordmark">ZB ACTIVE</span>
          <span class="footer-brand-line">朱宝 · 运动与健康数字档案</span>
        </span>
        <span>数据来自 COROS · 每天 08:00（北京时间）自动同步 · 坐标：睡眠/HRV 按醒来日，其余按自然日</span>"""
assert old_footer in s
s = s.replace(old_footer, new_footer)

html_path.write_text(s)
print('health index.html patched')
