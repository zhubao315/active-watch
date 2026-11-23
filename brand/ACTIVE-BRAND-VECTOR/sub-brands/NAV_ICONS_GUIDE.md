# ZB ACTIVE Navigation Icon 1.1 — Figurative Sport Glyph

四枚统一设计语言的**具象运动导航图标**，手工 SVG 路径（非位图描摹、非 Lucide/Emoji/火柴人），设计系统为同一品牌资产。1.1 版将图形概念从抽象几何改为一眼可辨的具象轮廓，保留 24×24 网格与四站品牌色。

## 统一参数

| 项 | 值 |
|---|---|
| 网格 | 24×24，1:1 |
| 描边 | 2–2.6px，圆角端点/折角 |
| 背景 | 完全透明 |
| 主体占比 | 约 70–78% |
| 识别尺寸 | 16 / 20 / 24 / 28px |
| 风格 | 具象轮廓 + 圆润线条 + 清晰负空间 |

## 四枚图标

| 图标 | 概念 | 主色 | 辅助色 |
|---|---|---|---|
| health | 心形 + 生命脉搏波 | `#38BDF8` | `#0EA5E9` |
| running | 前倾跑者 + 摆臂跨步 + 速度线 | `#D9F36A` | `#A3B82F` |
| cycling | 双轮 + 三角车架 + 车把 + 传动节点 | `#FBBF24` | `#F59E0B` |
| hiking | 双峰山形 + 登顶路径 | `#34D399` | `#10B981` |

## 资产清单（每枚）

- `<key>.svg` — 默认（品牌双色），站点导航使用
- `<key>-mono.svg` — 单色 `currentColor`，印刷/内联
- `<key>-active.svg` — 激活态（统一亮色、无减弱透明度）

由 `build-set.py` 从 base 确定性生成 mono/active。`validation/nav-icons-v1.png` 为 96/24/20/16px 预览。

## 站点落地与状态

- 三运动站 `SportIcon` 与 Header 统一引用 `brand/icons/<key>.svg`（同一映射，无分叉）。
- HEALTH 原生 shell 顶部/移动导航同样引用 `brand/icons/<key>.svg`。
- 默认：各自品牌色 + 透明背景；激活：CSS `opacity 0.8→1` 提亮（用当前站点主题色、无发光）；Hover：150–200ms 亮度/透明度变化；支持键盘焦点与 `prefers-reduced-motion`。
- 不修改 URL、导航顺序、主题存储、导航逻辑、运动数据与算法。
