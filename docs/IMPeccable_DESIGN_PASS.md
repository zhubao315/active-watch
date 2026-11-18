# Impeccable 设计复审与「去 AI 味」改造（2026-11-18）

本章记录用 Impeccable v4.9.2 的设计检测器（62 条确定性规则）对四站 + 运营中枢的复审与改造。工具已安装到 `.opencode/skills/impeccable`（OpenCode），检测器经本地 npm 引擎运行。

## 方法

按 skill 的 `typeset` + `craft-floor` playbook 执行：先扫描渲染页面建立基线，按 antipattern 归因，再逐层修复（一屏/一维度一批），每批后复扫。约束：保留 ACTIVE 既有视觉世界（深蓝底 / 四站强调色 / 自托管字体 / 指标语义色），不替换品牌，不改动数据口径。

## 基线 → 结果（渲染页，advisory 已排除）

| 站点 | 改造前 | 改造后 | 主要消除的 tell |
|---|---|---|---|
| RUNNING | 479 | 6 | 458 处 <11px 功能文字、7 处 kicker/章节编号、嵌套卡片、地图署名低对比 |
| CYCLING | 489 | 6 | 468 处微文字、kicker、嵌套卡片、低对比 |
| HIKING | 432 | 7 | 408 处微文字、kicker、灰底灰字、低对比 |
| HEALTH | 595 | 19 | 501 处微文字、66 处灰字压色块、青色发光、AI 紫蓝调、热图低对比 |

「去 AI 味」依据 craft floor 的**绝对禁令**：标题上方 kicker/eyebrow、装饰性章节编号（01/02/03）、<11px 功能文字、零偏移彩色发光、渐变文字、嵌套卡片、色块上的灰字。

## 具体改动

1. **字号阶梯**：把散乱的 0.5–0.69rem 任意值统一到 11/12px 阶梯（功能文字 ≥11px）；Tailwind `text-[10px]`→`text-[11px]`；覆盖四站的 CSS modules 与 HEALTH 的 `dashboard/style.css`。
2. **移除 kicker 与章节编号**：三站 `SectionHeader` 保留 props 兼容调用点，但不再渲染 kicker/编号，标题独自承担层级。
3. **文字随底色**：把 `--subtle` 从纯灰 `#64748b` 改为带蓝调 `#8fa6bd`（浅色主题 `#5c6b7c`），提升在卡片底色上的对比；HEALTH 表格 caption/`em` 同步受益。
4. **HEALTH 热图**：降低蓝色混合上限（88%→52%），文字改 `--text`，修复 35 处低对比；去除日历/提示点的零偏移发光与桶状渐变条。
5. **跨站统一**：标题 `text-wrap: balance`、正文 `text-wrap: pretty`（渐进增强）；HEALTH 修正 `#777`/`#5f5f5f` 硬编码灰为 token。
6. **上下文文件**：四仓写入 `PRODUCT.md` / `DESIGN.md`（Impeccable `init`/`document` 的产物），固定视觉世界与禁令，供后续设计自动遵循。

## 残余（均为有意的密度/结构取舍）

- `nested-cards`：三站仪表盘「卡片内卡片」是数据分组结构，属 Operate 模式的可接受布局，不为此重构 DOM。
- `tiny-text`（HEALTH 17、运动站 1–2）：11.2–11.8px 的密集图例/脚注，已在 11px 功能文字下限之上，符合仪表盘密度。
- 1 条 line-length（HEALTH 长说明）：中文长句，用 `text-wrap: pretty` 已改善断行，保留完整语义不被截断。

## 验收

- 四站 `pnpm check` / `build` / `verify-dist` / `verify-shards` 全过；HEALTH 92 项单测全过；品牌 13 项契约测试全过。
- 检测器复扫：四站 findings 下降 90%+，无新增类别。
