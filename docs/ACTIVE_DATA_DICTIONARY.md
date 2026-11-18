# ACTIVE 数据字典（2026-11-18）

## 1. 数据水位 `data-watermark.json`

由 `tools/write-data-watermark.mjs`（三运动仓各有一份逐字节副本）在同步成功后写入站点 `public/`。

| 字段 | 类型 | 含义 | 约束 |
|---|---|---|---|
| `schema_version` | int | 契约版本 | 必须 = 1 |
| `site` | string | 站点键 | health/running/cycling/hiking |
| `generated_at` | ISO-8601 | 水位生成时间 | 可解析 |
| `latest_activity_date` | `YYYY-MM-DD` | 最近一条活动的本地日期 | 与 `source_updated_at` 独立判定 |
| `activity_count` | int | 活动条数 | > 0；跌幅 >10% 触发巡检 |
| `source_updated_at` | ISO-8601 | 最近一次成功同步时间 | 各站独立阈值（3/3/10 天） |
| `data_checksum` | string | 原始 activities.json 的 SHA-256 | 格式 `sha256:<64hex>` |
| `build_version` | string | 产生该水位的构建版本 | 非空 |
| `status` | string | 数据质量状态 | 必须 `ok` |

生成公式（与展示层无关）：

- `latest_activity_date = max(start_date_local.slice(0,10))`
- `activity_count = activities.length`
- `data_checksum = sha256(src/static/activities.json bytes)`

## 1b. 构建期数据分片 `public/data/`（2026-11-18 新增）

由 `tools/build-data-shards.mjs` 生成，Vite 原样复制到 `dist/data/`。

| 文件 | 内容 | 用途 |
|---|---|---|
| `career-summary.json` | `scopes[scope].totals`（直接调用现有 `*Stats.computeTotals`）、年份数组、活动数、最近日期 | 首屏摘要候选；不重算 |
| `yearly-summary.json` | 每个 scope 每年的 YearPoint（来自 `buildYearSeries`） | 年度趋势候选 |
| `yearly-activities/<scope>/<year>.json` | 该年活动元数据，**已剥离 `summary_polyline`**，有轨迹时置 `has_track: true` | 按需加载明细 |
| `data-manifest.json` | 源文件 SHA-256、分片清单（年份/条数/校验和）、`reconciled` 对账结果 | 完整性验证 / 增量加载 |

对账规则：`buildDataset(full)` 与 `buildDataset(shard 合并)` 按 `run_id` 稳定排序后，`computeTotals` 输出必须逐字节相同；不一致则构建失败。CYCLING 同时生成 `standard`（≥3 km）与 `all` 两套，共用同一数据源。

生成时实测：RUNNING 2,039 条/12 年 4.1 MB，CYCLING 5,786+7,938 条/14 年 6.1 MB，HIKING 344 条/14 年 1.1 MB（均已去轨迹）。

## 2. 数据基线策略 `state/data-baselines.json`

| 站点 | 基线条数 | 同步阈值(天) | 活动日期阈值(天) | 说明 |
|---|---|---|---|---|
| running | 2039 | 3 | 14 | 日更 |
| cycling | 7938 | 3 | 14 | 日更，含全部 2152 条短途 |
| hiking | 344 | 10 | 60 | 周更；活动本身有季节性 |

## 3. 运动活动通用字段

三运动站 `src/static/activities.json` 的原始记录（由 splitActivities 在构建期剥离 `summary_polyline`，年份轨迹单独输出）：

| 字段 | 含义 | 缺失语义 |
|---|---|---|
| `run_id` | 活动唯一标识（去重键） | 不得重复 |
| `type` | 运动类型（Run/Cycling/Hiking） | 跨运动隔离，不得混算 |
| `start_date_local` | 本地开始时间 | 年份/日/日历口径来源 |
| `distance` | 米 | 缺失不补 0，计算时过滤 |
| `moving_time` | 移动时长 | 缺失不补 0 |
| `average_speed` | m/s | 用于加权配速/速度 |
| `average_heartrate` | bpm | 覆盖不足时不分析强度 |
| `climb_terrain` | 地形爬升 m | 仅 running 部分记录有值；Hiking 优先用它 |
| `altitude_max` | 最高海拔 m | 与累计爬升是不同指标 |
| `summary_polyline` | GPS 轨迹 | 构建期移至按年轨迹文件 |

## 4. HEALTH 指标

- 存储：`coros_health/db.py` 定义 11 张表；`daily` 视图左连接各指标。
- 时间口径：睡眠/HRV 按**醒来日**索引；步数/负荷/压力按自然日。
- 缺失：NULL，与真实 0 严格区分（`zeros.suspicious` 标记可疑零）。
- 基线：个人 7 天均值 / 28 天尾随基线，不与人群比较。
- `data_quality.json`：`latest_data_date` 只代表 daily 视图最后一行；每个 KPI 另有自己的 `latest[key].date`，二者不可互替。
- 相关性字段（本轮新增，附加不覆盖）：`spearman_rho`、`p_value`、`q_value_bh`、`coverage`、`min_samples=30`、`samples_ok`、`method`。

## 5. 配额账本 `state/fit-quota.json`

```
{"days": {"YYYY-MM-DD": {"running": n, "cycling": n, "hiking": n}}}
```

- 每天总量 50；单仓硬上限 45；reserve 默认想拿 10，按剩余额度收敛。
- reconcile 把预留量收敛到实际用量，未用完当天归还。
- 仅保留最近 3 天；SHA 乐观锁冲突重试 3 次；账本不可达时 fail-open 用保守值 10。
