# V02 战斗页精排预览

日期：2026-09-25。用户已认可首轮版画方向，并在查看本批交付后回复「可以的」。V02 已确认收录到 `Assets/UI/mockups/battle-etching-v02/`；本目录保留预览与制作记录，维持当前预览地址。以下为本批制作说明。

## 查看

直接用浏览器打开 `index.html`；页面不依赖网络。下方设计工具栏可切换常态、临界状态和卡牌详情，也可点击正面卡；Esc 关闭详情。隐藏牌不会在预览中翻开，不实现战斗模拟。

## 交付内容

- `../mockup_s03_etching_v02.png`：1920×1080 常态。
- `../mockup_s03_etching_v02_danger.png`：十格行动条 9/10 的临界示意。
- `../mockup_s03_etching_v02_detail.png`：完整规则详情，保留牌阵与敌人关键数值。
- `../mockup_s03_etching_v02_720p.png`、`../mockup_s03_etching_v02_720p_detail.png`：1280×720 独立字号与间距检查。
- `index.html`、`style.css`、`app.js`：可复用的布局与交互示意源文件。
- `verification.json`：浏览器检查结果。

## 本轮决策

1. 卡牌几何由 CSS 控制：1080p 为 144×192，720p 为 96×128，严格 3:4。四行四列，常态只一张正面。
2. 卡背为独立 SVG 几何徽记，所有实例一致；去除微细磨损和噪点，避免留下可识别身份的随机纹理。
3. 行动条由十个真实组件生成，常态 1/10、临界 9/10；临界同时有颜色、末格轮廓与文字提示。
4. 数字和中文全部由浏览器文字排版，场景和书本插画中无 UI 字样。正式游戏移植时由 TMP 或对应 UI 字体组件渲染。
5. 小卡补充「翻开·标记邻牌」摘要，详情完整解释随机目标、相邻、优先选择、共鸣和标记期限。
6. 为避免宽详情遮盖网格，改成右栏详情；暂替换敌人展示区域，底部保留敌人生命、行动条数值、攻击预告，玩家区域仍保留。
7. 720p 使用单独字体与间距，不整屏按 2/3 缩小。更小窗口按预览画布缩放，暂不宣称支持移动端。
8. 左侧遗物栏为空，不再使用无法对应实际持有遗物的装饰图标。

## 验证

浏览器渲染检查通过：16 张卡、1 张正面、精确比例、10 格刻度、常态/临界格数、详情打开/关闭、隐藏牌不泄露、图片全部载入、页面无横向溢出、720p 详情不越界。另已逐图检查正常、临界、详情和 720p 的可读性。

## 制作边界

这是一份设计预览，不是游戏代码或 Unity 预制体。两张插画使用内置 image_gen 生成，再由 HTML/CSS/SVG 合成 UI，未使用 API/CLI 回退。场景暂包含敌人和学者，正式游戏资产需再拆成独立立绘、背景与动效层。工具栏的临界切换仅改变观察状态，不表示模拟完整战斗过程；牌堆说明是示意交互，不伪造完整牌堆内容。

系统字体为本地宋体与微软雅黑回退，未打包字体授权文件。内容提示中的短摘要需要通过完整详情理解；正式部署仍需字体、交互和多状态验证。

## 复现

运行仓库根目录的 `tools/art/scripts/render_etching_preview.cjs`，参数为 Playwright 模块路径。脚本只写本批 ImageReview 预览和验证文件，不执行发布。

## 生成提示词

### 无字背景

```text
Use case: precise-object-edit / production game background.
Edit this approved Chinese game screenshot into a TEXTLESS illustration background for a new accurately coded UI. Keep the same premium bone-white and charcoal etched woodcut style, same mischievous ink CHAOS SLIME and same scholar with glasses, same low-contrast ruins. Landscape 16:9 at 1920x1080 if possible.
REMOVE all sixteen cards completely, every border around them, the left relic icons, all words, numbers, all UI bars, progress meters, buttons, top navigation line and all separators. No writing anywhere.
Composition required: left 60 percent is a dark smooth charcoal tabletop with only very faint texture, completely empty for a 4x4 grid. Edge scenery stays only at far left and bottom-left. Right 40 percent is a bone-white illustrated region. Keep slime on upper right in x=1250..1760 y=110..450, with faint ruined buildings behind it. The entire right-middle region y=470..790 is CLEAN UNMARKED bone-white paper reserved for readable UI, no scenery or lines. Scholar bust small at bottom-right region, x=1170..1360 y=840..1060, leaving everything right of him blank for player stats. Keep all important art within margins. Simplify fine hatching and scratches by about half: broad ink shapes and spare linework, avoid visual noise. Use an organic transition between dark left and light right around x=1120, no ornate frame. Absolutely no cards, no glyphs, no text, no logos, no circles pretending to be controls. This is a background layer, not a finished screen.
```

### 透明书本插画

```text
Use case: stylized-concept.
Create one isolated CARD ILLUSTRATION asset for the approved woodcut / etched memory-adventure game. Subject: a single open book, two broad outspread pages, clean strong horizontally spreading silhouette, viewed slightly from above. One small mist-blue annotation-shaped brushstroke over the right page. Black ink on bone-white paper pages, coarse sparse etched lines, large readable shapes, refined graphic printmaking with a touch of magic. Page markings must be only a few abstract hatch marks, NO legible writing, NO glyphs, NO letters. Simplify aggressively so the illustration reads at 110x65 pixels. No quill, no glowing orb, no stars, no decorative frame. Subject centered, entire book visible, generous clear margins. Transparent background. NO card rectangle, NO card title, NO numbers, NO UI. Landscape-oriented subject in a square output, book spans 80 percent of width and 50 percent of height. Left-top illumination rendered as paper white, not glossy gradients.
```
