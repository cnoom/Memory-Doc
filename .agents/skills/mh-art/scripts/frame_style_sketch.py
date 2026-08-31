#!/usr/bin/env python3
"""卡框内部细节改版·风格方向示意图——《记忆勇者》分层画法模板。

分层画法（与发布管线同构，几何全部程序绘制，类型只注入颜色）：
  L1 描边环层  ring      RING_PALETTES 逐层圆角矩形（与 roundify_card 同源）
  L2 卡面层    face      奶油纸平色（正式版可叠 texture_parchment AI 纹理层）
  L3 窗体层    window    拱窗/月洞窗净底（类型浅色 tint）+ 深描边
  L4 饰件层    trim      金饰线/星/柱/徽带（金 + 类型色 + 深描边）
  L5 效果区层  panel     面板/金线规（文字仍由引擎 TMP 渲染，不烘焙）

三个方向 × 四类型：几何完全一致，仅 RING/类型色参数不同。
输出：ImageReview/cardframes/frame_sketch_{a,b,c}_{type}.png（480×640）
      + frame_sketch_{a,b,c}_sheet.png（四类型拼图）

用法（仓库根目录）：
    python .agents/skills/mh-art/scripts/frame_style_sketch.py
"""

import os

from PIL import Image, ImageDraw, ImageFont

from roundify_card import RING_PALETTES, CREAM

S = 2                                   # 2x 超采样，缩回 480 消锯齿
W, H = 480, 640
GOLD = (212, 168, 87)
GOLD_DK = (176, 130, 62)
INK = (59, 50, 38)
FACE = CREAM                            # (249, 234, 206)
PANEL = (239, 231, 210)

TYPES = {
    "attack":  dict(label="攻击", dark=(139, 44, 44), light=(212, 69, 69), win=(217, 238, 225)),
    "skill":   dict(label="技能", dark=(44, 74, 139), light=(69, 119, 212), win=(219, 233, 243)),
    "ability": dict(label="能力", dark=(91, 44, 139), light=(155, 69, 212), win=(230, 224, 242)),
    "curse":   dict(label="诅咒", dark=(58, 42, 58), light=(58, 42, 58), win=(229, 223, 231)),
}
ORDER = ["attack", "skill", "ability", "curse"]

FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def font(size):
    for name in ("msyh.ttc", "simhei.ttf"):
        p = os.path.join(FONTS_DIR, name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("no CJK font")


def s(v):
    """设计坐标(480×640) → 画布坐标(2x，取整供 PIL)。"""
    return int(round(v * S))


def new_card():
    im = Image.new("RGB", (W * S, H * S), FACE)
    return im, ImageDraw.Draw(im)


def layer_ring(d, tk):
    """L1 描边环层：与 roundify_card.compose_card 同源同参。"""
    off = 0
    for col, wd in RING_PALETTES[tk]:
        d.rounded_rectangle([s(off), s(off), s(W - 1 - off), s(H - 1 - off)],
                            s(max(60 - off, 6)), fill=col)
        off += wd
    d.rounded_rectangle([s(off), s(off), s(W - 1 - off), s(H - 1 - off)],
                        s(60 - off), fill=FACE)


def arch(d, x0, y_top, x1, y_bot, fill):
    """圆拱形（半圆拱顶+矩形身），同心内缩由调用方控制 bbox。"""
    r = (x1 - x0) // 2
    d.ellipse([s(x0), s(y_top), s(x1), s(y_top + 2 * r)], fill=fill)
    d.rectangle([s(x0), s(y_top + r), s(x1), s(y_bot)], fill=fill)


def moon(d, cx, cy, r, fill):
    d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=fill)


def star(d, cx, cy, r, fill=GOLD):
    """四角星（长轴竖向）。"""
    k = r * 0.32
    d.polygon([(s(cx), s(cy - r)), (s(cx + k), s(cy - k)), (s(cx + r), s(cy)),
               (s(cx + k), s(cy + k)), (s(cx), s(cy + r)), (s(cx - k), s(cy + k)),
               (s(cx - r), s(cy)), (s(cx - k), s(cy - k))], fill=fill)


def diamond(d, cx, cy, r, fill=GOLD):
    d.polygon([(s(cx), s(cy - r)), (s(cx + r), s(cy)), (s(cx), s(cy + r)),
               (s(cx - r), s(cy))], fill=fill)


# ---- 方向 A「简柱面板」：圆拱窗 + 类型色细柱 + 奶油面板金键线 ----
def direction_a(tk):
    t = TYPES[tk]
    im, d = new_card()
    layer_ring(d, tk)
    # L3 窗体层：同心三层（墨线→金饰→净底）
    arch(d, 106, 46, 374, 434, INK)
    arch(d, 109, 49, 371, 434, GOLD)
    arch(d, 115, 55, 365, 434, t["win"])
    # L4 饰件层：拱顶金星 + 两侧类型色细柱（墨线+高光）
    star(d, 240, 46, 13)
    for cx in (78, 402):
        d.rounded_rectangle([s(cx - 12), s(168), s(cx + 12), s(450)], s(10),
                            fill=t["dark"], outline=INK, width=s(1.5))
        d.rounded_rectangle([s(cx - 6), s(174), s(cx - 1), s(444)], s(3), fill=t["light"])
        d.ellipse([s(cx - 16), s(154), s(cx + 16), s(172)], fill=GOLD, outline=INK, width=s(1.5))
        d.ellipse([s(cx - 16), s(446), s(cx + 16), s(464)], fill=GOLD, outline=INK, width=s(1.5))
    # L5 效果区层：面板 + 金键线 + 角部金菱
    d.rounded_rectangle([s(38), s(468), s(442), s(606)], s(16),
                        fill=PANEL, outline=GOLD, width=s(2))
    diamond(d, 58, 484, 6)
    diamond(d, 422, 484, 6)
    return im


