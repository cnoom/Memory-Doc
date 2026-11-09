# 20 · 奖励/交换 UI V2：美术资源交付与 Unity 接入规范

> 日期：2026-11-09  
> **状态：交付规格已冻结；正式独立新素材尚未生产/导入；Unity 实机尚未验收。**  
> 视觉裁决：[17·奖励选牌与交换 UI V2](./17-奖励选牌与交换UI-V2定稿.md)；玩法裁决：[14·牌库交换与软扩容 V2](./14-牌库交换与软扩容机制V2.md)；现有风格：11 §13 B03 / §14 V05。  
> **本文件解决“由其他开发模型实施时具体取哪张图、挂到哪个节点、导入如何设置、缺哪种资源、怎么验收”，不重开美术方向讨论。**

## 0. 一次性交付文件及优先级

| 文件 | 仓库位置 | 作用 |
|---|---|---|
| 已确认的交换界面原图 | 本会话交付包 `approved-exchange-full-1672x941.png`（原名“典雅卡牌交换界面.png”） | **唯一高保真视觉锚点；非运行时 Sprite** |
| 本文 | `docs/design/20-奖励交换UI-V2美术资源交付与Unity接入规范.md` | 资源制作/接入规格 |
| 机读资源表 | `Assets/UI/mockups/reward-exchange-v2/asset-handoff.json` | 资源、GUID、状态、坐标与预制体依赖 |
| 布局蓝图 | `Assets/UI/mockups/reward-exchange-v2/layout-blueprint.svg` | 1920×1080 节点示意，**仅几何线框，不替代原图** |
| 本批入口 | `Assets/UI/mockups/reward-exchange-v2/README.md` | 资源包摘要、交接核验 |
| 实现施工单 | 游戏仓 `docs/reward-exchange-ui-v2-implementation-plan.md` | 修改点与测试交付 |

**重要现状声明：** 原始 PNG 已从本会话挂载文件校验：**1672×941、2,947,675 字节、SHA-256 `4bb6f8eb029dc16f59cf09fc6363727e3e2c61f988139b7ff43a09a77a7745cf`**。仓库当前通过连接器可以写 UTF-8 文档、JSON、SVG，但尚未把该原始二进制 PNG 写入 GitHub。随本会话提供包含原图的 ZIP（供其他模型直接读取）；任何人**不得声称 SVG 等于已确认原图**。若执行模型只读取 GitHub，需要额外取得该原图，或者将成果标记“结构验收通过、视觉还原待最终对照”。

## 1. 不可偏离的界面结果

- 卡牌奖励 S05：三选一，一次选中一张，底部**只有“跳过”和“确认选择”两种操作**。牌库计数是信息，不是第三个操作。
- 牌库未满（例如 11/12）：点“确认选择”直接加入并结算；**没有第二层**。
- 牌库满或超容（例如 12/12、13/12）：点“确认选择”**直接打开交换弹层**；不能出现“是否交换”的询问弹窗，也不能直接加入。
- 交换弹层：左一张获得牌的大图，右 4 列 × 2 行显示旧库实例（每页 8 张，分页）；旧牌点击**仅改变选中态**；确认后才提交；返回奖励页保持新卡选中。
- 可以同名多份，每份按 `Library[index]` 的原始实例下标独立管理；升级及附加态各自显示；诅咒不可被普通交换，须保持不可选。
- 现行卡牌不使用手牌、能量徽记或抽手牌规则；概念图里的示例卡文不能被当成卡牌正本。**使用 `CardCatalog`、`CardViewBinder` 与运行时牌库数据。**

## 2. 美术交付的“已可使用”和“缺件”划分

### 2.1 P0 必须优先复用的正式资源

