# 《记忆勇者》设计文档仓库

本仓库是《记忆勇者》（记忆配对卡牌肉鸽）的纯设计文档仓库，无游戏代码。文档位于 `docs/design/`（00-总览 起）。

## 开发 AI 接入入口

接入或导出美术资源前，阅读 `docs/design/13-开发AI美术资源使用说明.md`；准确路径、尺寸与用途见 `docs/design/art-inventory/developer-asset-registry.json`。索引为确认状态快照，用户最新指令优先。区分正式独立资源、组合参考与待审候选，不能把示意代码当作游戏实现。当前细节基准为 V05，基础组件方向为 B03。

## AI 生图约定

- 生图使用当前环境可用的技能或工具。游戏资产的规格与命名遵循 `docs/design/10-UI美术资源规格.md`，风格遵循 `docs/design/09-UI设计规范.md` 及用户最新确认的方向。
- 图片三目录流转：**预览** `ImageReview/<类型>/`（进 git，便于远端查看）→ **归档** `ImageReview/_archived/<日期>/<类型>/` → **实际应用** `Assets/UI/<类型>/`（项目根目录，进 git，按类型分子目录）。**发布必须先经用户确认拍板**：校验通过不等于发布许可，示意图等一切生成资源先留在 ImageReview，用户确认后才可移动到 Assets/UI 并嵌入设计文档。详见 `ImageReview/README.md` 与 `Assets/UI/README.md`。
- 本地卡框合成、图片校验工具及资产参考资料保留在 `tools/art/`，不依赖生图网关。
