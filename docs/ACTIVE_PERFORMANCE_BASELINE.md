# ACTIVE 性能基线（2026-11-18，构建产物实测）

这是「优化前」基线。第 1–5 节数字来自本地构建产物与源码文件统计；第 6 节为 2026-11-23 补充的**浏览器实测**（Playwright + Chromium，线上 Pages），已覆盖 LCP/INP/CLS 与首屏 JS/请求基线，补齐了原先「尚未采集」的缺口。目标值见第 7 节。

## 1. 源文件与首屏数据

| 站点 | activities.json 源文件 | gzip | 记录数 | 首屏 meta chunk |
|---|---|---|---|---|
| RUNNING | 4.2 MB | — | 2,039 | 约 3.2 MiB（14 个年份轨迹共 3.3 MB，按需加载） |
| CYCLING | 20.1 MB | ≈5.9 MB | 7,938 | 3.37 MB（14 个年份轨迹共 15.3 MB，按需加载） |
| HIKING | 1.1 MB | ≈362 kB | 344 | 小；10 个年份轨迹共 0.9 MB，按需加载 |

结论：轨迹按年拆分机制已经生效且应保留；真正的首屏负担是**同步导入的活动元数据本身**，不是 GPS 轨迹。

## 2. 目录体积

- CYCLING `dist/` 中年份轨迹合计 ≈15.3 MB（最大 2023：3.3 MB）。
- HIKING `dist/` ≈15 MB，其中 232 组 `.scene` / `.scene.json`；3D 懒加载 chunk 约 651 kB（gzip 173 kB），已通过 `manualChunks` 排除出 eager vendors。
- RUNNING 场景按周烘焙，独立 `bake-scenes.yml`。

## 3. 现有优化点（保留）

- `plugins/splitActivities.ts`：构建期剥离 polyline，按年输出轨迹；运行时 `tracks.ts` 按年 fetch + 缓存。
- RUNNING/CYCLING 已做模块级聚合缓存；HIKING 本轮补齐。
- HIKING `TerrainCard` 使用 `React.lazy` + `Suspense` + WebGL 错误边界。

## 4. 构建期分片（本轮已完成数据层）

- 三站已生成 `career-summary.json` / `yearly-summary.json` / `yearly-activities/<scope>/<year>.json` / `data-manifest.json`，统计直接复用现有 `*Stats.ts`，含逐字段对账门槛；`verify-shards.mjs` 在 CI 与发布链路校验 dist 产物与每个分片校验和。
- 分片中的活动元数据已剥离 GPS（沿用 splitActivities 口径），体积远小于源文件；轨迹仍由原有按年文件按需加载。
- **尚未完成的部分**：页面仍通过 `useActivities` 同步导入完整 meta。真正的首屏解耦需要把数据层改成「摘要优先 + 分片按需 fetch」并配套加载态、深链接等待与 splitActivities 发射逻辑调整——作为阶段 2 的下一步，不建议在未做这些配套前直接移除同步导入。

## 5. 待优化（按优先级）

1. **首屏数据层迁移**：让页面先消费预计算摘要，活动明细按年 fetch；需同时处理加载态、深链接、地图/3D 与 splitActivities 轨迹发射。
2. **列表分页/虚拟滚动**：CYCLING 全部视图 7,938 条，地图批次渲染阈值（>240/18 帧/70ms）需复测。
3. **统计预计算对账**：年度/月度/PB 与现有 `runningStats.ts`、`cyclingStats.ts`、`hikingStats.ts` 逐项核对，禁止另起一套口径。
4. **缓存与压缩**：JSON/静态资源长缓存，`data-watermark.json` 与 `data_quality.json` 短缓存。

## 6. 浏览器实测基线（2026-11-23 补充）

采集方式：三站线上 Pages，Playwright + Chromium；3 档视口（desktop 1440×900 / mobile-390 / mobile-360）× 深浅主题（由 `zhubao315-theme` localStorage 控制）共 6 组；LCP/CLS/INP 由 PerformanceObserver 注入采集，加载后滚动触发交互。采集脚本已落地各站 `scripts/perf_baseline.py`，原始数据见各站 `docs/perf-baseline/<site>.json`，分站汇总见各站 `docs/PERF_BASELINE.md`。

| 站点 | LCP 范围 (ms) | CLS 最大 | INP 最大 (ms) | 首屏 JS (KB, 传输) | JSON (KB) | 3D 场景请求 |
|---|---:|---:|---:|---:|---:|---:|
| RUNNING | 1108–1996 | 0.0058 | 21.9 | 615 | 189 | 0 |
| CYCLING | 1320–2160 | 0.0034 | 20.4 | 953 | 723 | 0 |
| HIKING | 1052–1812 | 0.0071 | 18.8 | 507 | 36 | 0 |

结论：

- 六个组合全部满足第 7 节目标（LCP ≤ 2.5 s、INP < 200 ms、CLS < 0.1），当前无性能回归风险；
- 三站首屏 3D 场景请求均为 0，证明「场景按需」已生效（与第 3、4 节一致）；
- CYCLING 首屏 JS 953 KB / JSON 723 KB 为三站最高，与第 1 节记录的元数据规模吻合——**这是阶段 2「首屏消费迁移」的实测依据**；
- LCP 在同站不同视口/主题间波动约 500–900 ms，属网络/冷启动噪声，单次测量仅作初值；后续预算对比须同条件多次取中位数。

## 7. 目标值（对照基线）

| 指标 | 目标 |
|---|---|
| LCP | ≤ 2.5 s |
| INP | < 200 ms |
| CLS | < 0.1 |
| 首屏 JS | 记录基线后设定预算 |
| 地图首次可交互 | 记录基线后设定预算 |
| 3D 首次加载 | 仅在进入探索模块后发生 |

采集方式：四站各跑桌面/移动两档，记录 LCP/INP/CLS、首屏 JS 体积、首屏数据请求数、地图首次可交互时间、3D 首次加载时间，作为阶段 2 前后对照。