# ---- 方向 B「徽带宽窗」：无柱大拱窗 + 顶部类型徽带 + 金线规开放式效果区 ----
def direction_b(tk):
    t = TYPES[tk]
    im, d = new_card()
    layer_ring(d, tk)
    # L4 饰件层（先画徽带）：类型色圆角徽带 + 中央金星
    d.rounded_rectangle([s(84), s(58), s(396), s(96)], s(19),
                        fill=t["light"], outline=INK, width=s(1.5))
    d.rounded_rectangle([s(92), s(64), s(388), s(90)], s(13),
                        outline=GOLD, width=s(1.5))
    star(d, 240, 77, 12)
    for x in (104, 376):
        d.ellipse([s(x - 4), s(73), s(x + 4), s(81)], fill=GOLD)
    # L3 窗体层：宽拱窗（徽带之下直抵窗台）
    arch(d, 72, 112, 408, 452, INK)
    arch(d, 75, 115, 405, 452, GOLD)
    arch(d, 81, 121, 399, 452, t["win"])
    star(d, 240, 112, 11)
    # L5 效果区层：开放式——双金线规 + 端点类型色珠
    for y in (478, 486):
        d.line([s(52), s(y), s(428), s(y)], fill=GOLD, width=s(2))
    for x in (52, 428):
        d.ellipse([s(x - 6), s(476), s(x + 6), s(488)], fill=t["light"], outline=INK, width=s(1))
    return im


# ---- 方向 C「月洞窗」：圆形月洞窗双金环 + 角部扇饰 + 类型色顶栏面板 ----
def direction_c(tk):
    t = TYPES[tk]
    im, d = new_card()
    layer_ring(d, tk)
    # L4 饰件层（先画角扇，窗体压其上）：左上/右上四分之一扇，朝卡内张开
    for cx, a0, a1 in ((52, 0, 90), (428, 90, 180)):
        d.pieslice([s(cx - 58), s(52 - 58), s(cx + 58), s(52 + 58)], a0, a1,
                   fill=t["win"], outline=GOLD, width=s(2))
    # L3 窗体层：月洞窗（整圆与窗台相切）+ 双金环
    moon(d, 240, 272, 176, INK)
    moon(d, 240, 272, 173, GOLD)
    moon(d, 240, 272, 167, GOLD_DK)
    moon(d, 240, 272, 164, t["win"])
    star(d, 240, 96, 12)
    # L5 效果区层：面板 + 类型色顶栏 + 金键线
    d.rounded_rectangle([s(36), s(460), s(444), s(606)], s(16),
                        fill=PANEL, outline=GOLD, width=s(2))
    d.rounded_rectangle([s(36), s(460), s(444), s(474)], s(7), fill=t["light"])
    d.rectangle([s(36), s(468), s(444), s(474)], fill=t["light"])
    return im


def finish(im):
    im = im.resize((W, H), Image.LANCZOS)
    a = Image.new("L", im.size, 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, W - 1, H - 1], 28, fill=255)
    im.putalpha(a)
    return im


def sheet(dirs, out):
    """四类型横排拼图（240×320/张 + 类型标签）。"""
    cw, ch, gap = 240, 320, 18
    img = Image.new("RGBA", (cw * 4 + gap * 5, ch + gap * 2 + 34), (242, 235, 217, 255))
    d = ImageDraw.Draw(img)
    f = font(18)
    for i, tkey in enumerate(ORDER):
        x = gap + i * (cw + gap)
        card = dirs[tkey].resize((cw, ch), Image.LANCZOS)
        img.paste(card, (x, gap), card)
        d.text((x + cw // 2 - d.textlength(TYPES[tkey]["label"], font=f) / 2,
                gap + ch + 8), TYPES[tkey]["label"], font=f, fill=INK)
    img.save(out)


def main():
    out = os.path.join("ImageReview", "cardframes")
    os.makedirs(out, exist_ok=True)
    gens = {"a": direction_a, "b": direction_b, "c": direction_c}
    for key, gen in gens.items():
        cards = {tk: finish(gen(tk)) for tk in ORDER}
        for tk, im in cards.items():
            im.save(os.path.join(out, f"frame_sketch_{key}_{tk}.png"))
        sheet(cards, os.path.join(out, f"frame_sketch_{key}_sheet.png"))
        print(f"direction {key}: 4 cards + sheet -> {out}")


if __name__ == "__main__":
    main()
