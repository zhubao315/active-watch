# ACTIVE 2.0 升级路线与执行记录

## 已完成（2026-11-18 本轮）

按复审建议的推进顺序「ACTIVE-WATCH → RUNNING/CYCLING → HEALTH → HIKING」执行，优先正确性与工程治理。

### 阶段 1 · ACTIVE-WATCH 工程治理
- [x] `verify-live.mjs` / `verify-sites.mjs` 品牌断言改用 ACTIVE，旧名改为失败条件；抽出可测试契约 `brand/brand-contract.mjs`
- [x] 三运动站新增 `public/data-watermark.json` 生成器并接入 coros_sync.yml；巡检改读真实数据水位（双时钟阈值）
- [x] 巡检 API 重试/退避、错误显式化、`actions: read`、逐项执行记录
- [x] 配额账本 9 项自动化测试
- [x] `package.json` + `pnpm-lock.yaml` + `.gitignore`；`build-assets.mjs` 去除 `/oc/...` 硬编码
- [x] 21 项 Node/Python 测试全绿

### 阶段 1b · 三运动站 PR 门禁
- [x] package.json 脚本拆分（只读 check/lint/typecheck vs 写模式 format:write/lint:fix）
- [x] ci.yml 新增 web job：lint + tsc + build + verify-dist + 浏览器 smoke
- [x] 修复阻塞门禁的既有错误（useHover 的 Timeout 类型、unused vars）
- [x] 三仓本地验证全绿

### 阶段 1c · 定向修复
- [x] HIKING 聚合缓存（与 RUNNING/CYCLING 一致）
- [x] CYCLING ≥3 km / 全部活动 双视图，全站统一 scope，深链接保留
- [x] RUNNING 爬升覆盖率硬编码 0 → 真实统计
- [x] HEALTH 相关性严谨性（Spearman + p + BH-FDR + n≥30 门槛），90 项单测通过

## 进行中 / 下一步

### 阶段 2 · 数据性能升级
- [x] 生涯摘要 `career-summary.json`、`yearly-summary.json`、按年活动分片、`data-manifest.json` 生成链路（复用现有统计引擎，逐字段对账，失败即阻断构建）
- [x] `verify-shards.mjs` 进入 PR 门禁与发布链路；分片不含 GPS 轨迹
- [ ] **首屏消费迁移**：页面先读预计算摘要，明细按年 fetch。需要同步处理：加载态/骨架屏、深链接等待数据、`splitActivities` 在没有静态 activities.json 导入时仍能发射轨迹文件、地图与 3D 懒加载。这是本阶段剩余的核心工作。
- [ ] 列表虚拟滚动（现有表格已做「加载更多」分页，不必重写）
- [ ] 采集 LCP/INP/CLS 与首屏 JS/请求基线，设定性能预算

### 阶段 3 · 四站专业能力
- RUNNING Performance Lab：PB 中心（正式赛事与 GPS 估算分离）、配速进化、训练一致性。
- CYCLING：双视图文案与各模块口径一致性复验；速度分布、爬升效率。
- HIKING：地图主体化、海拔剖面/3D 联动、最高海拔榜。
- HEALTH：当前状态 vs 基线、变化方向、滞后分析（沿用新增严谨性字段）。

### 阶段 4 · 跨运动整合
- ACTIVE Daily Timeline：按日关联睡眠/HRV/负荷与三类活动，跳回原站，距离不混加，缺失显示覆盖率。

### 阶段 5 · 监控与发布治理
- 浏览器级巡检进入 patrol；ACTIVE System Status；性能预算；发布报告（代码/数据/品牌版本 + SHA256 + 测试结果 + 部署时间）。

## 工程原则（不可违反）

1. 原始数据永不因展示层改动而修改。
2. 缺失不等于 0；不伪造不存在的字段。
3. 统计单一可信源，分片后必须对账。
4. 70% 统一 + 30% 个性；不迁移 HEALTH 到 React，不合并 Monorepo。
5. CI 只读；Vite 升级单独分支试点（RUNNING 先行），验证 `splitActivities` 钩子。
