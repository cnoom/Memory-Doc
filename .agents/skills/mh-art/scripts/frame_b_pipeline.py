#!/usr/bin/env python3
"""方向 B「徽带宽窗」正式管线——《记忆勇者》卡框程序化生成（v1.17 候选）。

用户拍板（2026-08-30）：B 方向，顶部类型色徽带 = 卡名铭牌位。
与 AI 整图管线（roundify_card --compose-type）并行的**全程序分层管线**：
  L1 描边环  RING_PALETTES（与 roundify_card 同源，四类型绝对等粗色准）
  L2 卡面    奶油纸平色
  L3 窗体    宽拱窗（墨线→金饰→净底同心三层）
  L4 饰件    拱顶金星 + 窗台双金线规 + 端点类型色珠
  L5 铭牌    顶部类型色徽带（**卡名由引擎 TMP 渲染，不烘焙**）
四类型共用同一套几何参数，仅类型色板不同——零漂移。

窗区镂空：洞=拱窗净底区（程序几何直接定义，无需检测），alpha=0 + 1.2px
羽化；引擎/效果图按 alpha<200 读窗形，插画 cover 等比裁贴。

输出（预览区，用户拍板后 --publish 进 Assets/UI/cardframes/）：
  ImageReview/cardframes/border_card_{type}_b.png   960×1280 发布资产
  ImageReview/cards/cardframe_b_{type}.png          480×640 整卡效果图

用法（仓库根目录）：
    python .agents/skills/mh-art/scripts/frame_b_pipeline.py
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from roundify_card import RING_PALETTES

# ---- 设计坐标系 480×640，绘制 4x 超采样 → 发布 960×1280 ----
S = 4
W, H = 480, 640
GOLD = (212, 168, 87)
INK = (59, 50, 38)
FACE = (249, 234, 206)

TYPES = {
    "attack":  dict(label="攻击", dark=(139, 44, 44), light=(212, 69, 69),
                    win=(217, 238, 225), base=(223, 215, 223)),
    "skill":   dict(label="技能", dark=(44, 74, 139), light=(69, 119, 212),
                    win=(219, 233, 243), base=(223, 215, 223)),
    "ability": dict(label="能力", dark=(91, 44, 139), light=(155, 69, 212),
                    win=(230, 224, 242), base=(223, 215, 223)),
    "curse":   dict(label="诅咒", dark=(58, 42, 58), light=(58, 42, 58),
                    win=(229, 223, 231), base=(229, 223, 231)),
}
ORDER = ["attack", "skill", "ability", "curse"]

# 几何参数（480×640 设计值；徽带=卡名位，文字引擎渲染）
BAND = (84, 58, 396, 96)            # 卡名徽带（L5）
WIN = dict(x0=72, top=112, x1=408, bot=452)   # 宽拱窗（L3）
STAR = (240, 112, 11)               # 拱顶金星（L4）
RULE_YS = (478, 486)                # 窗台双金线规（L4）
RULE_X = (52, 428)
PAIR_Y = 496                        # 效果区行（480×640，金线规之下）
RARITY_Y = 614                # 稀有度条（环内缘 y=627 之上）
ABILITY_SUSTAIN_Y = 494
ABILITY_FLIP_Y = 552
ABILITY_TAG_Y = 582

FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def font(size, bold=False):
    for name in (["msyhbd.ttc", "msyh.ttc"] if bold else ["msyh.ttc", "simhei.ttf"]):
        p = os.path.join(FONTS_DIR, name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    raise SystemExit("no CJK font")


def s(v):
    return int(round(v * S))


def arch_points(win, inset=0):
    """圆拱窗 bbox（同心内缩 inset），返回 (x0, y_top, x1, y_bot, spring, r)。"""
    x0, top, x1, bot = win["x0"] + inset, win["top"] + inset, win["x1"] - inset, win["bot"]
    r = (x1 - x0) // 2
    return x0, top, x1, bot, top + r, r


def draw_arch(d, win, inset, fill):
    x0, top, x1, bot, spring, r = arch_points(win, inset)
    d.ellipse([s(x0), s(top), s(x1), s(top + 2 * r)], fill=fill)
    d.rectangle([s(x0), s(spring), s(x1), s(bot)], fill=fill)


def star(d, cx, cy, r, fill=GOLD):
    k = r * 0.32
    d.polygon([(s(cx), s(cy - r)), (s(cx + k), s(cy - k)), (s(cx + r), s(cy)),
               (s(cx + k), s(cy + k)), (s(cx), s(cy + r)), (s(cx - k), s(cy + k)),
               (s(cx - r), s(cy)), (s(cx - k), s(cy - k))], fill=fill)


def build_frame(tk):
    """发布资产 960×1280：五层程序绘制 + 拱窗 alpha 镂空。

    描边环 26px 为**源尺度规格**（v1.15 锁定）——色标宽度在 960 画布上
    原样落（非随画布缩放），环半径 60 与圆角 alpha（60）同心。
    """
    t = TYPES[tk]
    im = Image.new("RGB", (W * S, H * S), FACE)
    d = ImageDraw.Draw(im)
    PW, PH = W * S // 2, H * S // 2          # 发布尺度 960×1280
    # L1 描边环（同源 RING_PALETTES；2x=发布尺度坐标）
    off = 0
    for col, wd in RING_PALETTES[tk]:
        d.rounded_rectangle([2 * off, 2 * off, 2 * (PW - 1 - off), 2 * (PH - 1 - off)],
                            2 * max(60 - off, 6), fill=col)
        off += wd
    d.rounded_rectangle([2 * off, 2 * off, 2 * (PW - 1 - off), 2 * (PH - 1 - off)],
                        2 * (60 - off), fill=FACE)
    # L3 窗体：墨线 → 金饰 → 净底（净底随后被镂空，仅为调试可视）
    draw_arch(d, WIN, 0, INK)
    draw_arch(d, WIN, 3, GOLD)
    draw_arch(d, WIN, 9, t["win"])
    # L4 饰件：拱顶金星 + 窗台双金线规 + 端点类型色珠
    star(d, *STAR)
    for y in RULE_YS:
        d.line([s(RULE_X[0]), s(y), s(RULE_X[1]), s(y)], fill=GOLD, width=s(2))
    for x in RULE_X:
        d.ellipse([s(x - 6), s(RULE_YS[0] - 2), s(x + 6), s(RULE_YS[0] + 10)],
                  fill=t["light"], outline=INK, width=s(1))
    # L5 卡名徽带（几何；文字引擎渲染）
    d.rounded_rectangle([s(BAND[0]), s(BAND[1]), s(BAND[2]), s(BAND[3])], s(19),
                        fill=t["light"], outline=INK, width=s(1.5))

    im = im.resize((W * S // 2, H * S // 2), Image.LANCZOS)   # → 960×1280
    # alpha = 圆角卡形 − 拱窗洞（洞=净底区 inset 9，1.2px 羽化过渡）
    k = S // 2
    m = Image.new("L", im.size, 0)
    dm = ImageDraw.Draw(m)
    x0, top, x1, bot, spring, r = arch_points(WIN, 9)
    dm.ellipse([x0 * k, top * k, x1 * k, (top + 2 * r) * k], fill=255)
    dm.rectangle([x0 * k, spring * k, x1 * k, bot * k], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(1.2))
    a = Image.new("L", im.size, 0)
    ImageDraw.Draw(a).rounded_rectangle([0, 0, im.width - 1, im.height - 1], 60, fill=255)
    from PIL import ImageChops
    im.putalpha(ImageChops.multiply(a, m.point(lambda v: 255 - v)))
    return im.convert("RGBA")


# ---- 整卡效果图（480×640）----
INK_TXT = (59, 50, 38, 255)
PANEL = (239, 231, 210, 255)
GOLD_A = (212, 168, 87, 255)
GREEN = (91, 168, 91, 255)
GREY = (136, 136, 136, 255)
WHITE = (255, 255, 255, 255)


def wrap(d, text, fnt, max_w):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=fnt) <= max_w:
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def chip(d, x, y, text, bg, fg=WHITE, fnt=None, pad_x=12, h=28):
    bg = tuple(bg) if len(bg) == 4 else tuple(bg) + (255,)
    fnt = fnt or font(14, bold=True)
    tw = d.textlength(text, font=fnt)
    d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + h], h // 2, fill=bg, outline=INK, width=1)
    d.text((x + pad_x, y + (h - fnt.size) // 2 - 1), text, font=fnt, fill=fg)
    return x + tw + pad_x * 2


def number_badge(d, cx, cy, number, color):
    r = 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,), outline=INK, width=2)
    fnt = font(26, bold=True)
    tw = d.textlength(str(number), font=fnt)
    d.text((cx - tw / 2, cy - 19), str(number), font=fnt, fill=WHITE)


def paste_art(card, art_path, curse_base=None):
    """插画 cover 等比裁贴进 alpha 洞；无插画画净底+（诅咒）骷髅占位。"""
    a = card.getchannel("A")
    mask = Image.fromarray(((np_alpha(a)) < 200).astype("uint8") * 255, "L")
    bb = mask.getbbox()
    win_w, win_h = bb[2] - bb[0], bb[3] - bb[1]
    if art_path and os.path.isfile(art_path):
        art = Image.open(art_path).convert("RGBA")
        sw, sh = art.size
        if sw * win_h > sh * win_w:
            cw = int(sh * win_w / win_h)
            art = art.crop(((sw - cw) // 2, 0, (sw - cw) // 2 + cw, sh))
        else:
            ch = int(sw * win_h / win_w)
            top = int((sh - ch) * 0.45)
            art = art.crop((0, top, sw, top + ch))
        art = art.resize((win_w, win_h), Image.LANCZOS)
    elif curse_base is not None:
        art = Image.new("RGBA", (win_w, win_h), tuple(curse_base) + (255,))
        dd = ImageDraw.Draw(art)
        cx, cy = win_w // 2, win_h // 2 - 10
        dd.ellipse([cx - 46, cy - 50, cx + 46, cy + 42], fill=INK)
        dd.rectangle([cx - 26, cy - 22, cx - 8, cy - 2], fill=(226, 218, 228, 255))
        dd.rectangle([cx + 8, cy - 22, cx + 26, cy - 2], fill=(226, 218, 228, 255))
        dd.polygon([(cx, cy + 4), (cx - 7, cy + 20), (cx + 7, cy + 20)], fill=(226, 218, 228, 255))
        for i in range(4):
            dd.rectangle([cx - 24 + i * 16, cy + 34, cx - 24 + i * 16 + 10, cy + 52], fill=INK)
    else:
        art = Image.new("RGBA", (win_w, win_h), (0, 0, 0, 0))
    card.paste(art, (bb[0], bb[1]), mask.crop(bb))


def np_alpha(a):
    import numpy as np
    return np.asarray(a)


def name_on_band(d, name, rarity_color):
    """卡名渲在徽带中央（白字+墨描边；正式版由引擎 TMP 按稀有度色渲染）。"""
    fnt = font(22, bold=True)
    tw = d.textlength(name, font=fnt)
    cx, cy = (BAND[0] + BAND[2]) / 2, (BAND[1] + BAND[3]) / 2
    d.text((cx - tw / 2, cy - fnt.size / 2 - 1), name, font=fnt, fill=(255, 255, 255, 255),
           stroke_width=2, stroke_fill=INK)


def tag_chips(d, tags, y):
    x = 24
    for keyword, color in tags:
        fnt = font(14, bold=True)
        tw = d.textlength(keyword, font=fnt)
        w = tw + 34
        if x + w > 456:
            x, y = 24, y + 34
        d.rounded_rectangle([x, y, x + w, y + 28], 14, fill=PANEL, outline=INK, width=1)
        d.ellipse([x + 10, y + 9, x + 22, y + 21], fill=color, outline=INK, width=1)
        d.text((x + 26, y + 5), keyword, font=fnt, fill=color)
        x += w + 8
    return y


def effect_rows(d, t, y, pair, flip):
    text_fnt = font(16)
    if pair:
        kind, value, unit = pair
        x = chip(d, 24, y, "配对", t["dark"], h=32)
        number_badge(d, x + 34, y + 16, value, t["light"])
        d.text((x + 64, y + 6), "点" + unit, font=text_fnt, fill=INK)
        y += 52
    if flip:
        x = chip(d, 24, y, "翻开", GOLD, h=32)
        lines = wrap(d, flip, text_fnt, 456 - (x + 12))
        for i, ln in enumerate(lines[:2]):
            d.text((x + 12, y + 5 + i * 24), ln, font=text_fnt, fill=INK)
        y += 32 + (len(lines[:2]) - 1) * 24 + 6
    return y


def round_corners(card, radius=28):
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, card.width - 1, card.height - 1], radius, fill=255)
    card.putalpha(mask)
    return card


def mockup(tk, frame_path, name, rarity_color, art_path, pair, flip, tags):
    t = TYPES[tk]
    card = Image.open(frame_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(card)
    paste_art(card, art_path, curse_base=t["base"] if tk == "curse" else None)
    name_on_band(d, name, rarity_color)
    y = effect_rows(d, t, PAIR_Y, pair, flip)
    tag_chips(d, tags, min(max(y, PAIR_Y + 78), 584))   # 底部让位稀有度条
    d.rounded_rectangle([40, RARITY_Y, 440, RARITY_Y + 6], 3, fill=rarity_color)
    return round_corners(card)


def mockup_ability(frame_path, name, rarity_color, art_path, sustain_lines, flip, tags):
    t = TYPES["ability"]
    card = Image.open(frame_path).convert("RGBA").resize((W, H), Image.LANCZOS)
    d = ImageDraw.Draw(card)
    paste_art(card, art_path)
    name_on_band(d, name, rarity_color)
    text_fnt = font(15)
    y = ABILITY_SUSTAIN_Y
    chip(d, 24, y, "◆ 持续（背面在桌面时）", t["light"], h=28)
    y += 30
    d.text((24, y), sustain_lines[0], font=text_fnt, fill=INK)
    y += 26
    x = chip(d, 24, y, "↻ 翻开", GOLD, h=30)
    d.text((x + 12, y + 4), flip, font=text_fnt, fill=INK)
    tag_chips(d, tags, ABILITY_TAG_Y)
    d.rounded_rectangle([40, RARITY_Y, 440, RARITY_Y + 6], 3, fill=rarity_color)
    return round_corners(card)


def main():
    out_frame = os.path.join("ImageReview", "cardframes")
    out_card = os.path.join("ImageReview", "cards")
    os.makedirs(out_frame, exist_ok=True)
    frames = {}
    for tk in ORDER:
        im = build_frame(tk)
        p = os.path.join(out_frame, f"border_card_{tk}_b.png")
        im.save(p)
        frames[tk] = p
        print("frame:", p, im.size)

    rar_n = (176, 176, 176)
    cards = {}
    cards["attack"] = mockup(
        "attack", frames["attack"], "笔记", rar_n,
        os.path.join(out_card, "card_attack_biji_1.png"),
        pair=("atk", 6, "伤害"), flip=None, tags=[("[笔记]", GREEN)])
    cards["skill"] = mockup(
        "skill", frames["skill"], "速读", rar_n,
        os.path.join(out_card, "card_skill_sudu_1.png"),
        pair=("block", 4, "格挡"), flip="随机揭示周围 1 张背面牌", tags=[("[翻开]", GOLD)])
    cards["ability"] = mockup_ability(
        frames["ability"], "全神贯注", rar_n,
        os.path.join(out_card, "card_ability_quanshenguanzhu_1.png"),
        ["每翻开一张牌，获得 1 点「专注」"],
        flip="获得 2 点格挡", tags=[("[翻开]", GOLD)])
    cards["curse"] = mockup(
        "curse", frames["curse"], "遗忘", rar_n, None,
        pair=None, flip="失去 2 点血量；移除自身", tags=[("[翻开]", GOLD), ("[移除]", GREY)])
    for tk, im in cards.items():
        p = os.path.join(out_card, f"cardframe_b_{tk}.png")
        im.save(p)
        print("mockup:", p)


if __name__ == "__main__":
    main()
