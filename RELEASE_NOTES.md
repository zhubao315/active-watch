# ACTIVE 2.0.0 — Release Notes

**Tag:** `v2.0.0` · **Date:** 2026-11-18

ACTIVE — Personal Health & Active Life Intelligence Platform. 四个运动健康站点 + 一个运营中枢，统一品牌 / 数据契约 / 巡检体系。

## Highlights

- **品牌 3.0 / Navigation Icons 1.0**：渐变 A 形 PRECISION MOTION 母品牌真矢量；四枚 Neo Sport Glyph 几何导航图标；统一品牌源文件与四站同步。
- **Personal Profile 2.0**：三站个人档案紧凑化，首屏 KPI 更早可见（桌面档案 178px→107px，手机 443px→130px）。
- **数据可信**：共享 COROS 配额账本、数据水位、构建期分片 + 逐字段对账；四站巡检可识别 API 失败并自动关单。
- **去 AI 味**：Impeccable 复审把四站检测器 findings 从 479/489/432/595 降到 6/6/7/19。
- **前端工程质量**：frontend-ui-engineering 复审修复语义按钮与移动端触控目标；PR 门禁含 typecheck/build/verify/浏览器 smoke。

## Repos in this release

| Repo | Tag | Role |
|---|---|---|
| active-watch | v2.0.0 | 品牌单一事实源 / 巡检 / 配额 / 数据水位 |
| health | v2.0.0 | 健康驾驶舱（相关性严谨性、指标语义色） |
| running | v2.0.0 | 跑步档案（Profile 2.0、配速口径） |
| cycling | v2.0.0 | 骑行档案（双口径、范围切换整合） |
| hiking | v2.0.0 | 山野探索（活跃日/连续记录、3D 地形） |

## Data & privacy

未修改任何原始数据；缺失仍显示「—」不补零；四站统计口径与深链、地图、3D、筛选、COROS 同步保持不变。

See each repo's `CHANGELOG.md` for per-repo detail.
