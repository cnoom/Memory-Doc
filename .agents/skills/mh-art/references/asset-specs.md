# 《记忆勇者》美术资产名录与规格

SKILL.md 规格表的展开版。名录与命名提取自 `docs/design/` 各设计文档（2026-08-25 核对），若设计文档变更需同步更新本文与 SKILL.md。

## 1. 资产类型 ↔ 设计文档对应

全部类型发布到项目根目录 `Assets/UI/<类型>/`（**按类型分子目录**，目录名与 ImageReview 预览区一致，文件名前缀仍保留；发布前须经用户拍板确认）。

| 类型 | 数量 | 内容来源 |
| --- | --- | --- |
| 卡面插画 card | 35 种（见 §2） | [06-学者角色卡牌设计](../../../docs/design/06-学者角色卡牌设计.md) |
| 卡背 cardback | 1（通用·静谧青纹章，v1.5） | [10-UI美术资源规格 §2.3](../../../docs/design/10-UI美术资源规格.md) |
| 图标 icon | 33（见 §4） | [10-UI美术资源规格 §3.1–3.4/3.7](../../../docs/design/10-UI美术资源规格.md) |
| 遗物图标 relic | 20 | [07-遗物与道具设计](../../../docs/design/07-遗物与道具设计.md) + 10§3.5 |
| 道具图标 potion | 8 | [07-遗物与道具设计](../../../docs/design/07-遗物与道具设计.md) + 10§3.6 |
| 地图节点 node | 6 | [10-UI美术资源规格 §3.8](../../../docs/design/10-UI美术资源规格.md) |
| 敌人立绘 enemy | 9 | [08-原型敌人设计](../../../docs/design/08-原型敌人设计.md) |
| 角色立绘 portrait | 3 | [05-Meta系统 §3](../../../docs/design/05-Meta系统.md) |
| 徽标 logo | 1（`logo_main`） | 见本文 §13（规格定稿后回填 10 §9） |
| 背景 background | 5（暂定） | [09-UI设计规范 §5 界面清单](../../../docs/design/09-UI设计规范.md) |
| 纹理 texture | 3 | [10-UI美术资源规格 §4.2](../../../docs/design/10-UI美术资源规格.md) |
| 按钮底图 button | 3（主/次/危险，见 §14） | [09-UI设计规范 §4.2](../../../docs/design/09-UI设计规范.md) |

## 2. 卡面插画名录（35 种）

命名规则（10§9.3）：`card_<类型英文>_<拼音>.png`，拼音无分隔无声调。同一张卡只生成一份插画（配对双方共用）。

> ⚠️ 与文档口径的差异：06 文档标注"10 初始 + 28 奖励 + 4 诅咒 = 42 张"是**按张数**计（初始牌组有 ×2/×3 重复）；按**卡种**是 35。奖励区实际条目 26 种（普通 11 + 罕见 9 + 稀有 6），与标注的 28 差 2——生成时以本文名录为准，后续若 06 文档补卡需回填。

### 初始牌组（5 种）

| 卡名 | 类型 | 文件名 |
| --- | --- | --- |
| 笔记 | 攻击 | `card_attack_biji.png` |
| 读书笔记 | 攻击 | `card_attack_dushubiji.png` |
| 速读 | 技能 | `card_skill_sudu.png` |
| 笔记本格挡 | 技能 | `card_skill_bijibengedang.png` |
| 全神贯注 | 能力 | `card_ability_quanshenguanzhu.png` |

### 奖励卡池（26 种）

