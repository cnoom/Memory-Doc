# 读书笔记背景修复

日期：2026-10-24。用户明确授权替换。

使用内置 imagegen 编辑原卡图：仅为透明区域补骨白纸底及轻微纸纹，保留书本构图、黑色线条和蓝色羽毛标记；生成式编辑不保证主体逐像素不变。成品1254×1254，RGB不透明。

已同步 Assets/UI/cards、美术资源v1/cards 和 F:/UnityProject/MemoryRouge/Assets/Art/card-illustrations，沿用原文件名与Unity meta。开发索引、导出索引、替换映射及文件校验清单同步更新。历史组合参考不重绘。

旧图归档：../../_archived/2026-10-24/cards/dushubiji-background/

预览：../../cards/card_attack_dushubiji_background_fix_20261024.png

提示词：Use case: compositing. Image 1 is edit target, image 2 only background color/texture reference. Fix missing background on image 1: fill all transparent space with fully opaque pale bone ivory paper matching image 2, very subtle paper grain. Preserve the original open book exactly including its position, scale, black ink outlines, sparse page strokes, blue feather mark and existing composition. Do not redraw or restyle the book, add objects, text, border, shadow, vignette or crop. Square output, requested 1254x1254. Change only the transparent backdrop to ivory paper.
