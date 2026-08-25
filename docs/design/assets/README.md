# assets — 正式美术资产（实际应用区）

本目录存放**校验通过并正式发布**的游戏美术资产，随文档进 git，被 `docs/design/` 下的设计文档以相对路径嵌入（从任一设计文档引用均为 `./assets/<文件>.png`，如 `![记忆水晶](./assets/relic_memory_crystal.png)`）。

- 生成与发布流程见 [.agents/skills/mh-art/SKILL.md](../../.agents/skills/mh-art/SKILL.md)，候选/归档在仓库根 `ImageReview/`（同样进 git，便于远端查看）。
- 命名与规格遵循 [10-UI美术资源规格 §9](../10-UI美术资源规格.md)（全小写 snake_case + 类别前缀），完整名录见 [.agents/skills/mh-art/references/asset-specs.md](../../.agents/skills/mh-art/references/asset-specs.md)。
- 子目录：**无**——扁平目录，文件名前缀区分类别（`card_` / `cardback_` / `icon_` / `relic_` / `potion_` / `node_` / `enemy_` / `portrait_` / `bg_` / `texture_`）。
- 只放发布成品，不放候选与草稿；修改已发布资产 = 重新生成候选走 ImageReview 流程后再覆盖发布，并在嵌入它的文档处检查引用是否仍成立。
