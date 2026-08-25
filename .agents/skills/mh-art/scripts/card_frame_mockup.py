#!/usr/bin/env python3
"""卡框设计稿合成器——《记忆勇者》整卡 480×640 视觉方案 mockup。

用途：把"卡框（UI 层实现）+ 卡面插画（AI 资产）+ 真实文案"合成为整卡效果图，
供设计文档 10 §2.2/§4.3 卡框方案的人工拍板。本脚本只做设计稿预览，
正式 9-slice 边框资产（border_card_*.png）在方案定稿后另行切制。

设计要点（v3.2 风格基线）：
  - 480×640，外圆角 24px，3px 深可可描边（#3B3226）——与角色细描边一致的"贴纸感"
  - 类型色边带：主色 8px 环 + 亮色 2px 内衬线 + 四角古金圆点
  - 卡体奶油纸 #F8F2E3（诅咒偏灰紫），文案面板 #EFE7D2
  - 插画窗 400×240 圆角 12，亮类型色 2px 窗框，插画居中偏上裁切
  - 卡名用稀有度色（§1.3），底部稀有度色条
  - 能力牌双面板（§2.4：◆持续 紫 / ↻翻开 金）；诅咒牌无效果面板、占位骷髅插画

用法（仓库根目录）：
    python .agents/skills/mh-art/scripts/card_frame_mockup.py
输出：ImageReview/cards/cardframe_{attack,skill,ability,curse}.png
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 480, 640
RADIUS = 24
INK = (59, 50, 38, 255)            # #3B3226 深可可
BODY = (248, 242, 227, 255)        # #F8F2E3 亮纸卡体
BODY_CURSE = (233, 228, 233, 255)  # 诅咒卡体（偏灰紫）
PANEL = (239, 231, 210, 255)       # #EFE7D2 文案面板
GOLD = (212, 168, 87, 255)         # #D4A857 古金
GREEN = (91, 168, 91, 255)         # #5BA85B 匹配型词条色
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
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, win_w - 1, win_h - 1], 12, fill=255)
    card.paste(art, (x0, y0), mask)


def draw_frame(card, t, body):
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, W - 1, H - 1], RADIUS, fill=body, outline=INK, width=3)
    d.rounded_rectangle([6, 6, W - 7, H - 7], RADIUS - 5, outline=t["dark"] + (255,), width=8)
    d.rounded_rectangle([15, 15, W - 16, H - 16], RADIUS - 9, outline=t["light"] + (255,), width=2)
    for cx, cy in [(24, 24), (W - 24, 24), (24, H - 24), (W - 24, H - 24)]:
        d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD, outline=INK, width=1)


def draw_title(d, t, name, rarity_color):
    d.text((40, 26), name, font=font(27, bold=True), fill=rarity_color)
    fnt = font(17, bold=True)
    tw = d.textlength(t["label"], font=fnt)
    x0, y0, x1, y1 = 440 - tw - 26, 26, 440, 56
    d.rounded_rectangle([x0, y0, x1, y1], 15, fill=t["light"] + (255,), outline=INK, width=1)
    d.text((x0 + 13, y0 + 5), t["label"], font=fnt, fill=WHITE)


def draw_text_panel(d, box, lines, label=None, label_color=None):
    x0, y0, x1, y1 = box
    d.rounded_rectangle([x0, y0, x1, y1], 12, fill=PANEL, outline=INK, width=1)
    y = y0 + 12
    if label:
        d.text((x0 + 16, y), label, font=font(14, bold=True), fill=label_color)
        y += 24
    fnt = font(16)
    for text in lines:
        d.text((x0 + 16, y), text, font=fnt, fill=INK)
        y += fnt.size + 10


def draw_tags(d, tag_lines, y=478):
    tag_fnt, kw_fnt = font(15), font(15, bold=True)
    for keyword, kw_color, desc in tag_lines:
        d.ellipse([40, y + 7, 48, y + 15], fill=kw_color, outline=INK, width=1)
        x = 56
        d.text((x, y), keyword, font=kw_fnt, fill=kw_color)
        x += d.textlength(keyword, font=kw_fnt) + 6
        first = True
        for ln in wrap(d, desc, tag_fnt, 440 - x):
            d.text((x if first else 56, y), ln, font=tag_fnt, fill=INK)
            first = False
            y += 24
        y += 10


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


def draw_rarity_bar(d, rarity_color):
    d.rounded_rectangle([40, 606, 440, 612], 3, fill=rarity_color)


def make_standard(type_key, name, rarity, art_path, effect_lines, tag_lines):
    t, rc = TYPES[type_key], RARITY[rarity]
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_frame(card, t, BODY_CURSE if type_key == "curse" else BODY)
    d = ImageDraw.Draw(card)
    draw_title(d, t, name, rc)
    paste_art(card, art_path, (40, 88, 440, 328))
    d.rounded_rectangle([40, 88, 440, 328], 12, outline=t["light"] + (255,), width=2)
    if effect_lines:
        draw_text_panel(d, (24, 344, 456, 344 + len(effect_lines) * 26 + 28), effect_lines)
    draw_tags(d, tag_lines)
    draw_rarity_bar(d, rc)
    return card


def make_ability(name, rarity, art_path, sustain_lines, flip_lines):
    t, rc = TYPES["ability"], RARITY[rarity]
    card = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_frame(card, t, BODY)
    d = ImageDraw.Draw(card)
    draw_title(d, t, name, rc)
    paste_art(card, art_path, (40, 88, 440, 288))
    d.rounded_rectangle([40, 88, 440, 288], 12, outline=t["light"] + (255,), width=2)
    draw_text_panel(d, (24, 302, 456, 302 + 24 + len(sustain_lines) * 26 + 22),
                    sustain_lines, label="◆ 持续效果（此牌背面在桌面时）", label_color=t["light"])
    draw_text_panel(d, (24, 434, 456, 434 + 24 + len(flip_lines) * 26 + 22),
                    flip_lines, label="↻ 翻开效果", label_color=GOLD)
    draw_rarity_bar(d, rc)
    return card


def main():
    out_dir = os.path.join("ImageReview", "cards")
    cards = os.path.join(out_dir)

    make_standard(
        "attack", "笔记", "普通", os.path.join(cards, "card_attack_biji_1.png"),
        ["配对：造成 6 点伤害"],
        [("[笔记]", GREEN, "匹配型——可与笔记、读书笔记互相配对")],
    ).save(os.path.join(out_dir, "cardframe_attack.png"))

    make_standard(
        "skill", "速读", "普通", os.path.join(cards, "card_skill_sudu_1.png"),
        ["配对：获得 4 点格挡"],
        [("[翻开]", GOLD, "随机揭示周围 1 张背面牌")],
    ).save(os.path.join(out_dir, "cardframe_skill.png"))

    make_ability(
        "全神贯注", "普通", os.path.join(cards, "card_ability_quanshenguanzhu_1.png"),
        ["每翻开一张牌，获得 1 点「专注」",
         "专注：下次配对伤害 +1，触发后消耗 1 层"],
        ["获得 2 点格挡"],
    ).save(os.path.join(out_dir, "cardframe_ability.png"))

    make_standard(
        "curse", "遗忘", "普通", None,
        [],
        [("[翻开]", GOLD, "失去 2 点血量；移除自身"),
         ("[移除]", (136, 136, 136, 255), "进入弃牌堆时改为从游戏移除")],
    ).save(os.path.join(out_dir, "cardframe_curse.png"))

    print("Saved: cardframe_attack / skill / ability / curse ->", out_dir)


if __name__ == "__main__":
    main()
