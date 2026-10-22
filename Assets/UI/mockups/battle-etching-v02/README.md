# 战斗 UI V02 · 用户确认稿

确认日期：2026-09-25。用户查看交付后回复「可以的」，据此将本批从 ImageReview 收录到 Assets/UI。

## 内容

- `index.html`、`style.css`、`app.js`：可点击的设计稿，包含常态、临界、正面牌详情。
- `verification.json`：本批浏览器验证记录。
- 上级目录 `mockup_s03_battle.png`、`mockup_s03_battle_detail.png`、`mockup_s03_battle_danger.png`、`mockup_s03_battle_720p.png`、`mockup_s03_battle_720p_detail.png`：确认稿截图。
- `../../backgrounds/bg_battle_etching_textless_v02.png`：无字场景底图。
- `../../cards/card_attack_dushubiji_illustration_v02.png`：透明书本插画。

直接用浏览器打开 index.html，无网络依赖。1080p 卡牌为 144×192，720p 为 96×128；十格行动条和所有规则文字由 UI 层生成。

这是设计基准，不是战斗引擎或 Unity 预制体。场景中的敌人与角色仍为合并底图，正式游戏需要再拆层。字体使用本地字体回退，没有包含字体授权文件。

生成方式：内置 image_gen 制作插画，HTML/CSS/SVG 排版，Playwright 渲染验证。完整提示词和制作说明保留于 `ImageReview/mockups/battle-etching-v02/README.md`。原预览文件保留，以维持当前本地预览地址。

后续修改仍先生成新版本预览，经确认后再替换本目录。
