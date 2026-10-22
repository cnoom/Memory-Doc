# 美术资源 v1

整理日期：2026-10-21。包含当前正式收录的 238 项独立资源，共 383 个资源文件（包含PNG、SVG及辅助遮罩）。原始正式目录 Assets/UI 保留，此目录为可独立拷贝的分类交付副本。

包含61种卡牌插画、10种卡框、统一卡背，以及已确认的角色／敌人、图标、背景与UI组件。未收录待审候选、已替代版本和卡牌装框预览。

先查看 [资源索引](资源索引.json) 获取尺寸、类型、窗口、文字安全区和配套遮罩。索引中的文件路径相对此目录。逐文件来源与SHA256见 [校验清单](文件校验清单.json)，中文卡名检索见 [卡牌目录](卡牌目录.md)。

接入前必读 [客户端接入与视觉一致性验收](integration-v1/README.md)，逐页保存同状态截图与叠加对照。

先读 [17类UI视觉定稿清单](integration-v1/ui-finalization.md)。设计参考目录中的正式稿可按稿接入，不因productionEligible=false视为待审。

## 使用约定

- 卡牌插画为不透明骨白底，按对应卡框窗口等比容纳并应用该框自己的遮罩；不要混用遮罩。
- 卡名、效果与数值需单独渲染。所有隐藏卡使用统一卡背。
- backgrounds 包含一张旧的含角色组合背景（索引角色 composite-background-with-actors），仅供参考；分层场景使用 empty-battle-background，避免重复叠加人物。
- PNG与SVG可能是同一资源的两种格式，不是两个独立资源；导入时选择适合引擎的格式。
- 此包完成资源整理，不代表引擎接入、动画或运行时控件已实现。
- 详细接入说明位于原项目 docs/design/13-开发AI美术资源使用说明.md；原索引和设计文档路径保持不变。

## 分类文件数

| 目录 | 文件数 |
|---|---:|
| backgrounds | 7 |
| badges | 2 |
| bars | 10 |
| boss-phase2-s01 | 1 |
| boss-phase3-s02 | 1 |
| buttons | 32 |
| campfire-l01 | 1 |
| cardbacks | 1 |
| cardframes | 20 |
| cards | 61 |
| controls | 14 |
| effects | 4 |
| enemies | 11 |
| entry-h03 | 2 |
| fonts | 6 |
| icons | 78 |
| icons-q02 | 1 |
| illustrations | 10 |
| integration-v1 | 5 |
| journal | 34 |
| map | 26 |
| map-i04 | 1 |
| mockups | 1 |
| ornaments | 2 |
| overlays | 10 |
| panels | 19 |
| portraits | 1 |
| relics | 19 |
| settings-j03 | 2 |
| shop-k03 | 1 |
