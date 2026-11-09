# Reward / Exchange UI V2 · 已确认参考及交付入口

> 2026-11-09 · 用户确认：奖励主入口统一、满库直达交换页、左新卡右 4×2 旧卡分页、雾蓝选中、返回/确认交换、与 Battle V05 同风格。  
> **视觉裁决已确认；Unity 正式美术资源制作和实机验收尚未完成。**

## 必读文件

1. [设计 17 · 奖励选牌与交换 UI V2](../../../docs/design/17-奖励选牌与交换UI-V2定稿.md)：规则和风格边界。
2. [设计 20 · 美术资源交付与 Unity 接入规范](../../../docs/design/20-奖励交换UI-V2美术资源交付与Unity接入规范.md)：资产、挂点、导入参数、冷加载、测试。
3. [asset-handoff.json](./asset-handoff.json)：机器可读资源/GUID/状态/坐标。
4. [layout-blueprint.svg](./layout-blueprint.svg)：逻辑尺寸蓝图。注意它是**结构草图而非已批准的最终贴图**。
5. 游戏仓 [reward-exchange-ui-v2-implementation-plan.md](https://github.com/cnoom/MemoryRouge/blob/main/docs/reward-exchange-ui-v2-implementation-plan.md)：Unity 施工入口。

## 已确认最终高保真参考

- 原图文件名：`典雅卡牌交换界面.png`；建议仓库存档名：`approved-exchange-full-1672x941.png`。
- 图片尺寸：1672×941，RGB PNG。
- 字节数：2947675。
- SHA-256：`4bb6f8eb029dc16f59cf09fc6363727e3e2c61f988139b7ff43a09a77a7745cf`。
- **当前 GitHub 状态：尚未写入原始二进制 PNG**。原图随此次对话的离线交付包提供；后续可使用本地克隆库正常添加、提交和推送，补到本目录。切勿改用此前已否决的概念图。
- 原图仅用于视觉对照；图中文字、卡牌示例和数字不能作为运行时内容，不得整图导入 Unity 当作背景 Sprite。

## 引擎实施重点

- 游戏仓原版 `LibraryChoiceOverlaySetup` 实际用 `PageSize=6` 且旧模板已存在时**直接跳过烘焙**。修改代码后必须就地迁移现有预制体（保留 .meta GUID）。
- 游戏仓 `LibraryChoiceOverlay` 旧逻辑是点行直接成交。新版须点卡仅选中，再点确认才交换。
- `RewardPanel.ConfirmSelection` 当前只要有 `Library` 就打开弹层；新版未满应直接入库，满/超容才打开。
- 原大纸面 A03 Border=32（四边）、`Image.Type=Sliced`；B03 按钮比例 640×112，无 9-slice，四态 SpriteSwap。
- 工程的卡面绑定靠 `CardViewBinder`、当前正式卡框与独立卡图；右侧按库内实例显示，含升级/共鸣状态，诅咒禁选。
- 奖励/商店/事件共享换卡弹层，完成之前须回归三宿主交易原子性。

## 正式资源可用性

已经可用：A03 骨白/墨黑面板、B03 四态按钮、正式卡框与卡图、CardCore、焦点覆层、现有装饰等。

尚未独立制作或审阅：扩展版多层纸板（若 A03 复用还原不合格）、无字分组签、旧卡选中角框、小型交换箭头/分页图标（在现有资源无法满足时制作）。

**开发模型不得因文档和 SVG 已在仓库就汇报“新美术贴图全部完成”。** 先用现有素材做功能与布局可玩版本，再按本会话已确认原图逐项对照，必要时制作增量透明 PNG，验证后方可接入正式美术资产库。
