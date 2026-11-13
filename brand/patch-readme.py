"""Brand block for the four READMEs.

The stats block (STATS:START/END) is rewritten by the daily bot — it is
never touched here.
"""

from pathlib import Path

SITES = [
    ('health', '健康', 'HEALTH', '❤️'),
    ('running', '跑步', 'RUNNING', '🏃'),
    ('cycling', '骑行', 'CYCLING', '🚴'),
    ('hiking', '徒步', 'HIKING', '🥾'),
]

BRAND_BLOCK = """
<div align="center">

**ZB ACTIVE** — 朱宝 · 运动与健康数字档案
**用数据记录每一次前进。**

{nav}

</div>
"""

BRAND_SECTION = """## 品牌 ZB ACTIVE

四个站点属于同一套品牌视觉系统：同一个 ZB ACTIVE 标志、四套子品牌图标、同一套配色令牌、同一套字体与布局骨架、同一套响应式规则与主题偏好键。运动站各自保留专业表达（跑步的速度与节奏、骑行的机械与流线、徒步的地形与海拔），健康站保持独立的数据驾驶舱实现，不迁框架。

- 品牌规范：[BRAND_SYSTEM.md](BRAND_SYSTEM.md)
- 设计令牌：[src/styles/brand-tokens.css](src/styles/brand-tokens.css)
- 标志与图标：[public/brand/](public/brand/)
- 社交预览图：[public/brand/og-*.png](public/brand/)

"""

for repo in ['running', 'cycling', 'hiking', 'health']:
    path = Path('/oc/active') / repo / 'README.md'
    s = path.read_text()

    nav = ' · '.join(
        f'[{emoji} {zh} {en}](https://zhubao315.github.io/{key}/)'
        for key, zh, en, emoji in SITES
    )
    block = BRAND_BLOCK.replace('{nav}', nav)

    if 'ZB ACTIVE' not in s:
        # after the tagline line of the centred header
        marker = '\n</div>\n'
        index = s.find(marker)
        if index == -1:
            raise SystemExit(f'{repo}: header end not found')
        s = s[: index + len(marker)] + block + s[index + len(marker):]

    # the old anchor pointed at a heading that does not exist
    s = s.replace('[🔗 三个站点](#三个站点)', '[🔗 相关站点](#相关站点)')

    # the highlight list described three sport sites; there are four now
    s = s.replace(
        '- 三个运动站点互相跳转',
        '- 四个站点互相跳转（健康 / 跑步 / 骑行 / 徒步），共用同一套品牌与主题偏好',
    )

    # a hand-written number that drifted away from the auto-generated one
    s = s.replace(
        '- 2,600+ 次骑行，日历热力图按年切换',
        '- 全部骑行记录都在库里（当前次数见上方数据概览），日历热力图按年切换',
    )

    if '## 品牌 ZB ACTIVE' not in s:
        if '## 相关站点' in s:
            s = s.replace('## 相关站点', BRAND_SECTION + '## 相关站点', 1)
        elif '## 运动站点' in s:
            s = s.replace('## 运动站点', BRAND_SECTION + '## 运动站点', 1)

    path.write_text(s)
    print(repo, 'README updated')
