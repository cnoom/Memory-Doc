# V05 · 手记细节版（已确认）

用户已确认本版细节密度，含角色重叠修正。自包含源与截图已收录 Assets/UI/mockups/battle-journal-v05。V05 是后续细节基准，保留 B03 的基础组件方向。

新增：轻纸纤维、封皮细纹、书角压线、装订孔、书签缝线、章节侧签、夹页、肖像衬纸与纸胶带、肖像题签、铅笔式批注、页尾刻花与浅压印。菜单区仍保持留白；肖像复用 B01，书体与装饰由 CSS/SVG 绘制。

打开 index.html 默认展示暂停手记；?battle 进入战斗。左下“细节对照”可隐藏部分新增装饰，不是 V04 的完整复现。继续探索、Esc、关闭按钮合上手记，右上重新打开。设置为审阅页内示例，不影响游戏数据；返回主菜单不会实际退出。

details.css、details.js 为本轮新增细节层；journal.css、journal.js 为继承的手记结构；style.css、app.js 为 V02 战斗布局基础。依赖同级上两层的 backgrounds、cards、portraits 预览资源，保留原目录关系运行。

检查脚本：tools/art/scripts/check_ui_b05.cjs。validation.json 为检查结果，review_pause_1080.png、review_pause_720.png 为两种舞台尺寸的暂停截图；review_battle_1080.png、review_battle_720.png 为战斗截图。固定牌阵 16 张、稳定态正面 1 张；720p 卡牌 96×128。实装贴图拆分、字体和游戏内动画尚未交付，本轮为视觉候选。

修正：缩减敌人信息区纵向留白，将意图与临界提示排在同一行，常态/临界保持同高，避开背景中学者头部。1080p 信息区底部 y=688；720p 底部 y=487。专项检查见 overlap-validation.json 与 check_ui_b05_overlap.cjs。
