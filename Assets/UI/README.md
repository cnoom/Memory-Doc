# Assets/UI — 正式美术资产（实际应用区）

本目录存放**用户拍板确认后正式发布**的游戏美术资产，位于项目根目录 `Assets/UI/`（与将来 Unity 项目的资源路径一致），随仓库进 git，被 `docs/design/` 下的设计文档以相对路径嵌入（从任一设计文档引用均为 `../../Assets/UI/<类型>/<文件>.png`，如 `![记忆水晶](../../Assets/UI/relics/relic_memory_crystal.png)`）。

- 生成与发布流程见 [.agents/skills/mh-art/SKILL.md](../../.agents/skills/mh-art/SKILL.md)，候选/归档在仓库根 `ImageReview/`（同样进 git，便于远端查看）。
- 命名与规格遵循 [10-UI美术资源规格 §9](../../docs/design/10-UI美术资源规格.md)（全小写 snake_case + 类别前缀），完整名录见 [.agents/skills/mh-art/references/asset-specs.md](../../.agents/skills/mh-art/references/asset-specs.md)。
- 子目录：**按类型分目录**，目录名与 `ImageReview/<类型>/` 一致——`cards/` `cardbacks/` `cardframes/` `icons/` `relics/` `potions/` `map-nodes/` `enemies/` `portraits/` `backgrounds/` `textures/` `logos/` `mockups/` `buttons/` `panels/`；文件名前缀仍保留（双重可辨识）。
- **发布门槛**：任何资产（含 `ui_mockup.py` 合成的界面示意图）必须先落 `ImageReview/<类型>/` 待用户确认，用户拍板后才可 `--publish` 进本目录；校验/vision 通过不等于发布许可。
- 只放发布成品，不放候选与草稿；修改已发布资产 = 重新生成候选走 ImageReview 流程、再次经用户确认后覆盖发布，并在嵌入它的文档处检查引用是否仍成立。
