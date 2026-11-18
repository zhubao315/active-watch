# ACTIVE 系统审计（2026-11-18 复审）

审计对象：HEALTH / RUNNING / CYCLING / HIKING / ACTIVE-WATCH 五个仓库（本地检出 + 线上页面 + GitHub Actions 定义）。
基线：各仓 `docs/ACTIVE_SYSTEM_AUDIT.md`（2026-11-13）。本文只记录复审新增结论与本轮处理结果，不推翻既有审计。

## 1. 总体判断

系统已具备「个人运动健康数字基础设施」的底座：统一品牌单一事实源、共享配额账本、每日巡检、按年拆分 GPS 轨迹的数据管线。当前主要风险不在功能缺失，而在三处：

1. 巡检把「代码提交时间」当作「数据新鲜度」，且 API 失败被静默跳过；
2. PR 阶段只跑 Python Black，TypeScript 统计与构建不在门禁内；
3. 相关性分析缺样本量门槛、Spearman 与多重比较校正。

评分沿用复审结论：HEALTH 8.5、RUNNING 8.3、CYCLING 7.6、HIKING 8.0、ACTIVE-WATCH 7.8，整体 8.1。性能与可扩展性（6.8）是最弱项，优先级高于新增图表。

## 2. 问题清单（现状 / 文件 / 原因 / 风险 / 影响 / 方案 / 验收）

### A. 品牌验收断言使用已退役名称 — 已修复
- 现状：`brand/verify-live.mjs:25-28` 把 `ZB ACTIVE` 当作正确字标；`brand/verify-sites.mjs:33` 同样。
- 原因：品牌 2.0 已更名 ACTIVE，但断言未更新；旧名称同时被巡检当作应清除对象，规范自相矛盾。
- 风险：中。错误断言会掩盖真实品牌回归。
- 影响：四站品牌验收。
- 方案：抽出 `brand/brand-contract.mjs`，统一 DOM 选择器与纯校验函数；旧名称改为失败条件；`ZB ACTIVE` 包含 `ACTIVE` 子串，校验前先剥离旧名。
- 验收：`node --test tests/brand-contract.test.mjs`（12 项全过，含旧品牌必须失败用例）。

### B. 数据新鲜度依赖提交时间 — 已修复
- 现状：`scripts/patrol.mjs:91-101` 用最近提交判断 running/cycling/hiking 数据是否新鲜。
- 原因：README/代码提交也会产生新 commit，与运动数据无关。
- 风险：高。数据停更可能长期不告警。
- 影响：三个运动站的数据可信度。
- 方案：三仓新增 `scripts/write-data-watermark.mjs`，同步后生成 `public/data-watermark.json`（日期/条数/SHA256/同步时间/构建版本）；巡检改为读水位。同步时间与活动日期采用两个独立阈值——徒步活动可能数月为空，不能与主站同判。
- 验收：`tests/data-watermark.test.mjs`（含「徒步安静一个月但同步正常」用例）；三仓本地生成水位文件成功。

### C. 巡检 API 错误静默忽略 — 已修复
- 现状：`scripts/patrol.mjs:122` `if (status !== 200) continue;`。
- 原因：把「无失败工作流」与「查询失败」混为一谈。
- 风险：高。权限变化/私有化后巡检会长期假绿。
- 影响：整条巡检链路可信度。
- 方案：gh/web 增加 429/5xx/网络错误重试与退避；每种非 200 明确区分并记录为 incident；`actions: read` 权限写入 patrol.yml；每个检查记录开始/结束/结果到 issue。
- 验收：patrol.yml 权限变更；代码审查确认不存在裸 `continue`。

### D. PR 质量门禁不足 — 已修复
- 现状：三运动站 `ci.yml` 仅 Python Black；`lint`/`check` 脚本带 `--fix`/`--write`。
- 原因：CI 只读原则未落实，构建/类型检查放在发布链路。
- 风险：中高。TS 统计错误可合并后才暴露。
- 影响：三站。
- 方案：拆分 `format:write`/`format:check`/`lint`/`lint:fix`/`typecheck`；PR 新增 web job：lint + tsc + build + verify-dist + Playwright smoke；修复既有 unused-vars 与 useHover 的 Timeout 类型问题。
- 验收：三仓 `pnpm run check`、`pnpm build`、`verify-dist.mjs` 本地全绿。

### E. HIKING 聚合重复计算 — 已修复
- 现状：`src/hooks/useActivities.ts` 每次调用重算 cities/runPeriod/years，10+ 调用点。
- 原因：未采用 running/cycling 的模块级缓存模式。
- 风险：中（随筛选/地图交互放大）。
- 方案：改为模块初始化构建一次缓存。
- 验收：typecheck/lint/build 通过。

### F. 相关性严谨性不足 — 已修复（HEALTH）
- 现状：仅 Pearson；最小样本 8；5 项比较独立解读；三处重复实现。
- 原因：历史实现只覆盖基础统计。
- 风险：中。弱相关被过度解读。
- 方案：新增 `coros_health/stats_rigor.py`（Spearman、双侧 p、Benjamini-Hochberg FDR、n≥30 门槛），以附加字段方式接入 `db.correlations()`，页面相关性表新增 ρ/p/q 列与 ⚠ 样本标记；不改原 r/n/CI 语义。
- 验收：90 项 Python 单测全过；重新生成的 data.json 含新字段。

### G. CYCLING 双口径缺失 — 已修复
- 现状：3 km 门槛硬编码在 `useActivities.ts:5`，无 UI 切换；所有统计只有单一口径。
- 原因：门槛放在数据层而非视图层。
- 风险：中。2152 条短途记录长期不可见。
- 方案：同一数据源构建 standard/all 两套聚合，通过 `useSyncExternalStore` 统一 scope；新增 `ActivityScopeSwitch`；深链接 `?scope=all` 保留。原始 JSON 与 splitActivities 输出均未改动。
- 验收：lint/typecheck/build/verify-dist 通过。

### H. RUNNING 爬升覆盖率硬编码 0 — 已修复
- 现状：`JourneyStats/index.tsx` 写死「爬升字段 0 / 2039 条」，实际 1760 条有值。
- 原因：展示文案硬编码。
- 方案：从活动数据实时统计 `climb_terrain` 为有限数的记录数。
- 验收：typecheck 通过。

## 3. 尚未处理（按优先级）

- **P0 性能**：首屏仍同步导入全量 meta（cycling eager chunk 3.37 MB）；需按年分片 + 生涯摘要预计算 + 列表虚拟滚动。
- **P1 可移植性**：`brand/build-assets.mjs` 绝对路径已改为脚本相对 + 环境变量；仍需 CI 实测与产物入库规范。
- **P1 跨运动时间线**：HEALTH 与三站尚无按日关联（roadmap P2-5）。
- **P2 Vite 4 → 7/8 升级**：需独立分支验证 `splitActivities` 虚拟模块钩子。
- **P2 数据对账**：分片/预计算统计必须与现有统计逐项对账。

详见 `ACTIVE_UPGRADE_ROADMAP.md`。
