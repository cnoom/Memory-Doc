---
name: mh-art
description: 《记忆勇者》设计文档仓库专属 AI 生图——按 docs/design/10-UI美术资源规格.md 的命名与规格生成游戏美术资产（卡面插画、卡背、遗物/道具/状态/意图/功能图标、地图节点、敌人立绘、角色立绘、背景、纹理），经"预览→归档→实际应用"三目录流转并嵌入设计文档。凡在本仓库里提到"生成卡面/画卡背/生成图标/画遗物/画敌人/角色立绘/换背景/补美术资源"等与《记忆勇者》资产相关的生图请求都用本技能；与游戏资产无关的通用生图（海报、封面、任意插图）仍走用户级 germmc-image2。
---

# 《记忆勇者》文档仓库生图（mh-art）

生成通道复用用户级 germmc-image2 技能（`C:/Users/Administrator/.zcode/skills/germmc-image2/`）的脚本与 API Key（模型 gpt-image-2）。本技能只叠加项目层：**资产规格、命名、风格基线、三目录流转、文档嵌入**。不要在本技能内复制 API Key 或另写 HTTP 代码。

本仓库是纯设计文档仓库（无 Unity 工程），图片的"实际应用"= **被 docs/design/ 下的设计文档以相对路径引用**。

## 三目录模型（预览 → 归档 → 实际应用）

| 目录 | 角色 | 是否进 git |
| --- | --- | --- |
| `ImageReview/<类型>/` | **预览**：新生成的候选落这里，供人工/agent 校验，未定稿 | 是（便于远端查看拍板） |
| `ImageReview/_archived/<日期>/<类型>/` | **归档**：被新候选取代的旧图、落选方案，只进不出、永不发布 | 是 |
| `docs/design/assets/` | **实际应用**：校验通过后发布的正式资产，随文档进 git，被 md 嵌入。**扁平无子目录**——文件名自带类别前缀，不再按类型嵌套 | **是** |

## 工作流（三段式：生成 → 校验 → 发布嵌入）

1. 确定资产类型与规范文件名，查下方规格表和 [references/asset-specs.md](references/asset-specs.md)（含全部既有资产名录——遗物20/道具8/图标33/节点6/敌人9/立绘3/卡牌42 的文件名清单与卡背色板）。
2. 组装 prompt：风格基线 + 类型片段 + 具体内容描述（内容从对应设计文档 06/07/08 的词条与效果文本推衍，卡背要拼入类型色板 hex）。
3. 用 `scripts/gen_asset.py` 生成——**默认落 `ImageReview/<类型>/` 预览区**；要挑方案就 `--n 2` / `--n 3` 出多候选（`名称_1.png`…）。
4. **归档**：生成新一轮候选时，同任务被取代的旧图立即用 `--archive` 移入 `ImageReview/_archived/<日期>/<类型>/`——预览区各类型目录里只允许"当前待看"与"明确挂起"的候选（规则详见 `ImageReview/README.md`）。
5. 校验：agent 先用 Read 回看自检（风格一致性 / 透明底 / 水印 / 图标剪影可读性），再交用户在 `ImageReview/` 里拍板；不合格就调 prompt 重生成（旧图按上一步归档）。
6. 发布：`--publish ImageReview/<类型>/<文件>` 把通过校验的文件移动到 `docs/design/assets/`（扁平目录；自动剥离 `_N` 候选后缀、统一小写、校验类别前缀）。
7. **嵌入文档**（实际应用的最后一环）：在对应设计文档（06/07/08 等）的相关条目处插入相对路径引用，例如 `![记忆水晶](./assets/relic_memory_crystal.png)`；一张图只嵌一次，在首次定义它的文档里嵌。

## 资产规格表

命名规范遵循 [10-UI美术资源规格 §9](../../../docs/design/10-UI美术资源规格.md)：全小写 snake_case + 类别前缀（`card_` / `cardback_` / `icon_` / `relic_` / `potion_` / `node_` / `enemy_` / `portrait_` / `bg_` / `texture_`）。全部类型统一发布到 `docs/design/assets/`（扁平，靠前缀区分类别）。

| 类型 | API size | 透明底 | 发布规格 | 预览区目录 | 命名示例 |
| --- | --- | --- | --- | --- | --- |
| 卡面插画 card | 1024x1536 | 否 | 竖构图源图（保持生成比例，Unity 制作时再缩到 480×640） | `ImageReview/cards/` | `card_attack_biji.png` |
| 卡背 cardback | 1024x1536 | 否 | 整幅卡背设计 | `ImageReview/cardbacks/` | `cardback_attack.png` |
| 图标 icon（类型/词条/状态/意图/功能） | 1024x1024 | 是 | 256x256 RGBA（脚本自动缩） | `ImageReview/icons/` | `icon_status_burn.png` |
| 遗物图标 relic | 1024x1024 | 是 | 256x256 RGBA | `ImageReview/relics/` | `relic_memory_crystal.png` |
| 道具图标 potion | 1024x1024 | 是 | 256x256 RGBA | `ImageReview/potions/` | `potion_time.png` |
| 地图节点 node | 1024x1024 | 是 | 256x256 RGBA | `ImageReview/map-nodes/` | `node_battle.png` |
| 敌人立绘 enemy | 1024x1024 | 是 | 方构图全身源图 | `ImageReview/enemies/` | `enemy_goblin.png` |
| 角色立绘 portrait | 1024x1536 | 是 | 竖构图全身源图 | `ImageReview/portraits/` | `portrait_scholar.png` |
| 背景 background | 2048x1152 | 否 | 1920x1080 RGB（脚本自动缩） | `ImageReview/backgrounds/` | `bg_battle.png` |
| 纹理 texture | 1024x1024 | 否 | 256x256 可平铺 | `ImageReview/textures/` | `texture_parchment.png` |