| 卡名 | 稀有度·类型 | 文件名 |
| --- | --- | --- |
| 旁征博引 | 普通·攻击 | `card_attack_pangzhengboyin.png` |
| 引经据典 | 普通·攻击 | `card_attack_yinjingjudian.png` |
| 考据 | 普通·攻击 | `card_attack_kaoju.png` |
| 批注 | 普通·攻击 | `card_attack_pizhu.png` |
| 目录 | 普通·技能 | `card_skill_mulu.png` |
| 索引 | 普通·技能 | `card_skill_suoyin.png` |
| 摘要 | 普通·技能 | `card_skill_zhaiyao.png` |
| 速记 | 普通·技能 | `card_skill_suji.png` |
| 博闻强识 | 普通·能力 | `card_ability_bowenqiangshi.png` |
| 过目不忘 | 普通·能力 | `card_ability_guomubuwang.png` |
| 学术直觉 | 普通·能力 | `card_ability_xueshuzhijue.png` |
| 论文 | 罕见·攻击 | `card_attack_lunwen.png` |
| 精准打击 | 罕见·攻击 | `card_attack_jingzhundaji.png` |
| 交叉引用 | 罕见·攻击 | `card_attack_jiaochayinyong.png` |
| 破绽分析 | 罕见·攻击 | `card_attack_pozhanfenxi.png` |
| 图书馆 | 罕见·技能 | `card_skill_tushuguan.png` |
| 书签 | 罕见·技能 | `card_skill_shuqian.png` |
| 温习 | 罕见·技能 | `card_skill_wenxi.png` |
| 知识渊博 | 罕见·能力 | `card_ability_zhishiyuanbo.png` |
| 举一反三 | 罕见·能力 | `card_ability_juyifansan.png` |
| 百科全书 | 稀有·能力 | `card_ability_baikequanshu.png` |
| 万有文库 | 稀有·技能 | `card_skill_wanyouwenku.png` |
| 真理之眼 | 稀有·攻击 | `card_attack_zhenlizhiyan.png` |
| 时空回溯 | 稀有·技能 | `card_skill_shikonghuisu.png` |
| 全知全能 | 稀有·能力 | `card_ability_quanzhiquanneng.png` |
| 融会贯通 | 稀有·技能 | `card_skill_ronghuiguantong.png` |

### 诅咒牌（4 种）

| 卡名 | 文件名 |
| --- | --- |
| 遗忘 | `card_curse_yiwang.png` |
| 混乱笔记 | `card_curse_hunluanbiji.png` |
| 拖沓 | `card_curse_tuota.png` |
| 误解 | `card_curse_wujie.png` |

## 3. 卡背（1 种：通用卡背）

2026-08-29 定稿（10 §2.3 v1.5）：全类型共用**通用卡背·静谧青纹章版**——静谧青"学者书斋"底、金色细线框+四角金点、中央金环徽记（金色发光记忆宝珠悬浮于奶油色摊开的书本上方）、星点点缀、背景殿堂尖拱暗纹；背面不泄露类型（玩法影响见 02 §2）。已生成并发布 `cardback_universal.png`。v1.4 深可可旧书封版归档 `ImageReview/_archived/2026-08-29/cardbacks/`。

prompt 基调（再生时用）：

```
clean simple 2D cartoon game art for casual mobile games, ... vertical card back design
filling the whole canvas, perfectly symmetrical: muted medium-depth teal field like a calm
scholar study at dusk, centered cute golden emblem of one glowing memory orb floating above
a small open cream book, enclosed in a thin gold circular ring, elegant thin gold line
border with tiny gold dots at the four corners, a few tiny gold stars, soft warm glow,
very minimal, no text, no watermark
```

卡框（`border_card_*`，10 §2.2/§4.3 v1.5）：记忆殿堂拱窗版——暗类型色边带（attack 暗红 / skill 暗藏青 / ability 暗紫 / curse 炭黑）+ 金拱饰石柱 + 拱形插画窗（attack/skill/ability 窗内薄荷净底、curse 淡紫灰）+ 下部奶油效果区；发布为分层合成定稿（`roundify_card.py --compose-type`）：程序描边环（26px 等粗、类型色板锚定）+ 内容层 + 拱形插画窗镂空（alpha=0，插画引擎动态垫层）。prompt 片段见 SKILL.md 风格基线。

## 4. 图标名录（33 个，含状态/意图/词条/类型/功能）

状态/意图/类型/词条图标的色彩语言见 [10-UI美术资源规格 §1.4/§1.5](../../../docs/design/10-UI美术资源规格.md)，desc 中拼入对应 hex。

### 状态效果（5）

`icon_status_burn`(灼烧`#E84A20`) / `icon_status_freeze`(冰冻`#3AC4E8`) / `icon_status_armor`(护甲`#A8A8B8`) / `icon_status_vulnerable`(易伤`#B83A8B`) / `icon_status_weak`(虚弱`#8B9B3A`)

### 意图（5）

`icon_intent_attack`(攻击`#C73E3E`) / `icon_intent_charge`(蓄力`#E87B35`) / `icon_intent_defend`(防御`#4A7AD4`) / `icon_intent_special`(特殊`#9B45D4`) / `icon_intent_berserk`(狂暴`#A82020`)

### 卡牌类型（4）

`icon_type_attack`(攻击,红) / `icon_type_skill`(技能,蓝) / `icon_type_ability`(能力,紫) / `icon_type_curse`(诅咒,灰)

### 词条（8）

