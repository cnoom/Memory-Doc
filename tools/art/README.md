# 本地美术工具

旧生图技能已移除。此目录保留不依赖远程网关的程序化合成、图片处理和校验工具，以及历史规格资料。

在仓库根目录运行，依赖 Pillow、numpy，部分卡框处理需要 scipy：

- `scripts/card_frame_mockup.py`：整卡效果图合成。
- `scripts/frame_b_pipeline.py`：分层卡框生成。
- `scripts/frame_style_sketch.py`：卡框布局示意。
- `scripts/roundify_card.py`：卡形和透明窗口处理。
- `scripts/ui_mockup.py`：界面示意图合成。
- `scripts/verify_card.py`：卡背、卡框量化校验。

示例：`python tools/art/scripts/verify_card.py Assets/UI/cardframes/border_card_attack.png --type attack`

`references/asset-specs.md` 为历史资产名录，当前设计以 `docs/design/` 为准；`references/frame-pipeline-pitfalls.md` 保留卡框制作复盘。

运行历史脚本前检查其输出路径；部分脚本可能直接写入正式资产目录。任何覆盖或发布仍须遵循 [预览与发布流程](../../ImageReview/README.md)，先生成候选并由用户确认。
