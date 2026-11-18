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

**当前版本：3.0 — PRECISION MOTION（PNG 切图版）。** 母品牌为渐变「A」形徽记，字标 Manrope ExtraBold 800 / 字距 2.2px。一套母品牌 + 四个子品牌（HEALTH 蓝 / RUNNING 青柠 / CYCLING 琥珀 / HIKING 翡翠）+ 一个 ACTIVE WATCH 运营中枢；正式色板与指标语义色不变，禁止 `ZB ACTIVE`。

**Logo / icon 是真 SVG 矢量**：从 `brand/assets/ACTIVE_Brand_Identity_Board.png` 识别轮廓后用 Bézier 路径 + 原生渐变重建，见 `brand/ACTIVE-BRAND-VECTOR/`（含 `master/`、`sub-brands/`、`watch/`、`favicon/`、`png/`、`validation/` 与 `BRAND_VECTOR_GUIDE.md`）。矢量在黑/白/深蓝/透明下边缘干净、可无限缩放。`brand/sync.sh` 把 `assets/` 中的规范 SVG 同步到四站，站点组件引用 `active-mark.svg` 与 `icons/*.svg`。概念展示板在 `brand/boards/`（仅参考）。

- `brand/sync.sh` 把共享文件复制到四个仓库并重写每仓的 `BRAND_MANIFEST.sha256`；
- 每仓的 **Brand Guard** 工作流校验文件与清单一致、且代码中无旧品牌名——有人手改共享资产即红；
- 跨仓一致性由每日巡检兜底（blob 同源 + 线上字节一致）。

使用：把四个站点仓库与本仓检出在同一工作区（目录名即站点名），编辑 `brand/` 后运行 `bash brand/sync.sh`（工作区位置不同时用 `ACTIVE_ROOT=…` 覆盖），再在各仓提交。

## 数据水位（2026-11-18 新增）

三个运动站在每次 COROS 同步成功后，由 `scripts/write-data-watermark.mjs` 生成 `public/data-watermark.json`：

```json
{
  "schema_version": 1,
  "site": "running",
  "generated_at": "2026-11-18T00:00:00Z",
  "latest_activity_date": "2026-11-17",
  "activity_count": 2039,
  "source_updated_at": "2026-11-18T00:00:00Z",
  "data_checksum": "sha256:...",
  "build_version": "a6d19ad",
  "status": "ok"
}
```

巡检不再用 git 提交时间推断数据新鲜度，而是检查真实数据日期、最近成功同步时间、记录数跌幅与数据质量。同步时间与活动日期采用两套独立阈值（`state/data-baselines.json`）——徒步活动有季节性，几周没有新记录不等于系统故障。

## 测试与工具

本仓首次引入 `package.json` / `pnpm-lock.yaml`，Node ≥ 20.19：

```bash
pnpm install --frozen-lockfile
pnpm test          # 21 项 Node + Python 测试
pnpm run patrol    # 手动巡检（需 GITHUB_TOKEN）
pnpm run verify:live   # 线上品牌与运行时验收（需 playwright 浏览器）
```

- `brand/brand-contract.mjs`：品牌契约的唯一定义；`ACTIVE` 是当前唯一正确字标，`ZB ACTIVE` 必须不存在（注意它包含 `ACTIVE` 子串，校验前先剥离）。
- `tests/`：品牌契约、数据水位、配额账本（并发/SHA 冲突/网络失败/无 token）自动化测试。
- `brand/build-assets.mjs`：已去除硬编码 `/oc/...` 路径，改为脚本相对定位 + `ACTIVE_BRAND_DIR` / `ACTIVE_ART_DIR` / `ACTIVE_ASSET_OUT` 环境变量。

- `tools/build-data-shards.mjs` / `tools/verify-shards.mjs`：构建期数据分片与 dist 校验的规范副本，三运动仓 `scripts/` 下各有一份。生成器通过 Vite SSR 加载现有 `*Stats.ts`，不重写统计；全量与分片统计必须逐字段对账，否则构建失败。

`tools/quota_lease.py`、`tools/write-data-watermark.mjs`、`tools/build-data-shards.mjs`、`tools/verify-shards.mjs` 是三运动仓对应脚本的规范副本，修改后需同步。

## 相关文档

复审后的系统级文档在本仓 `docs/`：`ACTIVE_SYSTEM_AUDIT.md`、`ACTIVE_ARCHITECTURE.md`、`ACTIVE_DATA_DICTIONARY.md`、`ACTIVE_PERFORMANCE_BASELINE.md`、`ACTIVE_TEST_COVERAGE.md`、`ACTIVE_PRIVACY_REVIEW.md`、`ACTIVE_UPGRADE_ROADMAP.md`。各站仓库 `docs/` 保留原有的单站审计、路线图、隐私审计与数据公开声明。
