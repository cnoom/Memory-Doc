# 《记忆勇者》设计文档仓库

本仓库是《记忆勇者》（记忆配对卡牌肉鸽）的纯设计文档仓库，无游戏代码。文档位于 `docs/design/`（00-总览 起）。

## AI 生图约定

- **凡与游戏资产相关的生图**（卡面插画、卡背、遗物/道具/状态/意图/功能图标、地图节点、敌人立绘、角色立绘、背景、纹理），使用项目级技能 **mh-art**（`.agents/skills/mh-art/SKILL.md`）——它复用用户级 germmc-image2 的 API 通道，叠加本项目的规格、命名与目录流转。此约定收窄用户级 AGENTS.md 中"生图一律走 germmc-image2"的默认规则。
- 图片三目录流转：**预览** `ImageReview/<类型>/`（进 git，便于远端查看）→ **归档** `ImageReview/_archived/<日期>/<类型>/` → **实际应用** `Assets/UI/`（项目根目录，进 git，扁平无子目录，文件名前缀区分类别，被设计文档嵌入）。详见 `ImageReview/README.md` 与 `Assets/UI/README.md`。
- 与游戏资产无关的通用生图（海报、封面、任意插图）仍走用户级 germmc-image2。
