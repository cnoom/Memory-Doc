# ImageReview — AI 生图预览/归档区

mh-art 技能（`.agents/skills/mh-art/`）生成的图片**先落在本目录**（含 `_archived/` 归档区，整体随仓库进 git——便于在远端直接查看候选与旧方案），供人工校验风格/构图/透明底。校验通过的发布到项目根目录 `Assets/UI/`（实际应用区）。

## 目录角色

| 路径 | 角色 | 规则 |
| --- | --- | --- |
| `<类型>/`（cards/ cardbacks/ icons/ relics/ potions/ map-nodes/ enemies/ portraits/ backgrounds/ textures/ logos/） | **预览**：当前待看的候选 | 只允许存在"当前待审批"与"明确挂起"的活候选 |
| `_archived/<日期>/<类型>/` | **归档**：被取代/落选的历史方案 | 只进不出，永不发布；回看旧方案按日期目录翻 |
| `Assets/UI/`（项目根目录，不在本目录下） | **实际应用**：正式资产 | 进 git，**扁平无子目录**（文件名前缀区分类别），被设计文档以相对路径嵌入 |

## 工作流

1. 生成（默认落本目录对应类型子目录；`--n 2/3` 出多候选 `名称_1.png / 名称_2.png`）：
   `python .agents/skills/mh-art/scripts/gen_asset.py --type relic --name relic_memory_crystal --desc "..."`
2. 校验：资源管理器直接看图，或让 agent 用 Read 回看并按风格基线自检。
3. 出**新一轮**候选前，把同任务被取代的旧图归档：
   `python .agents/skills/mh-art/scripts/gen_asset.py --archive ImageReview/relics/旧图.png`
4. 拍板后发布（移动到实际应用区并按规范重命名，自动去掉 `_N` 候选后缀）：
   `python .agents/skills/mh-art/scripts/gen_asset.py --publish ImageReview/relics/relic_memory_crystal_1.png`
5. 发布后在对应设计文档嵌入相对引用（这是文档仓库里图片的"实际应用"）。

## 归档规则（保持预览区只放"当前待看"批次）

- 生成新一轮候选时，**同任务被取代的旧图立即移入 `_archived/<日期>/<类型>/`**（按归档当日日期建目录，保留原子目录结构）。
- 落选但不被取代的候选（如多候选中被否掉的兄弟方案）随当轮任务拍板后一并归档。
- `_archived/` 只进不出，永不发布。

## 校验要点

- 风格是否与基线一致（暗色奇幻故事书、羊皮纸古金、烛光氛围——见 SKILL.md 风格基线）
- 透明类资产背景是否真透明（实心底会有 WARNING 日志）
- 图标剪影在 256×256 下是否可读
- 是否有水印/乱入文字（卡面插画严禁出现文字）
- 卡背颜色是否与色板严格一致（#D44545/#4577D4/#9B45D4/#3A2A3A）