| 用途 | 游戏仓精确路径 | 使用方式 | Unity 已核验元数据 |
|---|---|---|---|
| 骨白大纸面 | `Assets/Art/panels/panel_paper_a03.png` | `Image.Type=Sliced`，保留角饰，纸面中央可读 | GUID `36de27dba2ba4fbc9cc10218eb75ef3d`；Sprite Border L/B/R/T 均 32 |
| 深墨信息分组（可选） | `Assets/Art/panels/panel_ink_a03.png` | 同上，仅局部区域 | GUID `359478e09e1c43bcab09c53ade447182`；Border 均 32 |
| 深色主按钮 | `Assets/Art/buttons/btn_primary_{normal,hover,pressed,disabled}_b03.png` | `SpriteSwap` 四态，图/字分层 | normal GUID `f92d0415c93b16a4895c42ccc4155e63`；Sprite Border=0 |
| 浅色次按钮 | `Assets/Art/buttons/btn_secondary_{normal,hover,pressed,disabled}_b03.png` | 同上 | normal GUID `f262d412a3a04f94db4e443110b115b7`；Border=0 |
| 现有卡牌套装 | `Assets/UI/Cards/CardCore.prefab` 及 `Assets/Art/cardframes/`、`card-illustrations/` | 按绑定器绘制；不得重画独立卡框 | 框源 960×1280；完整框不要设置 Sliced |
| 键盘焦点（可选） | `Assets/Art/overlays/focus_button_a02.png` | 焦点覆盖层；与卡牌选中雾蓝描边互不混淆 | GUID `70c84a5183574f6d99cefde23eae04cb` |
| 章节签（可选） | `Assets/Art/decor/decor_chapter_tab_a02.png` | 仅如真图适配，再以独立 Image 叠在纸板边缘 | GUID `4211b410e7f545f69c0556810e2547e7` |

**B03 图片没有 Nine Slice：** 原图比例 640:112=40:7。推荐按钮 320×56 等比显示，`Image.Type=Simple` 且 `PreserveAspect` 或等比尺寸；严禁将该按钮强行改为 Sliced 造成两端刻痕变形。

可选 `bg_battle_empty_a01.png` 已在工程，GUID `8180cfed80ce4a7384aa7e3aa9e4de3a`；弹层应优先**遮暗原奖励页面**而不是多加载/重画第二套背景。2026-11-01 已退役的八层战斗手记资产不得当“现成”调用。

### 2.2 尚无经过独立审阅的新资产

| 资源代号 | 要达到的效果 | P0 替代方案（无需新 PNG） | 何时需要独立生产 |
|---|---|---|---|
| `exchange_sheet_base_v2` | 大幅错层纸面，细手工边框，中央低纹理 | A03 `panel_paper` 9-slice + 子层细线/浅纸块 | 若 Unity 对照原图后多层质感明显不足 |
| `exchange_label_v2` | “将获得的奖励牌”“选择换出的旧牌”两处短题签 | A03 墨色底、TMP 标题、已有短装饰 | 若需版画状毛边，独立透明、无文字 |
| `exchange_selected_v2` | 雾蓝框、弱光、四角强调，不能盖住卡名 | UI Outline/边框 Image（可先程序化） | 若低分辨率边缘/高亮仍不符合 V05 |
| `exchange_swap_arrow_v2` | 中心单个双向交换记号 | 现有可用图标 / TMP 符号（需检查字体） | 若出现方块字或风格不匹配 |
| `exchange_pager_v2` | 左右翻页图标与页码 | B03 次按钮缩小 + TMP 独立页数 | 若四态与输入反馈无法满足 |

新增独立 PNG 不得通过从“确认稿截图”裁出文字/装饰/卡面合图冒充生产资源；应在设计仓 `ImageReview/` 留审阅版、确认后发布 `Assets/UI/`，并同步游戏仓 `Assets/Art/` 与 `ArtKeys/ArtCatalog`。没有缺陷证据时不要生成新的同功能资源。