`icon_tag_flip`(翻开`#D4A857`) / `icon_tag_exhaust_trigger`(消除`#D4A857`) / `icon_tag_enter`(入场`#D4A857`) / `icon_tag_consume`(消耗`#E84A20`) / `icon_tag_remove`(移除`#888888`) / `icon_tag_resonance`(共鸣`#5BA85B`) / `icon_tag_note`(笔记`#5BA85B`) / `icon_tag_sword_shield`(剑盾`#5BA85B`)

### UI 功能（11）

`icon_menu` / `icon_settings` / `icon_back` / `icon_gold` / `icon_deck` / `icon_discard` / `icon_exhaust` / `icon_reshuffle` / `icon_hp` / `icon_block` / `icon_focus`(专注`#D4A857`)

> 2026-09-01：功能图标 ×12（§3.6 全部，含 `icon_memory`）已生成发布；`icon_intent_attack`、`icon_status_burn` 为意图/状态两组的首批样张（同风格，其余待批量）。图标风格关键词：居中单一物体、粗圆润剪影、深色细描边、平色软高光；易加戏的题材（火焰/骷髅等）desc 需显式否定（no lantern/no face/no books…）。

## 5. 遗物名录（20 个）

来自 [10-UI美术资源规格 §3.5](../../../docs/design/10-UI美术资源规格.md)。边框色随稀有度：普通银 `#B0B0B0` / 罕见蓝 `#4A9CD4` / 稀有金 `#D4A857` / Boss 橙 `#E87B35`。

| 稀有度 | 文件名（图标意象） |
| --- | --- |
| 普通 | `relic_memory_crystal`(水晶球) / `relic_notebook`(笔记本) / `relic_resonance_stone`(音波石) / `relic_twin_dice`(骰子) / `relic_first_aid`(医药包) / `relic_wood_shield`(木盾) / `relic_slow_seal`(减速符文) |
| 罕见 | `relic_mind_map`(脑/网状图) / `relic_eternal_candle`(蜡烛) / `relic_chain_core`(链条核心) / `relic_charge_crystal`(闪电水晶) / `relic_vampire_fang`(獠牙) / `relic_energy_shield`(能量盾) |
| 稀有 | `relic_stable_anchor`(锚) / `relic_twin_charm`(双生符) / `relic_mirror_echo`(镜子) / `relic_scholar_badge`(徽章) |
| Boss | `relic_omniscient_eye`(眼睛) / `relic_chaos_core`(漩涡) / `relic_memory_crown`(王冠) |

## 6. 道具名录（8 个）

`potion_time`(时间,沙漏,金) / `potion_insight`(透视,眼球,青) / `potion_rearrange`(重排,棋盘网格,紫) / `potion_divination`(占卜,水晶球,蓝) / `potion_block`(格挡,盾牌,银) / `potion_power`(力量,拳头,红) / `potion_purify`(净化,圣光十字,白) / `potion_recall`(回忆,书签,金)

## 7. 地图节点名录（6 个，2026-09-01 全部发布）

A 方向"圆形金环徽章"家族（彩色圆底+哑金环+奶油符号浮雕+深可可细描边，256×256 透明底；类型区分=底色+符号，形状编码作废）：

`node_battle`(战斗,红底,交叉双剑) / `node_elite`(精英,紫底,切面宝石) / `node_shop`(商店,金底,双硬币) / `node_campfire`(篝火,橙底,火焰+木柴) / `node_event`(事件,蓝底,粗问号) / `node_boss`(Boss,红橙底,王冠+双层金环)

> 家族尺寸基线：内容宽约 207px/不透明占比约 0.51（battle 实测）；同族候选占比跑偏时优先按基准程序规范化归一，不靠重掷生成。

## 8. 敌人立绘名录（9 个）

来自 [08-原型敌人设计](../../../docs/design/08-原型敌人设计.md)。

| 敌人 | 定位 | 文件名 |
| --- | --- | --- |
| 训练假人 | 教学敌人 | `enemy_training_dummy.png` |
| 哥林布 | 基础攻击型 | `enemy_goblin.png` |
| 混乱史莱姆 | 位置干扰型 | `enemy_chaos_slime.png` |
| 蛮族战士 | 节奏施压型 | `enemy_barbarian.png` |
| 腐化花蕾 | 桌面污染型 | `enemy_corrupted_bud.png` |
| 幻影 | 可用性干扰型 | `enemy_phantom.png` |
| 双刃执行者 | 精英·连击高压 | `enemy_twinblade_executor.png` |
| 记忆窃贼 | 精英·复合干扰 | `enemy_memory_thief.png` |
| 记忆吞噬者 | 第一章 Boss | `enemy_memory_devourer.png` |

