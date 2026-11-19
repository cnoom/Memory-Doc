# 仓库边界（Memory-Doc 侧）

本仓只保留玩法、系统与内容策划文档及文本型策划附件（JSON/YAML/CSV/Mermaid 等）。美术二进制、审阅候选、UI 视觉稿、艺术制作脚本与正式美术资源副本不在本仓长期保留。

- 最终职责边界、文件分类表、混合文档拆分与清理顺序的**唯一操作合同**：[Memory-Art docs/repository-boundaries-and-cleanup.md](https://github.com/cnoom/Memory-Art/blob/main/docs/repository-boundaries-and-cleanup.md)。
- 美术视觉正本：Memory-Art（版本规则见其 `docs/art-versioning.md`）。Unity 运行时事实：MemoryRouge。
- 跨仓引用一律使用 GitHub 链接指向对应仓库正本，不在本仓复制第二份继续维护。

## 迁移与清理状态（2026-11-18）

- **Phase 1–3 已完成**：Memory-Art#2 与 Memory-Doc#6 已按顺序合并；双仓落地树与本地验收树一致，27/27 条跨仓 GitHub URL 有效，migration-manifest 2250 条记录完成复核；Memory-Art `versions/index.json.latestReady=true`。
- **Phase 4 源仓清理**：本次独立清理变更删除 Memory-Doc 中已迁移的美术副本：`Assets/` 505 文件、`ImageReview/` 1190 文件、`美术资源v1/` 468 文件、`tools/art/` 87 文件，以及 10 个已迁移的美术专项文档/台账文件。精确清单与源树基线见 [Phase 4 清理记录](./art-source-cleanup-2026-11-18.md)。
- 美术资源与视觉规范唯一正本为 [Memory-Art](https://github.com/cnoom/Memory-Art)；正式 v1 清单为 [资源索引.json](https://github.com/cnoom/Memory-Art/blob/main/versions/v1/资源索引.json)。玩法、交互与系统策划继续以本仓为准；Unity 运行时事实以 [MemoryRouge](https://github.com/cnoom/MemoryRouge) 为准。
- 本次只从 Memory-Doc 当前工作树删除副本，**不重写或清理 Git 历史**；MemoryRouge 未修改。