**新素材生产规格（仅当确实缺件）：** 透明 RGBA PNG、独立图层、无固定文字、无卡牌插画、无状态数字；命名 `panel_exchange_sheet_v2.png`、`label_exchange_tab_v2.png`、`overlay_exchange_selected_v2.png`。若需要九宫格，则生产均匀直边与角饰只在边带中的源图，建议**源图 512×512、切边 48/48/48/48**作为候选（非既有已确认切片值），必须在 1560×800 和缩小窗口双尺寸检查不失真后定档。选中边建议 256×256 RGBA 四角标记的可九宫格候选，切边根据实测另定，勿先写死为 32。

## 3. 推荐 UI 层级与逐节点映射

现有运行路径：

```text
RewardPanel.prefab
  Parchment/{Skip,Confirm,...}
  Templates/RewardCard
  [SerializeField] _libraryChoiceTemplate -> Assets/UI/Templates/LibraryChoice.prefab

LibraryChoice.prefab             // 现有旧版，必须改造
  Sheet/{Title,Hint,Indicator,Row0..Row5,Prev,Next,Add,Back}
```

推荐接入后的稳定层级（由编辑器生成或修改 prefab，**运行时仅克隆、填数据、监听**）：

```text
LibraryChoice                  (Root，全屏 RectTransform，Image Dim，raycast)
  Dim                         (如根已有遮罩可复用，勿叠两层)
  Sheet                       (Image: A03/Sliced)
    Header
      Title                   (TMP “交换卡牌”)
      Hint                    (TMP 容量/提示)
    IncomingZone              (左，视觉容器)
      Label                   (TMP + 无字签)
      IncomingCard            (CardCore 同构根：Frame,ArtWindow,Name,Desc)
    SwapArrow                 (居中图标)
    OutgoingZone              (右，视觉容器)
      Label                   (TMP + 无字签)
      Grid                    (预制四列×两行容器)
        Row0..Row7            (8 个旧库实例卡：Button、CardCore/缩略信息、SelectedOutline、DisabledReason)
      Prev                    (上一页)
      Indicator               (TMP 例如 1/2)
      Next                    (下一页)
    Back                      (B03 secondary：“返回奖励页”)
    ConfirmExchange           (B03 primary：“确认交换”，默认 disabled)
```

节点名仅为建议稳定合同：执行模型可以迁移现有名字，但**必须同步修改 `LibraryChoiceOverlay.cs` 的 Need/find、编辑器生成脚本、相关测试**。特别注意：现行 `LibraryChoiceOverlaySetup.Run` **检测 prefab 存在即跳过**。只改烘焙器并重跑无效；应对**现有预制体就地升级且保留 .meta GUID、宿主序列化引用**，或实现带断言的幂等迁移器。禁止删除重建导致引用断链。

## 4. 推荐布局参数（逻辑坐标，不是 1672×941 图源像素）

唯一坐标标准：**1920×1080 Canvas 左上原点，x 向右，y 向下**；下表是可执行初值，仍须与原图叠加对照后微调。

| ID | x | y | w | h | 内容 |
|---|---:|---:|---:|---:|---|
| Sheet | 190 | 170 | 1540 | 780 | 主弹层/边框 |
| Title | 350 | 195 | 1220 | 68 | 标题 |
| Hint | 390 | 270 | 1140 | 44 | 满库信息与引导 |
| IncomingZone | 255 | 330 | 435 | 482 | 左新卡区 |
| IncomingCard | 318 | 376 | 300 | 400 | 3:4 大卡 |
| OutgoingZone | 755 | 330 | 900 | 482 | 右旧库区 |
| Grid | 810 | 366 | 716 | 401 | 旧卡起点，4 列×2 行 |
| OldCard0..7 | 810+190×col | 366+206×row | 146 | 195 | 3:4 缩略，col=0..3,row=0..1 |
| PageControls | 1010 | 780 | 390 | 42 | Prev/页码/Next |
| Back | 455 | 858 | 320 | 56 | B03 secondary |
| ConfirmExchange | 1005 | 858 | 320 | 56 | B03 primary |

