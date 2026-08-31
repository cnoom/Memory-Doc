#!/usr/bin/env python3
"""卡牌资产自动验收——《记忆勇者》卡背/卡框发布前必跑（SKILL 工作流第 5 步）。

历史教训（frame-pipeline-pitfalls.md）：多轮返工源于交付前缺少系统自检，
每轮只修用户指出的点、修 A 破 B。本脚本把量化检查固化，任何改动后跑一遍
自证，避免"你看下→再修"的循环。

检查项（全部通过 exit 0）：
  1. 3:4 比例（±1%）
  2. 黑不透明像素 = 0（`sum(RGB)<30 & alpha==255`——拼接画布透明黑暴露等）
  3. 四角透明（圆角 alpha=0）
  4. 边带宽度：四边中线扫描 20–32px（程序环 26±6）
  5. 描边主色偏差：主段（距缘 8–20px）中位色 vs 类型色板（RING_PALETTES
     主环色）偏差和 < 40（--type 指定；不传则跳过）
  6. 窗镂空：窗中心（0.42h, w/2）alpha=0（默认检查；卡背用 --no-window）
  7. 描边沿边波动：边带区相邻行均差 < 8（生长/重绘条纹与断层检测）

用法：
    python .agents/skills/mh-art/scripts/verify_card.py Assets/UI/border_card_attack.png --type attack
    python .agents/skills/mh-art/scripts/verify_card.py Assets/UI/cardback_universal.png --no-window
    python .agents/skills/mh-art/scripts/verify_card.py Assets/UI/border_card_*.png --type attack  # 逐个
"""

import argparse
import math
import os
import sys

import numpy as np
from PIL import Image

# 与 roundify_card.RING_PALETTES 对齐的主环色（验收参照）
PALETTES = {
    "attack": (139, 44, 44),
    "skill": (44, 74, 139),
    "ability": (91, 44, 139),
    "curse": (58, 42, 58),
}


def creamish(a):
    return (np.abs(a[..., 0] - 249) < 26) & (np.abs(a[..., 1] - 234) < 26) \
        & (np.abs(a[..., 2] - 206) < 30)


def check(path, type_key, expect_window, no_band=False):
    issues = []
    im = Image.open(path)
    if im.mode != "RGBA":
        issues.append(f"mode={im.mode}，应为 RGBA")
    a = np.asarray(im.convert("RGBA"))
    h, w = a.shape[:2]
    rgb = a[..., :3].astype(int)
    alpha = a[..., 3]

    # 1 比例
    if abs(w / h - 3 / 4) > 0.01:
        issues.append(f"比例 {w}x{h} 非 3:4")

    # 2 黑像素
    black = int(((rgb.sum(axis=2) < 30) & (alpha == 255)).sum())
    if black:
        issues.append(f"黑不透明像素 {black}（应为 0）")

    # 3 四角透明
    corners = [alpha[2, 2], alpha[2, w - 3], alpha[h - 3, 2], alpha[h - 3, w - 3]]
    if max(corners) > 8:
        issues.append(f"四角 alpha {corners}（应为 0）")

    # 4 程序环完整性：0–26px 环带区不应出现卡面奶油（程序描边环 26px，
    #   环外内容层装饰（底座/金线）不参与判定——"到首奶油距离"会把贴边
    #   装饰误报为边带宽，已踩坑）。只统计不透明像素：圆角外透明区的
    #   RGB 底色（程序生成资产常为奶油画布）不参与判定。
    if not no_band:
        for name, band, aband in (("左", rgb[:, 0:26], alpha[:, 0:26]),
                                   ("右", rgb[:, -26:], alpha[:, -26:]),
                                   ("上", rgb[0:26], alpha[0:26]),
                                   ("下", rgb[-26:], alpha[-26:])):
            cream_ratio = float((creamish(band) & (aband == 255)).mean())
            if cream_ratio > 0.05:
                issues.append(f"边带{name}环带区含卡面奶油 {cream_ratio:.0%}")

    # 5 主色偏差
    if not no_band and type_key and type_key in PALETTES:
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
        zone = (d > 8) & (d < 20)
        med = np.median(rgb[zone], axis=0).astype(int)
        dev = int(np.abs(med - np.array(PALETTES[type_key])).sum())
        if dev > 40:
            issues.append(f"描边主色偏差和 {dev}（应 <40，实测 {tuple(med)} vs 色板 {PALETTES[type_key]}）")

    # 6 窗镂空
    if no_band:
        pass
    elif expect_window:
        wc = alpha[int(h * 0.42), w // 2]
        if wc > 8:
            issues.append(f"窗中心 alpha={wc}（插画窗应镂空）")
        win_px = int((alpha < 128).sum())
        if win_px < h * w * 0.03:
            issues.append(f"镂空区过小 {win_px}px")

        # 6b 洞边残留（分层镂空验收）：从窗中心向 24 向发射线，首个不透明
        # 像素若仍是窗底色（与窗中心 RGB 差和 <48）→ 洞外残留窗底色环
        # （旧版"洞<真窗、插画漂在异色环里"的根因量化）
        cy0, cx0 = int(h * 0.42), w // 2
        ref = rgb[cy0, cx0]
        bad = []
        for k in range(24):
            ang = k * math.pi / 12
            dx, dy = math.cos(ang), math.sin(ang)
            for r in range(4, int(min(h, w) * 0.45)):
                x, y = int(cx0 + dx * r), int(cy0 + dy * r)
                if not (0 <= x < w and 0 <= y < h):
                    break
                if alpha[y, x] >= 200:
                    if int(np.abs(rgb[y, x].astype(int) - ref).sum()) < 48:
                        bad.append((k, r, tuple(rgb[y, x])))
                    break
        if bad:
            issues.append(f"洞边残留窗底色 {len(bad)}/24 向（如向{bad[0][0]} r={bad[0][1]} 色{bad[0][2]}）——洞应贴到金饰内沿")

    # 7 沿边波动
    strip = (rgb if no_band else rgb[:, w - 18:w - 8]).astype(float).mean(axis=1)
    wav = float(np.abs(np.diff(strip, axis=0)).mean())
    if wav > 8:
        issues.append(f"边带沿边波动 {wav:.1f}（应 <8，疑似条纹/断层）")

    return issues


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="asset PNG paths")
    ap.add_argument("--type", choices=list(PALETTES), help="type for palette check (skip if omitted)")
    ap.add_argument("--no-window", action="store_true", help="skip hollow-window check (cardback)")
    args = ap.parse_args()

    failed = 0
    for p in args.paths:
        if not os.path.isfile(p):
            print(f"FAIL  {p}: 文件不存在")
            failed += 1
            continue
        try:
            issues = check(p, args.type, not args.no_window, no_band=args.no_window)
        except Exception as e:
            issues = [f"异常: {type(e).__name__}: {e}"]
        if issues:
            failed += 1
            print(f"FAIL  {p}")
            for it in issues:
                print(f"      - {it}")
        else:
            print(f"PASS  {p}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
