# 《记忆勇者》策划文档仓库

本仓应只保存玩法、系统和内容策划文档，主要位于 `docs/design/`。Unity 工程位于 [MemoryRouge](https://github.com/cnoom/MemoryRouge)。

## 美术工作已拆分（迁移进行中）

- **美术规范与制作说明正本**：[Memory-Art](https://github.com/cnoom/Memory-Art) 的 `docs/design/`。
- **美术工具正本**：Memory-Art 的 `tools/art/`。
- **正式图片、候选审稿、独立交付资源包**：计划分别迁往 Memory-Art 的 `Assets/`、`ImageReview/`、`美术资源v1/`，**当前仍在本仓暂存，未完成二进制迁移**。不能据此将它们删掉，也不能把目标仓误判为资源齐备。
- 后续 AI 生图、资产 ID、规格、命名和发布审核请先参考 Memory-Art 的 `docs/design/13-开发AI美术资源使用说明.md` 及 `docs/design/art-inventory/developer-asset-registry.json`。发布需要用户确认；不能把候选审稿图当作正式资产。
- 待二进制资源验证、相对链接修复及 Unity 消费路径确认完成，再清理本仓资源与重复美术规范。迁移剩余任务见 [Memory-Art #1](https://github.com/cnoom/Memory-Art/issues/1)。

**策划变更仍以本仓玩法文档为准；美术视觉决策以 Memory-Art 为准。** 不要仅凭历史记录覆盖用户最新裁决。


## 双仓库整理执行合同

策划仓与美术仓的最终边界、文件分类、混合文档拆分和清理顺序，统一遵循 [Memory-Art 仓库清理执行规范](https://github.com/cnoom/Memory-Art/blob/main/docs/repository-boundaries-and-cleanup.md)。本仓只保留玩法/系统/内容策划文档及其文本型附件。**迁移、哈希校验、链接修复和目标仓验收全部通过前，不得删除 Assets、ImageReview、美术资源v1 或 tools/art。**