- 控制逻辑分辨率与实际屏幕尺寸；建议沿现有 CanvasScaler 配置（项目参考 1920×1080）。**不要凭坐标重置整个 CanvasScaler**。
- 1280×720 对应 2/3 缩放只是首版；此时 146×195 缩略成为约 97×130，**小卡效果全文不应该被强行塞进去**。至少保持卡图、卡名、升级/共鸣标识、禁用与选中态可读；完整效果由悬停/焦点的卡牌详情承载。
- 设计原图右侧卡片视觉比例偏方，工程仍优先使用**正式 3:4 卡框不变形**；若视觉不符合，调整区域间距/裁剪展示规则，不拉扁卡框。
- 现有 B03 按钮 320×56 等比；确认、返回及页控在最小目标分辨率可点击，不得因纸面装饰拦截射线。

## 5. 运行时数据绑定与预加载

| UI 目标 | 运行时来源 | 约束 |
|---|---|---|
| 新卡大图 | 传入的 `incoming` + `CardCatalog.ByName` | 使用 `CardViewBinder.Bind`；复用 FrameKeyOf/ CardArtKeyOf/ FrameWindowOf |
| 旧库卡序列 | `IReadOnlyList<LibraryCard> library` | **按原始下标**；`Name`、`Upgraded`、`Resonated` 独立投影；同名可重复 |
| 旧牌可选 | `RunSession.CanAcquire(library,capacity,index)` | 不可交换诅咒；禁用必须阻断事件，仍显示原牌 |
| 直接加入 | `RunSession.CanAcquire(library,capacity,null)` | 只在奖励页未满分支生效；交换弹层不要放“加入空位”按钮 |
| 确认交换 | 原始 index + incoming | 确认瞬间复核合法性；只调用一次消费/结算 API |
| 牌库容量 | `library.Count` / `capacity` | 可能超容；不能写死为 12 |
| 页数 | `Mathf.Max(1, (library.Count + 7) / 8)` | 以实际条目总数计算；不得仅计算可交换条目 |
| 旧卡缩略内容 | `CardCatalog.ByName(library[i].Name)` | `Upgraded` 需按既有升级投影呈现；共鸣状态仅公开正面展示 |

**冷加载特别注意：** 目前 `RewardPanel.PreloadKeys()` 只覆盖三候选与额外掉落遗物。改造后右侧需要真实 `library` 全量卡图及框：必须在面板准备期补充所需帧与插画键，或使用框架可验证的共享预加载机制；不能依赖缓存碰巧命中，否则出现大块占位美术。商店和事件同样调用共享弹层，亦应逐宿主验证冷启动。

字体：游戏仓当前含 `MapleMono-NF-CN-Bold SDF`；设计仓有思源字体方案，但**不应默默假设游戏仓已安装**。优先确保现行 TMP 能正确显示所有中文及页码，再把思源字体对齐作为独立替换任务，禁止自行拷贝不具许可证的字体或宣称已切换。

## 6. UI 状态、事件与防错

- 新卡选中态与旧牌选中态分离；键盘/手柄 Focus 与永久 Selected 分离。
- 旧卡点选不写入库；翻页保持被选实例下标，不因为页内序号变化导致换错卡。
- 选中禁用的诅咒无效；卡库完全不可换时可返回奖励页跳过。
- 交换弹层背景全屏阻断输入；Back/Esc 取消，归还到原候选页面；双击 Confirm 不会提交两次。
- 若当前库列表变化，确认时需检查原始实例身份/快照，不应仅用同名卡判断，避免错换。
- 共用 `LibraryChoiceOverlay` 的三宿主（奖励、商店、事件）仍保持各自交易提交时机；特别是金币只在商店确认成功时扣，事件取消不扣取决于既有事务口径。
- “收到新卡”反馈不新增中间领取页（2026-10-24 裁定），成功即推进。

## 7. Unity 图片导入与层级检验

