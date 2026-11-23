# ACTIVE 测试覆盖（2026-11-18）

## 1. 本轮新增（active-watch）

| 测试 | 命令 | 数量 | 覆盖 |
|---|---|---|---|
| 品牌契约 | `node --test tests/brand-contract.test.mjs` | 5 | 当前品牌/旧品牌失败/稳定 DOM/主题/溢出/坏图 |
| 数据水位 | `node --test tests/data-watermark.test.mjs` | 7 | schema、站点、双时钟、计数跌幅、校验和、徒步季节性 |
| 配额账本 | `python3 -m unittest discover -s tests -p 'test_quota_lease.py'` | 9 | 并发申请、额度收敛、reconcile、SHA 冲突重试、网络失败、无 token、旧日期裁剪 |
| 统一入口 | `pnpm test` | 21 | 上述全部 |

关键回归用例：**`ZB ACTIVE` 必须先被剥离再检查 ACTIVE**，否则旧品牌因包含子串会通过——这是本轮测试发现并修复的真实缺陷。

## 2. 三运动站 PR 门禁（本轮新增）

`ci.yml` 的 `web` job 在 PR 上执行：

1. `pnpm install --frozen-lockfile`
2. `pnpm run check` = `eslint`（无 --fix）+ `tsc --noEmit`
3. `PATH_PREFIX=/<repo> pnpm build`
4. `SITE_SPORT=<sport> node scripts/verify-dist.mjs`
5. Playwright `scripts/smoke-theme.mjs`（导航、主题、无 JS 异常）

本地验证结果：三站 `check` / `build` / `verify-dist` 全部通过。

脚本已拆分：

- `format:write` / `lint:fix` —— 本地主动修改；
- `format:check` / `lint` / `typecheck` —— 只读检查；
- CI 只调用只读命令。

注：`format:check` 当前对既有代码会报大量风格差异（31 个文件），因此未作为硬门禁；先保持只读可观测，后续单独做格式收敛，且不得格式化 `brand-tokens.css`（会破坏 Brand Guard 清单）。

## 2b. 三运动站统计单测（2026-11-23 新增）

| 站点 | 文件 | 测试数 | 覆盖 |
|---|---|---:|---|
| RUNNING | `tests/stats.test.mjs` | 9 | 类型隔离、run_id 去重、无效行丢弃、加权配速、缺失心率 null、年份升序、闰年 / 周一偏移、scope 过滤、格式化 null |
| CYCLING | `tests/stats.test.mjs` | 8 | 类型隔离、去重 / 无效、爬升只计上报值、加权配速、缺失心率 null、3 km 视图门槛不在统计层、日历、格式化 |
| HIKING | `tests/stats.test.mjs` | 9 | 类型隔离 / 去重 / 无效、`climbOf` 合理性校验（海拔上限 2.5× / 距离上限 100 m·km⁻¹）、`aliveRuns`、四季映射、`climbM` 缺失为 null、海拔取最大、日历 |

加载方式：复用 `build-data-shards.mjs` 的 Vite SSR loader（`server.ssrLoadModule`），解析 `@/` 别名与 TS，与页面共用同一统计引擎，不另起口径；测试框架为 Node 内置 `node:test`，未引入新依赖。

接入：三站 `package.json` 新增 `test` 脚本，`ci` 脚本已加入 `pnpm run test`。本地实测 **26/26 通过**。

## 3. HEALTH

- Python 单测 **90 项**（`python3 -m unittest discover -s tests -q`），本轮新增 8 项统计严谨性测试。
- 同步工作流内运行单测 + 数据完整性检查；部署 job 运行 `scripts/smoke_dashboard.js`。
- 新增 `stats_rigor.py`：Spearman、双侧 p、BH-FDR、样本量门槛。
- 未覆盖：`analytics.py`、`cli.py`、`fetch.py`、`mcp.py`、大部分 `scripts/*.py`、前端 JS 数学（续做项）。

## 4. 持续缺口

- ~~三运动站没有统计逻辑单元测试~~ —— 2026-11-23 已补齐 26 项（见 2b）。剩余：`useActivities` 的 scope 切换、深链接等待等 React 层逻辑仍无单测。
- 跨运动隔离测试缺失。
- 深链接测试仅 smoke 覆盖部分场景。
- 浏览器巡检（JS 异常、404、主题、移动端溢出）目前仅部署路径有，尚未进入 active-watch 每日巡检。

## 5. 数据分片对账（本轮新增）

- `scripts/build-data-shards.mjs` 在构建期以现有统计模块为唯一引擎生成分片，并强校验：全量统计与「分片合并后统计」按 run_id 稳定排序后必须逐字节相同，否则构建失败。
- `scripts/verify-shards.mjs` 在 CI 与 coros_sync 发布链路检查 `dist/data/`：schema、站点、源文件 SHA-256、每个分片的条数与校验和、摘要与清单计数一致、`reconciled === true`。
- 本地实测：三站构建 + 对账 + 分片验证全部通过；CYCLING 双 scope 均通过。
