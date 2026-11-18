# Frontend UI Engineering 复审（2026-11-18）

使用技能：`frontend-ui-engineering`（安装于 `.opencode/skills/frontend-ui-engineering`，来自 github.com/lumpinif/frontend-ui-engineering），按其 `review-checklist.md` 对五站做 UI 工程复审。项目为个人运动健康仪表盘（Operate / Read 模式）。

## 复审方法

- 静态扫描五仓源码：outline 移除、`!important`、`will-change`、正 tabindex、`<div onClick>`、reduced-motion 覆盖。
- 浏览器审计（四站 × 4 分辨率 1440/768/390/360）：标题层级、可访问名称、焦点可见性、触控目标尺寸、溢出、控制台错误。
- 结论先行、按用户影响排序、最小修复，不做无关重构。

## 发现与修复

### P1 · 可点击 `<div>` 无按钮语义（三运动站）
- 文件：`src/components/YearStat/index.tsx`（running/cycling/hiking）。
- 问题：整块年度统计卡用 `<div onClick>` 切换年份，键盘用户无法聚焦/操作，无 accessible name。
- 影响：键盘与屏幕阅读器用户无法使用年度切换。
- 修复：改为 `<button type="button">`，补 `aria-label`，保留 hover/视觉与 `useHover` 行为。三站一致。

### P2 · 触控目标过小（四站）
- 发现（移动端）：scopeBar 链接 21–22px 高、日历格 18px、图例按钮 19–23px、排序按钮 19px、HEALTH 热图格 20px、页脚链接 17px。
- 影响：真实手机误触率高。
- 修复（最小 CSS）：
  - 三站 scopeLink/scopeClear `min-height:26px`；图例按钮 `min-height:26px`；排序按钮 `min-height:24px`；≤560px 日历格 `min-width/height:26px`；页脚 `.link min-height:26px`。
  - HEALTH `.hcell` 20→24px、`.tool min-height:26px`、`.sport-link min-height:26px`、移动端 nav/footer 链接 `min-height:32px`。
- 说明：年柱图 `~20×176px` 为数据驱动的图表内联元素（宽度由年份数决定，高度充足），属 WCAG 2.5.8 内联/间距例外，保留不改以免破坏图表布局。

### 通过项（无需修复）
- 焦点可见：四站各抽样 30 个可聚焦控件，全部有可见 outline/box-shadow。
- 标题层级：无跳级；主标题唯一（承接上一轮 Profile 2.0）。
- 可访问名称：按钮/链接均有文本或 aria-label；图标按钮有 aria-label。
- 无 `!important`（五站 0 处）、无 `will-change`、无正 tabindex、无 `div[onclick]` 残留（修复后）。
- reduced-motion：四站均有覆盖。
- 布局：1440/768/390/360 无横向溢出、无遮挡、无控制台错误。

## 验证

- 三站 `pnpm check` / `build` / `verify-dist` / `verify-shards` 全过；HEALTH 92 项单测全过；品牌 13 项测试全过。
- 修复后浏览器复审：焦点、标题、可访问名称、溢出、错误 0 发现；剩余触控项仅为图表内联元素（有据可依的例外）。
- 保持所有数据口径、URL、主题、筛选、深链、地图/3D、COROS 同步不变。
