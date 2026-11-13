# ACTIVE WATCH

ACTIVE 四站（[RUNNING](https://zhubao315.github.io/running/) · [CYCLING](https://zhubao315.github.io/cycling/) · [HIKING](https://zhubao315.github.io/hiking/) · [HEALTH](https://zhubao315.github.io/health/)）的**运营中枢**。本仓库不发布页面，只承担三件事：

1. **每日巡检**（`scripts/patrol.mjs`）——只在真正需要处理时开 issue；
2. **共享 COROS 配额账本**（`state/fit-quota.json`）——三个运动站共用每天 50 个 FIT 下载额度；
3. **品牌单一事实源**（`brand/`）——四站共享品牌资产的唯一编辑处。

## 每日巡检

定时：每天 `05:40 UTC`（≈ 北京 13:40，晚于各站同步在 GitHub 调度漂移后的实际落地时间）。范围：

- 四站 HTTP 可用、标题为 `ACTIVE / …`、无旧母品牌名残留；
- `brand-tokens.css` 四仓 Git blob 同源 + 线上 `favicon-32.png` 四站字节一致；
- 数据新鲜度：各站默认分支最近提交（running/cycling/health ≤3 天，hiking ≤8 天，其为周更）＋ health `data_quality.json` 最新数据日期；
- 各站默认分支近 36 小时内的失败工作流。

异常时：创建/更新**唯一**一张 `watch:incident` issue；恢复后自动关闭。手动运行：Actions → Daily Patrol → Run workflow。

## COROS 配额账本（租约式）

COROS 账号每天限 50 次 FIT 下载，running / cycling / hiking 共享。三个运动站的 `scripts/quota_lease.py` 在同步前 **reserve**（默认想拿 10、硬上限 45，按账本剩余额度收敛），同步后 **reconcile** 回写实际用量——没用完的当天就还给另外两站。

- 格式：`{"days": {"YYYY-MM-DD": {"running": n, "cycling": n, "hiking": n}}}`，仅保留 3 天；
- 历史回填：手动触发运动站 COROS Sync，`reserve_budget` 输入调大预算；
- 失败策略：**fail-open**——账本不可达时回退保守值 10，同步永远不会因配额记账失败而中断；
- 写权限：运动站需要仓库 secret `ACTIVE_STATE_TOKEN`（对本仓 `state/` 有写权限的 PAT；轮换时同步更新三个运动站的 secret 即可）。

## 品牌单一事实源

`brand/` 是四站共享品牌资产的唯一编辑处：tokens（`brand-tokens.css`）、规范（`BRAND_SYSTEM.md`）、静态资产（`assets/`）、字体（`fonts/`）、共享组件（`sp-src/`）。

- `brand/sync.sh` 把共享文件复制到四个仓库并重写每仓的 `BRAND_MANIFEST.sha256`；
- 每仓的 **Brand Guard** 工作流校验文件与清单一致、且代码中无旧品牌名——有人手改共享资产即红；
- 跨仓一致性由每日巡检兜底（blob 同源 + 线上字节一致）。

使用：把四个站点仓库与本仓检出在同一工作区（目录名即站点名），编辑 `brand/` 后运行 `bash brand/sync.sh`（工作区位置不同时用 `ACTIVE_ROOT=…` 覆盖），再在各仓提交。

## 相关文档

系统审计 / 路线图 / 隐私审计 / 数据公开声明见各站仓库 `docs/`：`ACTIVE_SYSTEM_AUDIT.md`、`ACTIVE_ROADMAP.md`、`ACTIVE_PRIVACY_AUDIT.md`、`DATA_PUBLICATION.md`。
