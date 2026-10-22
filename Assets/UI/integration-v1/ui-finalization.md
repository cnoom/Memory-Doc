# v1 UI视觉定稿清单

2026-10-21。共17类界面全部标记视觉定稿，另有2批动效/特效表现规范已定稿。用户授权本次统一定稿，U01战斗常态采用正式资源组合，暂停与详情沿用V05结构。没有重绘或修改玩法。

**设计参考 ≠ 未定稿。** visualStatus=final表示可按稿实现；runtimeTexture=false/productionEligible=false表示组合图不能直接作为独立贴图导入；implementationStatus=not-verified表示尚无客户端实机验收证据。不要因后两项再次阻塞视觉接入。

|界面|正式来源（Assets/UI根目录）|状态|
|---|---|---|
|启动Logo|mockups/startup-v03/startup_cover_v03.png|视觉定稿，可接入|
|主菜单|mockups/entry-h02/mockup_main_menu_h02_1920x1080.png|视觉定稿，可接入|
|加载页|mockups/entry-h02/mockup_loading_h02_1920x1080.png|视觉定稿，可接入|
|角色选择|mockups/v1-closure-p01/character_select.png|视觉定稿，可接入|
|地图|mockups/map-i03/mockup_map_i03_1920x1080.png|视觉定稿，可接入|
|战斗|mockups/battle-u01/normal.png|视觉定稿，可接入|
|暂停手记/卡牌详情|mockups/battle-journal-v05/index.html|视觉定稿，可接入|
|设置|mockups/settings-j02/mockup_settings_j02_1920x1080.png|视觉定稿，可接入|
|商店|mockups/shop-k02/mockup_shop_k02_1920x1080.png|视觉定稿，可接入|
|移除卡牌|mockups/shop-k04/selected.png|视觉定稿，可接入|
|篝火|mockups/campfire-l01/mockup_campfire_l01_1920x1080.png|视觉定稿，可接入|
|强化卡牌|mockups/campfire-l03/selected.png|视觉定稿，可接入|
|事件选择与结果|mockups/event-m01/choices.png|视觉定稿，可接入|
|战后卡牌奖励|mockups/reward-n01/selected.png|视觉定稿，可接入|
|Boss遗物奖励|mockups/relic-reward-o01/selected.png|视觉定稿，可接入|
|旅途详情|mockups/v1-closure-p01/journey_profile.png|视觉定稿，可接入|
|胜利/失败结算|mockups/v1-closure-p01/victory.png|视觉定稿，可接入|

交付包来源路径请通过设计参考索引中的references与文件清单查找；组合参考副本位于设计参考/相应ID，不能直接把本表仓库路径拼到交付包中。

未绘制的长列表、排序展开、溢出、非16:9布局、启动失败分支仍须工程补充和截图验证；这不撤销已有页面定稿。不得删功能或声称未覆盖分支已像素验收。启动Logo仍为整图方向，独立拆分尚未提供。

历史草稿、被否决L02、旧启动V01/V02、旧卡框和I04占位详情不在本次批准范围。U01卡面小字与生命填充等工程约束以battle-replacement.md为准，不能照抄组装脚本作为游戏逻辑。
