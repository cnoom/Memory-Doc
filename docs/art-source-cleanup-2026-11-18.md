# Memory-Doc Phase 4 美术源仓清理记录

> 状态：本文件随独立 Phase 4 清理 PR 提交。PR 合并后，本记录成为 Memory-Doc 的清理审计入口。

## 执行基线

- Memory-Doc 源仓：`cnoom/Memory-Doc`，分支 `master`，基线提交 `19c73814df74208c8190d0d40cd1508e3e52aac9`。
- 基线 Git tree：`e3242c7f197275cb56cc9458243aae2baf426b13`。
- Memory-Art 目标仓：`cnoom/Memory-Art`，本次复核时 `main` 为 `4113c96c5e0ec05e0bc7f62bae8e797989305529`；`versions/index.json.latestReady=true`。
- 双仓迁移 PR：Memory-Art#2（`ecdf37d`）与 Memory-Doc#6（`19c7381`）均已合并；合并后双仓树复核一致，27/27 条跨仓 URL 有效。

## 删除范围

本次只从 Memory-Doc 当前工作树移除已迁移的美术资源副本及美术专项文档，不删除玩法/交互正本。

| 路径 | 基线文件数 | 处理 |
|---|---:|---|
| `Assets/` | 505 | 删除；资源正本位于 Memory-Art |
| `ImageReview/` | 1,190 | 删除；审阅历史归档位于 Memory-Art `archive/unversioned/ImageReview/` |
| `美术资源v1/` | 468 | 删除；正式版本位于 Memory-Art `versions/v1/` |
| `tools/art/` | 87 | 删除；工具正本位于 Memory-Art `tools/art/` |
| `docs/design/10-UI美术资源规格.md` | 1 | 删除迁移副本 |
| `docs/design/11-美术设计方案.md` | 1 | 删除迁移副本 |
| `docs/design/12-美术资源总清单与制作计划.md` | 1 | 删除迁移副本 |
| `docs/design/13-开发AI美术资源使用说明.md` | 1 | 删除迁移副本 |
| `docs/design/18-奖励交换UI-V2美术资源交付与Unity接入规范.md` | 1 | 删除迁移副本 |
| `docs/design/art-inventory/` | 5 | 删除迁移台账副本 |
| **合计** | **2,260** | **仅删除当前工作树路径** |

## 迁移对账依据

Memory-Art `docs/migration-manifest.json` 共 2,250 条记录：

- byte-exact：1,786
- alias-mapped-no-copy：461
- adapted-with-target-hash：2
- content-merge：1
- 合计：2,250

v1 原交付清单 368 个文件的复验口径为 351 个逐字节一致、17 个仅换行差异（EOL-only）；资源索引记录 231 项。以上是迁移复验口径，不将别名映射误算为复制文件。

## 保留范围与引用修复

- 保留所有玩法、战斗、卡牌、状态、敌人、遗物和关卡策划文档。
- 保留 `docs/design/09-UI交互与流程规范.md`（交互行为正本）、`docs/design/09-UI设计规范.md`（兼容入口）及 `docs/design/17-奖励选牌与交换UI-V2定稿.md`（交互正本）。
- 保留 `docs/design/18-顺序入场预览与敌人被动位置干扰V3.md`；它是玩法文档，与被删除的 18 号美术交付文档不是同一文件。
- 更新 `docs/design/00-项目总览.md`，将 12/13 美术入口改为 Memory-Art 跨仓链接，并链接正式 v1 资源索引。
- 更新 `AGENTS.md` 与 `docs/repository-boundaries.md`，记录双仓验收完成和 Phase 4 清理边界。
- 不修改 MemoryRouge，不修改美术资产内容，不清理 Git 历史，不 force-push。

## 合并后验收要求

1. 对 PR changed-files 清单核对：删除范围必须严格等于上述 2,260 个路径，另加本记录及 3 个文档更新。
2. 检查 Memory-Doc 默认分支仅保留策划文档、仓库说明及文本型策划附件。
3. 对所有剩余活跃文档复扫旧仓美术相对路径；跨仓链接应指向 Memory-Art 正本。
4. 确认 Memory-Art `versions/index.json.latestReady=true`，并复核资源索引与迁移 manifest 可访问。
5. 确认 MemoryRouge 工作区和仓库未发生任何改动。
6. PR 合并后再关闭 Memory-Art Issue #1；不得在 PR 合并前关闭。

