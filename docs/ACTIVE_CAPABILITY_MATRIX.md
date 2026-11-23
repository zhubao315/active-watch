# ACTIVE 能力现状矩阵

> 用途：任何「优化建议」落地前先对照本表。表中已登记的能力，直接判定为重复，不得再作为缺口重做。
> 依据：`/oc` 四站 + `active-watch` 源码勘察（2026-11-23），并对照 `ACTIVE_UPGRADE_ROADMAP.md`、`ACTIVE_PERFORMANCE_BASELINE.md`、`ACTIVE_TEST_COVERAGE.md` 与 `running/docs/ACTIVE_ROADMAP.md`。
> 维护位置：`active-watch/docs/`（跨站治理文档，单一事实源）。

## 1. 跨站能力（四站共有或四站联动）

| 能力 | 状态 | 证据 |
|---|---|---|
| 四站全局导航 | ✅ 已实现 | 三运动站 `src/components/BrandNav/index.tsx`（移动底部、当前站高亮）；health `dashboard/cross_sport.js`；四站 README 顶部四站链接 |
| 主题零闪烁 + 跨站共享 | ✅ 已实现 | 各站 `index.html` 内联脚本读写 `zhubao315-theme`（同源四站共享） |
| 品牌单一事实源 + 防漂移 | ✅ 已实现 | `active-watch/brand/` + `brand/sync.sh` + 四仓 `BRAND_MANIFEST.sha256` + Brand Guard |
| 四站在线巡检 / 失败告警 | ✅ 已实现 | `active-watch/.github/workflows/patrol.yml`：可用性、品牌同源、数据新鲜度、失败工作流；异常自动开唯一 issue |
| COROS 共享配额租约账本 | ✅ 已实现 | `state/fit-quota.json`，reserve→sync→reconcile，fail-open 降级 10 |
| 按年数据分片 + 构建对账 | ✅ 已实现 | `build-data-shards.mjs` + `verify-shards.mjs`（checksum / 条数 / 年份齐全），进入 PR 门禁与发布链路 |
| 轨迹按年懒加载 | ✅ 已实现 | 各站 `utils/tracks.ts`：「用到才 fetch 该年」+ 会话缓存 |
| 3D 场景按需加载 | ✅ 已实现 | `TerrainCard` + Vert/three.js + `React.lazy` + WebGL 错误边界；首屏 3D 场景请求实测为 0 |
| 数据水位 | ✅ 已实现 | 三运动站 `public/data-watermark.json` + 巡检双时钟阈值 |
| 隐私 / 数据公开治理 | ✅ 已实现 | `ACTIVE_PRIVACY_REVIEW.md`、`DATA_PUBLICATION.md` |
| 工作流缓存 / 软失败 | ✅ 已实现 | `setup-python cache:pip`、`actions/cache` pnpm store、`continue-on-error` + soft-fail、`git diff` 非空才构建 |
| 统计严谨性（Spearman / BH-FDR / n≥30） | ✅ 仅 health | `health/coros_health/stats_rigor.py` + `tests/test_stats_rigor.py` |

## 2. 各站已实现能力

### RUNNING
- ✅ 个人最佳墙：5K / 10K / 半马 / 全马（`JourneyStats` 的 `pbRows` / `prRows`）
- ✅ 年度热力图、配速/里程趋势、训练分析
- ✅ 按周烘焙 3D 场景（`bake-scenes.yml`）
- ✅ 首屏性能基线已采集（2026-11-23）

### CYCLING
- ✅ ≥3 km / 全部活动 双口径，全站 KPI·趋势·日历·地图·表格统一 scope（`ActivityScopeSwitch`）
- ✅ 爬升覆盖率由真实统计替代硬编码
- ✅ 首屏性能基线已采集（2026-11-23）
- ⛔ **原始数据无功率字段**，代码明确不展示 FTP / NP / 功率曲线——不要作为「缺失功能」提出

### HIKING
- ✅ 季节 / 省份 / 时段筛选（`Journey` 的 `buildSeasons` + `HikingDashboard` 的 filterNote）
- ✅ 聚合缓存（与另两站一致）
- ✅ 3D 地形 + 海拔剖面组件（`TerrainCard` / `VertTerrain` / `ElevationPanel`）
- ✅ 首屏性能基线已采集（2026-11-23）

### HEALTH
- ✅ 数据仓库：COROS 官方 MCP → SQLite + CSV + gzip 时间序列
- ✅ 睡眠 / HRV / 静息心率 / 压力 / 步数 / 训练负荷趋势面板
- ✅ 跨运动年度 / 月度聚合（距离分列不相加、时长聚合标覆盖率）
- ✅ 90 项 Python 单测
- ✅ 健康指标日表（health-only）

## 3. 明确「未做 / 进行中」（才是真缺口）

按 `ACTIVE_UPGRADE_ROADMAP.md` 的阶段：

- **阶段 2 剩余**：首屏消费迁移（页面先读预计算摘要、明细按年 fetch，配套加载态/深链接/轨迹发射）——核心剩余工作；列表虚拟滚动；性能预算设定（基线已具备）
- **阶段 3**：RUNNING PB 正式赛事与 GPS 估算分离、配速进化、训练一致性；CYCLING 速度分布 / 爬升效率；HIKING 地图主体化、剖面↔3D 联动、最高海拔榜；HEALTH 当前状态 vs 基线、变化方向、滞后分析
- **阶段 4**：ACTIVE Daily Timeline（按日关联睡眠/HRV/负荷与三类活动，跳回原站）
- **阶段 5**：浏览器级巡检进入 patrol、ACTIVE System Status、发布报告
- **测试**：三运动站**没有统计逻辑单元测试**（`runningStats.ts` / `cyclingStats.ts` / `hikingStats.ts`），见 `ACTIVE_TEST_COVERAGE.md`
- **AI 周报**：全仓无 LLM 调用——真实空白，但须先过隐私 / 治理评审，且模型只措辞不产数值

## 4. 使用规则

1. 新建议先查本表；命中「✅ 已实现」的直接驳回。
2. 命中「⛔」的（如 FTP）属于数据源不支持，不得作为缺陷。
3. 命中「未做」的，按阶段顺序执行，一站一轮。
4. 任何统计口径改动须与现有 `*Stats.ts` / `stats_rigor.py` 对账，禁止另起一套。
5. 涉及共享品牌资产的改动必须走 `brand/sync.sh` 并更新 `BRAND_MANIFEST.sha256`。
