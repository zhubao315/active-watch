# ACTIVE 架构（2026-11-18）

## 1. 系统边界

```
COROS / 手动导入 ──▶ 各站同步工作流 ──▶ 原始数据（FIT/DB/activities.json，只增不改）
                                      │
                                      ├─▶ 构建期 splitActivities（轨迹按年拆出）
                                      ├─▶ 构建期统计（现状：运行时计算；目标：预计算）
                                      └─▶ data-watermark.json（新增，数据水位）
                                             │
                      GitHub Pages ──────────┴──▶ active-watch patrol（巡检）
                            │                          │
                     四站页面（用户）                   └─▶ 单一 watch:incident issue
```

## 2. 五个仓库的职责

| 仓库 | 定位 | 技术 | 发布 |
|---|---|---|---|
| health | 健康驾驶舱 | 原生 JS + Chart.js + Python(stdlib) | health_sync.yml / body_sync.yml |
| running | 跑步表现实验室 | React 19 + TS + Vite 4 | coros_sync.yml |
| cycling | 骑行表现（双口径） | 同上 | coros_sync.yml |
| hiking | 山野探索 | 同上 + Three.js/vert | coros_sync.yml（周更） |
| active-watch | 运营与治理中枢 | Node 22 + Python(stdlib) | 不发布页面，只跑 patrol |

## 3. 统一层（70%）

- **品牌单一事实源**：`active-watch/brand/` → `sync.sh` 复制到四仓 → 各仓 Brand Guard 校验 `BRAND_MANIFEST.sha256` → patrol 校验四仓 blob 同源 + 线上 favicon 字节一致。
- **品牌契约**：`brand/brand-contract.mjs` 一份定义，浏览器验收与单元测试共用；当前品牌唯一为 ACTIVE，旧名 `ZB ACTIVE` 必须不存在。
- **配额账本**：`active-watch/state/fit-quota.json`，三运动站 `quota_lease.py` reserve → sync → reconcile，SHA 乐观锁 + fail-open 降级；本轮补 9 项自动化测试。
- **数据水位**：`state/data-baselines.json` 定义计数基线与两套新鲜度阈值；各站 `public/data-watermark.json` 由真实同步生成。
- **巡检**：`scripts/patrol.mjs`，检查项均记录结果，API 异常显式告警，恢复后自动关 issue。

## 4. 个性化层（30%）

- HEALTH：原生 shell，不迁移 React；睡眠按醒来日索引，缺失为 NULL，个人 7 天/28 天基线。
- RUNNING：加权配速，`runningStats.ts` 为统计真源。
- CYCLING：`≥3 km` 标准视图与全部活动视图，同一数据源、统一 scope。
- HIKING：单次爬升 / 累计爬升 / 最高海拔三者独立；地图与 3D 场景懒加载。

## 5. 数据流关键约束

1. 原始数据（FIT/SQLite/CSV/原始 JSON）永不因展示层改动而修改。
2. 缺失值不等于 0；无功率/踏频数据不生成相应指标。
3. 跑步/骑行/徒步距离不混合累计。
4. 相关性只作探索性描述，不作因果或医学结论。
5. 深链接（date / year / runId / scope）在视图切换时保留。

## 6. 本轮架构变更

- 新增 `data-watermark.json` 作为巡检的机器可读数据契约。
- 品牌断言从脚本内联逻辑抽为可测试的纯模块。
- CYCLING 把距离门槛从数据层上移到视图层（`useSyncExternalStore`），原始数据集不变。
- 巡检 API 层统一重试/退避，并把「检查自身可靠性」纳入 issue 正文。