## 9. 角色立绘名录（3 个）

`portrait_scholar`(学者,情报型,袍服+眼镜+书卷) / `portrait_berserker`(狂战士,暴力输出,待设计——生成前与用户确认形象) / `portrait_warlock`(术士,高风险解锁角色,待设计——同上)

## 10. 背景名录（5 个，2026-09-01 全部发布）

`bg_menu`(主菜单,图书馆大厅) / `bg_battle`(战斗,殿堂石厅烛光) / `bg_event`(事件,神秘壁龛) / `bg_shop`(商店,书房小店) / `bg_campfire`(篝火,休息壁龛)

> 每张 2 候选、vision 判读"中央 UI 留空区干净（stddev 采样）"者定稿；落选件在 `_archived/2026-09-01/backgrounds/`。命名与场景对应已随发布定稿（10 §9.2 `bg_` 前缀）。

## 11. 纹理名录（3 个）

`texture_parchment`(羊皮纸,可平铺) / `texture_dark`(暗色,可平铺) / `texture_noise`(噪声遮罩——文档规格 512×512,如需精确对齐用 `--no-resize` 后手动缩放)

## 12. 尺寸与透明底备忘

- 发布规格：图标/遗物/道具/节点/纹理 256×256；背景 1920×1080；卡面插画/立绘保留 API 原尺寸；**卡背与四类型卡框发布为 3:4 圆角定稿版**（1024×1365 居中裁切 + 60px 圆角透明角，`roundify_card.py` 后处理，2026-08-29）。
- 文档里的 32–56px 图标尺寸是 UI 显示尺寸，非源图尺寸（详见 SKILL.md 规格表附注）。
- 透明底：仅 icon/relic/potion/node/enemy/portrait/logo；网关不支持 `background: transparent` 参数但响应 prompt 关键词，脚本自动校验 alpha 并对实心底打 WARNING。卡背/卡框的圆角透明角由 roundify 后处理产生，不依赖网关。

## 13. 徽标（1 个，2026-09-01 定稿）

`logo_main`（游戏徽记，已发布 `Assets/UI/logos/logo_main.png`）——**宝珠主体版**：大颗薄荷青发光记忆宝珠（内含书本剪影+星点）坐在摊开奶油书本上、顶悬小金冠（三方向候选中 vision 七项全过者：描边干净、4 元素、严格对称、透明底无残迹；圆环/盾形两方向落选件在 `_archived/2026-09-01/logos/`）。透明底方构图源图 1254×1254。**《记忆勇者》中文标题字标由 UI 层（TMP 思源宋体）排版合成，不烘焙进徽记资产**（AI 不画文字原则）；徽记+雅黑近似字标的主菜单效果见 `mockup_s01_menu.png`。

## 14. 按钮底图（3 个，2026-09-01 定稿）

`btn_primary`(主按钮,蜂蜜金) / `btn_secondary`(次按钮,亮纸奶油) / `btn_danger`(危险按钮,收敛暗红)

> "糖果光泽"方向（用户三选一拍板，金徽浮雕/描金木牌两落选方向在 `_archived/2026-09-01/buttons/`）。三变体同构：胶囊圆角+上缘白高光带+底缘深唇边+深可可描边+双线金内框+四角金珠+左右星光，**中央留净供叠字**（九宫格关键约束）。发布规格统一 960×208、切片边 52（10 §8.3）；叠字色：主/次=深可可 #3B3226、危=白（09 §4.2）。风格锚点提取自 logo/卡背/卡框家族采样（蜂蜜金 #FDCE6A~#ECC67B）。`ui_mockup.py` 的 `button()` 辅助函数消费（缺失自动回退纯色 panel）；2026-09-01 起 S01 已接入。

## 15. 界面示意图（程序合成，非 AI 生图）

`ui_mockup.py`（mh-art scripts）按 09 布局/色板把已发布资产合成 1920×1080 示意图，落 `ImageReview/mockups/` 校验后 `--publish` 发布（`mockup_` 前缀）。**2026-09-01 S01~S13 共 13 屏全量发布**（09 §5.1/§5.4/§6/§7.1~§7.4/§8.1~§8.3 嵌入）。字体为系统雅黑近似（正式实现 Noto Serif/Sans SC + TMP）；正面小卡文字按整卡缩放仅示意；商店/Boss遗物屏的遗物徽记为程序简笔占位（`relic_glyph`），真遗物图标发布后重渲替换。
