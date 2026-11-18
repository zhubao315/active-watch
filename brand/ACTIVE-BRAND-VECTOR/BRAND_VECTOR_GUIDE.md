# ACTIVE 品牌矢量重建指南（BRAND_VECTOR_GUIDE）

本目录是从 `../ACTIVE_Brand_Identity_Board.png` **识别轮廓 → 贝塞尔重建 → 原生渐变填充**得到的真矢量资产。所有 logo/icon 都是 SVG Path + `linearGradient`，不嵌入位图、不含 Base64、不依赖外部字体，可无限缩放。

## 目录结构

```
ACTIVE-BRAND-VECTOR/
├── master/     active-symbol, horizontal, vertical, wordmark, monochrome, white
├── sub-brands/ health / running / cycling / hiking
├── watch/      active-watch-symbol / active-watch-logo
├── favicon/    favicon.svg + 16/32/64 + apple-touch
├── png/        1024/2048/4096 透明导出 + 深/浅底导出
└── validation/ all-assets.png、symbol-validation.png、render-all.mjs
```

## 重建口径（诚实说明）

- 源图是 1672×941 的品牌展示板，A 标志最大实例约 160×112px。据此人工重建三条闭合 Path（上升笔画 / 下降笔画 / 底部弧线），保留原图的负空间比例、蓝色→青色渐变方向与三段结构。
- 四枚子品牌图标按板中「四大子品牌图标」卡片重建：健康心率波形（线性）、跑步人形剪影、骑行几何自行车、徒步双峰+路径（线性描边）。
- ACTIVE WATCH 用独立矢量圆形节点 + 连接线重绘，中央 A 复用主符号 Path。
- 字标保留可编辑 `<text>` 版本（Manrope ExtraBold 800 / 字距 2.2px，副标 Fira Code 500 / 2.1px）；生产严格场景可将文字转路径。
- 原图分辨率不足以确认的微小细节未虚构；以几何上合理的重建替代。

## 颜色（全部 SVG 原生值）

渐变：青 `#22D3EE` → 亮蓝 `#38BDF8` → 深蓝 `#2563EB` / `#1D4ED8`。
子品牌：HEALTH `#38BDF8` · RUNNING `#D9F36A` · CYCLING `#FBBF24` · HIKING `#34D399`。
背景：Midnight `#07111F` · Deep Navy `#0B1D33`。文字：Paper White `#F7FAFF` · Soft Slate `#CBD5E1` · Muted Steel `#94A3B8`。

## 验证结果

`validation/all-assets.png` 展示：黑 / 深海军蓝 / 白 / 棋盘格透明四种背景均边缘干净，无黑边白边、无颗粒；16px–1024px 全部可辨认，曲线平滑、渐变连续、负空间完整。PNG 导出由 `render-all.mjs` 用 Chromium 对 SVG 截图生成（非放大位图）。

## 站点使用

`brand/assets/` 中的 `active-mark.svg`、`icon-*.svg`、`watch-mark.svg`、`favicon.svg` 为本目录规范副本，由 `sync.sh` 同步到四站。站点组件 `BrandMark` / `SportIcon` 引用这些 SVG；深色底用 `active-logo-white.svg`。