> 尺寸说明：文档规格（图标 32–56px、卡牌 240×320 等）是 UI **显示尺寸**；本技能发布 4x 源图（图标 256、插画保持 API 原尺寸），显示缩放交给文档嵌入（`<img width>`）与未来 Unity 导入。

## 风格基线

源自 [09-UI设计规范 §1](../../../docs/design/09-UI设计规范.md)「记忆殿堂」视觉定位：暗色奇幻 + 学术羊皮纸 + 古金点缀。所有 prompt 以此为底，保证新旧资产同风格：

- **全局基线（EN，拼在最前）**：`dark fantasy storybook game art, ancient memory-palace library aesthetic, aged parchment and antique gold palette, warm candlelight atmosphere, painterly hand-drawn texture`
- **卡面**：`single focal subject, dynamic pose, rich atmospheric background, no text, no watermark`
- **卡背**：`full playing-card back design, ornate symmetrical border, radial gradient field, glowing central emblem, subtle arcane rune pattern, no text`（desc 里必须给类型色 hex，见 asset-specs 色板）
- **图标（icon/relic/potion/node）**：`flat dark-fantasy game icon, centered composition, bold readable silhouette, glowing accent color, plain transparent background, no text, no watermark`
- **立绘（enemy/portrait）**：`full body, centered, facing viewer, transparent background, no text, no watermark`
- **背景**：`wide scene illustration, soft depth, empty center area for UI, no characters, no text, no watermark`
- **纹理**：`seamless tileable texture, evenly lit, no vignette, no text`

中文 prompt 同样可用，但保持上述关键词的英文版拼入更稳。

## gen_asset.py

```bash
# 生成：默认落 ImageReview/<类型>/，--type 套用规格表预设（尺寸/风格/透明/缩放/命名）
python .agents/skills/mh-art/scripts/gen_asset.py --type relic --name relic_memory_crystal \
    --desc "a glowing crystal orb containing swirling memories, silver common-rarity trim"
# 多候选（挑方案用，产出 名称_1.png / 名称_2.png）
python .agents/skills/mh-art/scripts/gen_asset.py --type cardback --name cardback_attack --desc "..." --n 2
# 归档：被取代的旧候选移入 _archived/<今日>/<类型>/（可传单文件或整目录）
python .agents/skills/mh-art/scripts/gen_asset.py --archive ImageReview/cards/card_attack_biji.png
# 发布：校验通过后移动到 docs/design/assets/（扁平）；类型可从路径推断，_N 后缀自动剥离
python .agents/skills/mh-art/scripts/gen_asset.py --publish ImageReview/relics/relic_memory_crystal_1.png
```

- `--desc` 只写内容，风格基线自动拼接；`--no-style` 关闭。
- 发布时会校验文件名前缀与类别一致（`relic_` 开头落 `relics/`），不一致打 WARNING。
- 透明底机制（继承 tr2-art 实测结论）：网关 gpt-image-2 **不支持** `background: transparent` 请求参数（返回 400），脚本自动去参重试；但 prompt 文本里的 "transparent background" 关键词会让模型输出像素级真透明 PNG——类型片段已包含该词。脚本落盘后自动校验 alpha 通道，实心底打 WARNING，需人工抠图或重生成。
- 也可绕过包装器直接调 base 脚本：
  `python "C:/Users/Administrator/.zcode/skills/germmc-image2/scripts/generate_image.py" "<prompt>" --size 1024x1024 --output <路径>`

## 已知坑

- `gen_asset.py` 依赖 base 脚本绝对路径（默认 `C:/Users/Administrator/.zcode/skills/germmc-image2/`），换机器需设 `IMAGE2_SKILL_DIR` 环境变量。
- 生成尺寸档位：网关仅支持 1024x1024 / 1024x1536 / 1536x1024 / 2048x1152 等固定档位，项目规格靠脚本 PIL 后缩放。
- 上游生成慢（可达数分钟），base 脚本 600s 超时 + 3 次重试，502 等一会再试。
- 卡面是**插画**不是整卡：卡框/文字/词条区由 UI 层实现（见 10-UI美术资源规格 §2.2），AI 不画文字，desc 里明确 "no text"。
- 覆层（overlay_*）类资产是编辑器合成效果（虚线框/遮罩/锁链），不适合 AI 生成，不在本技能类型表内。

## 批量节奏

先出 2-3 个代表（`--n` 多候选或不同题材）落 `ImageReview/` 给用户确认风格，拍板后按 asset-specs.md 的名录批量跑、逐个或整目录 `--publish`；每张之间留意网关限流，失败重试即可（自带 3 次重试）。批量完成后汇报：生成数、预览区清单、已发布清单、待嵌入文档的条目。
