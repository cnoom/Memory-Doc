#!/usr/bin/env python3
"""卡框设计稿合成器 v3——《记忆勇者》整卡 480×640 视觉方案 mockup。

v3 修订（用户反馈：布局 OK，但 PIL 手绘框体"简陋、不简约"）：
  - 框体与卡背改由 AI 绘制（与插画同风格体系），存 ImageReview/cards/frame_*.png
    与 cardback_universal.png；本脚本只负责把插画窗 + 文字元素按定稿布局合成上去
  - 布局沿用 v2（插画主导 432×320、铭牌压插画、配对大数字徽章、词条胶囊）
  - AI 源图 1024×1536（2:3）居中裁到 3:4 后缩放 480×640

用法（仓库根目录，先生成 frame_*.png / cardback_universal.png）：
    python .agents/skills/mh-art/scripts/card_frame_mockup.py
输出：ImageReview/cards/cardframe_{attack,skill,ability,curse,back}.png
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 480, 640
INK = (59, 50, 38, 255)            # #3B3226 深可可
BODY = (248, 242, 227, 255)        # #F8F2E3 亮纸（铭牌底）
PANEL = (239, 231, 210, 255)       # #EFE7D2 胶囊底
GOLD = (212, 168, 87, 255)         # #D4A857 古金
GREEN = (91, 168, 91, 255)         # #5BA85B 匹配型词条
GREY = (136, 136, 136, 255)        # 移除词条
WHITE = (255, 255, 255, 255)

TYPES = {
    "attack":  dict(dark=(139, 44, 44),  light=(212, 69, 69),  label="攻击"),
    "skill":   dict(dark=(44, 74, 139),  light=(69, 119, 212), label="技能"),
    "ability": dict(dark=(91, 44, 139),  light=(155, 69, 212), label="能力"),
    "curse":   dict(dark=(26, 26, 26),   light=(58, 42, 58),   label="诅咒"),
}
RARITY = {"普通": (176, 176, 176), "罕见": (74, 156, 212), "稀有": (212, 168, 87)}

FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")


def font(size, bold=False):
    for name in (["msyhbd.ttc", "msyh.ttc"] if bold else ["msyh.ttc", "simhei.ttf"]):
        path = os.path.join(FONTS_DIR, name)
        if os.path.isfile(path):
            return ImageFont.truetype(path, size)
    sys.exit("no CJK font found in " + FONTS_DIR)


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


def load_base(raw_path):
    """AI 框体源图（1024×1536，2:3）→ 居中裁 3:4 → 480×640。"""
    art = Image.open(raw_path).convert("RGBA")
    src_w, src_h = art.size
    target_h = int(src_w * 4 / 3)
    if src_h > target_h:
        top = (src_h - target_h) // 2
        art = art.crop((0, top, src_w, top + target_h))
    return art.resize((W, H), Image.LANCZOS)


def paste_art(card, art_path, box):
    """插画居中偏上裁切铺满插画窗；无插画时绘制诅咒占位骷髅。"""
    x0, y0, x1, y1 = box
    win_w, win_h = x1 - x0, y1 - y0
    if art_path and os.path.isfile(art_path):
        art = Image.open(art_path).convert("RGBA")
        src_w, src_h = art.size
        crop_h = int(src_w * win_h / win_w)
        top = int((src_h - crop_h) * 0.45)
        art = art.crop((0, top, src_w, top + crop_h)).resize((win_w, win_h), Image.LANCZOS)
    else:
        art = Image.new("RGBA", (win_w, win_h))
        d = ImageDraw.Draw(art)
        for y in range(win_h):
            t = y / win_h
            color = tuple(int(a + (b - a) * t) for a, b in zip((42, 26, 42), (10, 10, 10)))
            d.line([(0, y), (win_w, y)], fill=color + (255,))
        cx, cy = win_w // 2, win_h // 2 - 10
        d.ellipse([cx - 46, cy - 50, cx + 46, cy + 42], fill=(232, 224, 232, 255), outline=INK, width=3)
        d.rectangle([cx - 26, cy - 22, cx - 8, cy - 2], fill=(42, 26, 42, 255))
        d.rectangle([cx + 8, cy - 22, cx + 26, cy - 2], fill=(42, 26, 42, 255))
        d.polygon([(cx, cy + 4), (cx - 7, cy + 20), (cx + 7, cy + 20)], fill=(42, 26, 42, 255))
        for i in range(4):
            tx = cx - 24 + i * 16
            d.rectangle([tx, cy + 34, tx + 10, cy + 52], fill=(232, 224, 232, 255), outline=INK, width=2)
    mask = Image.new("L", (win_w, win_h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, win_w - 1, win_h - 1], 14, fill=255)
    card.paste(art, (x0, y0), mask)


def chip(d, x, y, text, bg, fg=WHITE, fnt=None, pad_x=12, h=28):
    bg = tuple(bg) if len(bg) == 4 else tuple(bg) + (255,)
    fnt = fnt or font(14, bold=True)
    tw = d.textlength(text, font=fnt)
    d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + h], h // 2, fill=bg, outline=INK, width=1)
    d.text((x + pad_x, y + (h - fnt.size) // 2 - 1), text, font=fnt, fill=fg)
    return x + tw + pad_x * 2


def nameplate(d, name, rarity_color, y=330):
    fnt = font(24, bold=True)
    tw = d.textlength(name, font=fnt)
    x0 = (W - tw) // 2 - 20
    d.rounded_rectangle([x0, y, x0 + tw + 40, y + 42], 21, fill=BODY, outline=INK, width=2)
    d.text(((W - tw) // 2, y + 7), name, font=fnt, fill=rarity_color)


def type_badge(d, t):
    chip(d, 378, 86, t["label"], t["light"], h=30)


def number_badge(d, cx, cy, number, color):
    r = 22
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,), outline=INK, width=2)
    fnt = font(26, bold=True)
    tw = d.textlength(str(number), font=fnt)
    d.text((cx - tw / 2, cy - 19), str(number), font=fnt, fill=WHITE)


def tag_chips(d, tags, y):
    x = 24
    for keyword, color in tags:
        fnt = font(14, bold=True)
        tw = d.textlength(keyword, font=fnt)
        w = tw + 34
        if x + w > 456:
            x, y = 24, y + 36
        d.rounded_rectangle([x, y, x + w, y + 28], 14, fill=PANEL, outline=INK, width=1)
        d.ellipse([x + 10, y + 9, x + 22, y + 21], fill=color, outline=INK, width=1)
        d.text((x + 26, y + 5), keyword, font=fnt, fill=color)
        x += w + 8
    return y


def effect_rows(d, t, y, pair, flip):
    """配对效果（标签+数字徽章+单位）与翻开效果（标签+短句）。"""
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
        y += 32 + (len(lines[:2]) - 1) * 24 + 14
    return y


def make_standard(type_key, frame_path, name, rarity, art_path, pair, flip, tags):
    t, rc = TYPES[type_key], RARITY[rarity]
    card = load_base(frame_path)
    d = ImageDraw.Draw(card)
    paste_art(card, art_path, (24, 30, 456, 350))
    d.rounded_rectangle([24, 30, 456, 350], 14, outline=INK, width=2)
    type_badge(d, t)
    nameplate(d, name, rc, y=330)
    y = effect_rows(d, t, 398, pair, flip)
    tag_chips(d, tags, max(y, 520))
    d.rounded_rectangle([40, 606, 440, 612], 3, fill=rc)
    return card


def make_ability(frame_path, name, rarity, art_path, sustain_lines, flip, tags):
    t, rc = TYPES["ability"], RARITY[rarity]
    card = load_base(frame_path)
    d = ImageDraw.Draw(card)
    paste_art(card, art_path, (24, 30, 456, 300))
    d.rounded_rectangle([24, 30, 456, 300], 14, outline=INK, width=2)
    type_badge(d, t)
    nameplate(d, name, rc, y=280)
    text_fnt = font(15)
    chip(d, 24, 342, "◆ 持续（背面在桌面时）", t["light"], h=30)
    y = 380
    for ln in sustain_lines[:2]:
        d.text((24, y), ln, font=text_fnt, fill=INK)
        y += 24
    x = chip(d, 24, y + 12, "↻ 翻开", GOLD, h=30)
    d.text((x + 12, y + 16), flip, font=text_fnt, fill=INK)
    tag_chips(d, tags, 548)
    d.rounded_rectangle([40, 606, 440, 612], 3, fill=rc)
    return card


def main():
    out = os.path.join("ImageReview", "cards")

    make_standard(
        "attack", os.path.join(out, "frame_attack.png"),
        "笔记", "普通", os.path.join(out, "card_attack_biji_1.png"),
        pair=("atk", 6, "伤害"), flip=None,
        tags=[("[笔记]", GREEN)],
    ).save(os.path.join(out, "cardframe_attack.png"))

    make_standard(
        "skill", os.path.join(out, "frame_skill.png"),
        "速读", "普通", os.path.join(out, "card_skill_sudu_1.png"),
        pair=("block", 4, "格挡"), flip="随机揭示周围 1 张背面牌",
        tags=[("[翻开]", GOLD)],
    ).save(os.path.join(out, "cardframe_skill.png"))

    make_ability(
        os.path.join(out, "frame_ability.png"),
        "全神贯注", "普通", os.path.join(out, "card_ability_quanshenguanzhu_1.png"),
        ["每翻开一张牌，获得 1 点「专注」", "专注：下次配对伤害 +1，触发后消耗"],
        flip="获得 2 点格挡",
        tags=[("[翻开]", GOLD)],
    ).save(os.path.join(out, "cardframe_ability.png"))

    make_standard(
        "curse", os.path.join(out, "frame_curse.png"),
        "遗忘", "普通", None,
        pair=None, flip="失去 2 点血量；移除自身",
        tags=[("[翻开]", GOLD), ("[移除]", GREY)],
    ).save(os.path.join(out, "cardframe_curse.png"))

    load_base(os.path.join(out, "cardback_universal.png")).save(
        os.path.join(out, "cardframe_back.png"))

    print("Saved: cardframe_attack / skill / ability / curse / back ->", out)


if __name__ == "__main__":
    main()