1. 现有 asset **读取 .meta 的实际设置**，不要重新导入造成 GUID 改变；A03 是 32 四边 Sliced，B03 是 Simple/四态，卡框与卡图不额外九宫格。
2. 若生产独立 PNG：2D Sprite、sRGB、RGBA Alpha Is Transparency、无 MipMaps（UI 场景）；Filter Mode Bilinear（沿用同族），移动平台压缩先以不损伤细轮廓优先，记录测试平台与压缩质量。新 .meta 必须提交；地址键与 `ArtKeys/ArtCatalog` 同步。
3. 分层顺序：奖励页面 -> 全屏 Dim 阻断 -> 交换 Sheet -> 区域底板 -> 旧/新卡 -> 文本 -> 选中态 -> 弹层按钮与焦点；装饰 Image 默认 `raycastTarget=false`。
4. 不从完整概念稿切割生成运行时卡图；不把含文字的概念稿烘焙到任何 Sprite。
5. 任一新资源必须清单记录：源文件、透明边、尺寸、GUID/资源键、导入设置、9-slice 或 Simple、使用节点、验证截图、是否通过审阅。

## 8. 交付/验收矩阵（其他模型必须实际运行）

| 用例 | 测试设置 | 通过条件 |
|---|---|---|
| 奖励未满 | 11/12，选新卡 | 直接加入变 12/12，无弹层 |
| 满库第一页 | 12/12 | 点确认即打开弹层；1/2 页 8 张，显示实例不去重 |
| 第二页选择 | 12/12 | 页 2/2 4 张，选择一个后按钮启用，翻页不丢选择 |
| 原子交换 | 12/12，已选旧卡 | 点击旧卡无变化；再点确认才执行且牌库仍 12/12 |
| 返回 | 满库交换打开后 | 不修改牌库、不丢候选、可重新选择或跳过 |
| 诅咒/超容 | 13/12 或含诅咒 | 不允许直接加入，禁用诅咒，合法旧卡可换 |
| 边界容量 | 0/1/8/9/12/16/17 张 | 页数、空位禁用、箭头可用状态正确 |
| 三宿主回归 | Reward/Shop/Event | 交易/选择/取消原子性及金额正确 |
| 冷启动真实贴图 | 清空 AssetCatalog/重启 Editor | 所有缩略卡加载真实图框，缺图有报告而非默默“验收通过” |
| 视觉基准 | 1920×1080 + 1280×720 | 与原图比例/层级相符；卡名可读、按钮可点、内容不遮挡 |

交付必须有：**独立资源清单（含复用映射）、Editor 中预制体层级截图、两分辨率游戏实机截图、至少一次满额翻页+选择+确认的录屏或步骤证据、自动测试结果、未完成差异表**。建议保留参考/实机/半透明叠加三图及截图实际测试数据。

## 9. 执行顺序与停机线

**P0：零新美术版本** → 更新预制体结构与真实卡图绑定，完成状态机、8 卡分页、禁用/焦点、两分辨率可读性、三宿主回归。此时允许标记“**可玩接入完成，正式视觉精修待对照**”。

**P1：视觉还原** → 与已确认的原始 PNG 对照，检查 A03 平铺效果与装饰是否充分；只对可证明不达标的具体区域生产独立资源，再按 ImageReview→Assets/UI→Unity 项目流转。资源审阅前不可宣称“视觉还原完成”。

**停机线：** 不允许为了凑“美术完成”把整张概念图当运行时贴图；不允许因缺少独立资源而修改交易规则；不允许未经截图就认定九宫格拉伸无误；不允许丢弃/重建既有 .meta 后留下宿主丢失的 serialized prefab 引用。

**建议交接 AI 直接执行顺序：** 读取 14/17/18 → 读取 asset-handoff.json + SVG → 读取游戏仓 RewardPanel/LibraryChoiceOverlay/LibraryChoiceOverlaySetup/CardCore → 交互/预制体/预加载改造 → 自动测试+双分辨率截图 → 视觉差异补件；只在拿到高保真原图后做“最终风格验收”。
