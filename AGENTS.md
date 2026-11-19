# 《记忆勇者》策划文档仓库

本仓应只保存玩法、系统和内容策划文档，主要位于 `docs/design/`。Unity 工程位于 [MemoryRouge](https://github.com/cnoom/MemoryRouge)。

## 美术资源迁移与源仓清理（2026-11-18）

- **美术规范与制作说明正本**：[Memory-Art](https://github.com/cnoom/Memory-Art) 的 `docs/design/`。
- **美术工具正本**：Memory-Art 的 `tools/art/`。
- **正式图片、候选审稿、独立交付资源包**：已于 2026-11-18 完成迁移至 Memory-Art（`versions/v1/` 正式包 + `archive/unversioned/` 归档）；逐文件对账见 [migration-manifest.json](https://github.com/cnoom/Memory-Art/blob/main/docs/migration-manifest.json)。Memory-Art 是唯一美术资源正本。
- 后续 AI 生图、资产 ID、规格、命名和发布审核请先参考 Memory-Art 的 `docs/design/13-开发AI美术资源使用说明.md`（注意其页首「历史路径说明」）。**`developer-asset-registry.json` 是 2026-11-09 历史快照，不是当前正式资源清单正本**；当前正式美术资源清单以 Memory-Art `versions/v1/资源索引.json` 为准。journal_*_a01 已按 2026-11-01 用户裁定退役，不得重新作为生产资源投放。发布需要用户确认；不能把候选审稿图当作正式资产。
- **Phase 4 源仓清理**：本次独立清理变更删除 Memory-Doc 中已迁移的资源目录与美术专项文档副本，精确范围见 [Phase 4 清理记录](docs/art-source-cleanup-2026-11-18.md)。该变更合并后，Memory-Doc 不再保留这些副本；Git 历史保持不变。

**策划变更仍以本仓玩法文档为准；美术视觉决策以 Memory-Art 为准。** 不要仅凭历史记录覆盖用户最新裁决。


## 双仓库整理执行合同

策划仓与美术仓的最终边界、文件分类、混合文档拆分和清理顺序，统一遵循 [Memory-Art 仓库清理执行规范](https://github.com/cnoom/Memory-Art/blob/main/docs/repository-boundaries-and-cleanup.md)。本仓只保留玩法/系统/内容策划文档及其文本型附件。美术资源、候选审阅、艺术制作脚本和美术专项文档统一在 Memory-Art 维护；不得在本仓恢复或继续维护已迁移副本。