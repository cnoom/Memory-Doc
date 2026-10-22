# V04 · 战斗内旅途手记（待审）

根据用户对 B03「网页感偏重」的反馈制作的新候选，不替换已确认的 V02/B03。

入口 index.html 默认打开暂停手记；index.html?battle 显示战斗。使用原 V02 背景、规则示例与固定牌阵，在场景内验证纸质菜单，而非展示页分栏。背景含人物，未拆为独立动态场景。

新增双页纸张曲面、书脊凹槽、四处缝线、页边、布书签、折角与印章；右页选项采用书页排版和纸签反馈。左页复用 B01 学者版画作为主题参考，不自动批准 B01 整批资源。战斗信息使用姓名短纸签、暗色墨面、细生命槽与意图挂签。

书体、纸张与控件均为 HTML/CSS，未使用新的 AI 生图；本轮未交付引擎九宫格贴图。保留 B03 色板和物件主题，UI 文案与数值独立排版。

继续探索 / × / Esc 合上手记；右上角入口重新打开。设置提供音量滑条和减少动态效果示例，均只影响审阅页面，不保存游戏设置。返回主菜单仅提示，不执行退出。暂停层约束焦点、背景舞台设为 inert；背面牌不执行战斗模拟。底部常态/临界/详情按钮是审阅工具。

校验：1920×1080 与 1280×720 的舞台截图；16 张固定位置卡牌、稳定态 1 张正面；720p 卡牌 96×128；暂停开启/关闭、设置、Esc 与正面详情。检查脚本 tools/art/scripts/check_ui_b04.cjs，记录 validation.json。

review_pause_1080.png / review_pause_720.png 为暂停；review_battle_1080.png / review_battle_720.png 为战斗。

依赖 ImageReview/backgrounds/bg_battle_etching_textless_v02.png、cards/card_attack_dushubiji_illustration_v02.png、portraits/portrait_scholar_etching_b01.png。新稿保留 ImageReview，待用户确认后再收录 Assets/UI。
