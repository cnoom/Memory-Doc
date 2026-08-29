#!/usr/bin/env python3
"""卡框设计稿合成器 v4——《记忆勇者》整卡 480×640 视觉方案 mockup。

v4 修订（2026-08-29，卡面卡框定稿为"记忆殿堂拱窗"方向）：
  - 框体换为四类型拱窗框 border_card_{attack,skill,ability,curse}.png：
    AI 绘制金拱饰 + 石柱 + 暗类型色边带，拱窗内为净色底
  - 本脚本自动从框图提取拱窗净底区域（颜色采样 + 逐行 span 填充 + 收缩），
    生成像素级拱形 mask，把插画裁贴进拱窗——不盖金拱线，适配 ogee 尖拱
  - 布局按拱窗底沿重排：铭牌压拱底、配对/翻开/词条/稀有度条下移进效果区
  - v3 及之前：矩形插画窗布局（git 历史可查）；框体与卡背仍由 AI 绘制

用法（仓库根目录）：
    python .agents/skills/mh-art/scripts/card_frame_mockup.py
输出：ImageReview/cards/cardframe_{attack,skill,ability,curse,back}.png
"""

import os
import sys

import numpy as np

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

# 拱窗净底采样点（480×640 拱窗中心）与 mask 容差/收缩
ARCH_SAMPLE = (W // 2, 270)
ARCH_TOL = 46
ARCH_SHRINK = 3
# 拱窗版效果区布局（y 坐标，480×640）——按 v1.5 拱窗框实测：
# 拱底沿/金线效果框顶 y≈465，金线效果框底 y≈617（attack 框实测，四框同款）
NAMEPLATE_Y = 443          # 卡名铭牌压拱底沿
PAIR_Y = 478               # 配对效果行（金框内）
FLIP_GAP = 6               # 翻开行与上一行间距
TAG_Y_FALLBACK = 568       # 词条行（金框内）
RARITY_Y = 602             # 稀有度条（金框内底部）
# 能力牌（元素多，整组上收）
ABILITY_NAMEPLATE_Y = 436
ABILITY_SUSTAIN_Y = 480
ABILITY_FLIP_Y = 542
ABILITY_TAG_Y = 574

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
    """AI 框体/卡背源图（1024×1536，2:3）→ 居中裁 3:4 → 480×640。"""
    art = Image.open(raw_path).convert("RGBA")
    src_w, src_h = art.size
    target_h = int(src_w * 4 / 3)
    if src_h > target_h:
        top = (src_h - target_h) // 2
        art = art.crop((0, top, src_w, top + target_h))
    return art.resize((W, H), Image.LANCZOS)



def window_mask(card):
    """镂空框的插画窗 mask：compose 挖洞区（alpha<200），即精确窗形。"""
    a = np.asarray(card.getchannel("A"))
    return Image.fromarray(((a < 200) * 255).astype("uint8"), "L")


def paste_arch_art(card, mask, art_path, curse=False, base_color=None):
    """插画按拱形 mask 贴入拱窗；诅咒牌无插画时画深底占位骷髅。"""
    bb = mask.getbbox()
    win_w, win_h = bb[2] - bb[0], bb[3] - bb[1]
    if art_path and os.path.isfile(art_path):
        art = Image.open(art_path).convert("RGBA")
        src_w, src_h = art.size
        crop_h = int(src_w * win_h / win_w)
        top = int((src_h - crop_h) * 0.45)
        art = art.crop((0, top, src_w, top + crop_h)).resize((win_w, win_h), Image.LANCZOS)
    elif curse:
        # 诅咒占位：不贴深色底（框图拱窗内缘有暗角，像素 mask 边界不规则会
        # 显锯齿）——底色用框图窗中心采样色原样平铺（与窗底无缝），仅画深
        # 可可骷髅剪影
        art = Image.new("RGBA", (win_w, win_h), tuple(base_color) + (255,))
        d = ImageDraw.Draw(art)
        cx, cy = win_w // 2, win_h // 2 - 10
        d.ellipse([cx - 46, cy - 50, cx + 46, cy + 42], fill=INK)
        d.rectangle([cx - 26, cy - 22, cx - 8, cy - 2], fill=(226, 218, 228, 255))
        d.rectangle([cx + 8, cy - 22, cx + 26, cy - 2], fill=(226, 218, 228, 255))
        d.polygon([(cx, cy + 4), (cx - 7, cy + 20), (cx + 7, cy + 20)], fill=(226, 218, 228, 255))
        for i in range(4):
            tx = cx - 24 + i * 16
            d.rectangle([tx, cy + 34, tx + 10, cy + 52], fill=INK)
    else:
        art = Image.new("RGBA", (win_w, win_h))
    card.paste(art, (bb[0], bb[1]), mask.crop(bb))


def chip(d, x, y, text, bg, fg=WHITE, fnt=None, pad_x=12, h=28):
    bg = tuple(bg) if len(bg) == 4 else tuple(bg) + (255,)
    fnt = fnt or font(14, bold=True)
    tw = d.textlength(text, font=fnt)
    d.rounded_rectangle([x, y, x + tw + pad_x * 2, y + h], h // 2, fill=bg, outline=INK, width=1)
    d.text((x + pad_x, y + (h - fnt.size) // 2 - 1), text, font=fnt, fill=fg)
    return x + tw + pad_x * 2


def nameplate(d, name, rarity_color, y=NAMEPLATE_Y):
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
        y += 32 + (len(lines[:2]) - 1) * 24 + FLIP_GAP
    return y


def make_standard(type_key, frame_path, name, rarity, art_path, pair, flip, tags):
    t, rc = TYPES[type_key], RARITY[rarity]
    card = load_base(frame_path)
    mask = window_mask(card)
    d = ImageDraw.Draw(card)
    paste_arch_art(card, mask, art_path, curse=(type_key == "curse"),
                   base_color=(223, 215, 223) if type_key == "curse" else None)
    type_badge(d, t)
    nameplate(d, name, rc)
    y = effect_rows(d, t, PAIR_Y, pair, flip)
    tag_chips(d, tags, max(y, TAG_Y_FALLBACK))
    d.rounded_rectangle([40, RARITY_Y, 440, RARITY_Y + 6], 3, fill=rc)
    return round_corners(card)


def make_ability(frame_path, name, rarity, art_path, sustain_lines, flip, tags):
    """能力牌：拱窗框下半排持续段+翻开段；持续文字压成 1 行保空间。"""
    t, rc = TYPES["ability"], RARITY[rarity]
    card = load_base(frame_path)
    mask = window_mask(card)
    d = ImageDraw.Draw(card)
    paste_arch_art(card, mask, art_path)
    type_badge(d, t)
    nameplate(d, name, rc, y=ABILITY_NAMEPLATE_Y)
    text_fnt = font(15)
    y = ABILITY_SUSTAIN_Y
    chip(d, 24, y, "◆ 持续（背面在桌面时）", t["light"], h=28)
    y += 32
    ln = sustain_lines[0]
    d.text((24, y), ln, font=text_fnt, fill=INK)
    y += 26
    x = chip(d, 24, y, "↻ 翻开", GOLD, h=30)
    d.text((x + 12, y + 4), flip, font=text_fnt, fill=INK)
    tag_chips(d, tags, ABILITY_TAG_Y)
    d.rounded_rectangle([40, RARITY_Y, 440, RARITY_Y + 6], 3, fill=rc)
    return round_corners(card)


def frame_src(out, name):
    """框体源图定位：正式资产 Assets/UI 优先（已发布），预览区 ImageReview 兜底。"""
    for p in (os.path.join("Assets", "UI", name), os.path.join(out, name)):
        if os.path.isfile(p):
            return p
    sys.exit(f"frame not found in Assets/UI or {out}: {name}")


def round_corners(card, radius=28):
    """480×640 产物加圆角透明角（与发布资产 60px@1024 口径一致，≈28px@480）。"""
    mask = Image.new("L", card.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, card.width - 1, card.height - 1], radius, fill=255)
    card.putalpha(mask)
    return card


def main():
    out = os.path.join("ImageReview", "cards")

    make_standard(
        "attack", frame_src(out, "border_card_attack.png"),
        "笔记", "普通", os.path.join(out, "card_attack_biji_1.png"),
        pair=("atk", 6, "伤害"), flip=None,
        tags=[("[笔记]", GREEN)],
    ).save(os.path.join(out, "cardframe_attack.png"))

    make_standard(
        "skill", frame_src(out, "border_card_skill.png"),
        "速读", "普通", os.path.join(out, "card_skill_sudu_1.png"),
        pair=("block", 4, "格挡"), flip="随机揭示周围 1 张背面牌",
        tags=[("[翻开]", GOLD)],
    ).save(os.path.join(out, "cardframe_skill.png"))

    make_ability(
        frame_src(out, "border_card_ability.png"),
        "全神贯注", "普通", os.path.join(out, "card_ability_quanshenguanzhu_1.png"),
        ["每翻开一张牌，获得 1 点「专注」", "专注：下次配对伤害 +1，触发后消耗"],
        flip="获得 2 点格挡",
        tags=[("[翻开]", GOLD)],
    ).save(os.path.join(out, "cardframe_ability.png"))

    make_standard(
        "curse", frame_src(out, "border_card_curse.png"),
        "遗忘", "普通", None,
        pair=None, flip="失去 2 点血量；移除自身",
        tags=[("[翻开]", GOLD), ("[移除]", GREY)],
    ).save(os.path.join(out, "cardframe_curse.png"))

    # 卡背效果图：优先预览区新卡背（本轮定稿 v2 静谧青纹章），发布后退化到正式资产
    back_src = os.path.join(out, "..", "cardbacks", "cardback_universal_v2b.png")
    if not os.path.isfile(back_src):
        back_src = os.path.join("Assets", "UI", "cardback_universal.png")
    load_base(back_src).save(os.path.join(out, "cardframe_back.png"))

    print("Saved: cardframe_attack / skill / ability / curse / back ->", out)


if __name__ == "__main__":
    main()
