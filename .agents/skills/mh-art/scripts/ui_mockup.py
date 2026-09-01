#!/usr/bin/env python3
"""ui_mockup.py — 《记忆勇者》界面示意图合成器 v1（2026-09-01）

按 09-UI设计规范 §6/§7/§8 的布局与色板，把已发布美术资产（背景/logo/卡框/
卡背/敌人/图标）程序化合成为 1920×1080 界面示意图，供设计文档嵌入——
延续 v1.17 卡框"程序生成定稿"口径：布局/文字由程序精确排版，AI 不画 UI 文字。

输出：ImageReview/mockups/mockup_<界面>.png（预览区，校验后 --publish 发布）
用法（仓库根目录）：
    python .agents/skills/mh-art/scripts/ui_mockup.py            # 全部界面
    python .agents/skills/mh-art/scripts/ui_mockup.py s03 s01    # 指定界面
    python .agents/skills/mh-art/scripts/ui_mockup.py --publish  # 预览区全部发布

字体说明：mockup 用系统雅黑（msyhbd/msyh）近似；正式实现按 10 §5 用
Noto Serif SC / Noto Sans SC（TMP 渲染），示意图不绑定字体资产。
"""

import argparse
import math
import os
import shutil
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080

# ---- 色板（09 §2 / 10 §1）----
INK = (59, 50, 38, 255)          # #3B3226 深可可（主文字）
SUB = (138, 122, 96, 255)        # #8A7A60 暖灰褐（次文字）
CREAM = (242, 235, 217, 255)     # #F2EBD9 奶油纸（主背景）
SAND = (230, 220, 194, 255)      # #E6DCC2 暖沙
PANEL = (239, 231, 210, 255)     # #EFE7D2 浅羊皮纸面板
BRIGHT = (248, 242, 227, 255)    # #F8F2E3 亮纸
BORDER = (201, 161, 99, 255)     # #C9A163 暖金木
TEAL = (127, 181, 172, 255)      # #7FB5AC 静谧青
GOLD = (212, 168, 87, 255)       # #D4A857 古金
RED = (199, 62, 62, 255)         # #C73E3E 危险红
BLOCKBLUE = (122, 143, 168, 255) # #7A8FA8 格挡蓝
DARKRED = (139, 44, 44, 255)     # #8B2C2C 敌人血条
BURN = (232, 74, 32, 255)        # #E84A20 灼烧
PURPLE = (155, 69, 212, 255)     # #9B45D4 特殊/精英
TRACK = (217, 205, 176, 255)     # #D9CDB0 条底
WHITE = (255, 255, 255, 255)

FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
REVIEW_DIR = os.path.join("ImageReview", "mockups")
ASSETS = os.path.join("Assets", "UI")


def font(size, bold=True):
    for name in (["msyhbd.ttc", "msyh.ttc"] if bold else ["msyh.ttc", "simhei.ttf"]):
        p = os.path.join(FONTS_DIR, name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    sys.exit("no CJK font in " + FONTS_DIR)


def asset(name):
    """已发布资产优先，预览区兜底，无则 None（调用方画占位）。"""
    for d in (ASSETS, os.path.join("ImageReview", "icons"),
              os.path.join("ImageReview", "backgrounds"),
              os.path.join("ImageReview", "logos")):
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return Image.open(p).convert("RGBA")
    return None


def text(d, xy, s, size=16, fill=INK, bold=True, anchor="la"):
    d.text(xy, s, font=font(size, bold), fill=fill, anchor=anchor)


def rrect(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def panel(img, box, r=8, fill=PANEL, outline=BORDER, width=2, shadow=True):
    """面板：外阴影 0 4 12 rgba(74,58,32,.25)（09 §4.1）。"""
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle(
            [box[0] + 2, box[1] + 6, box[2] + 2, box[3] + 6], r, fill=(74, 58, 32, 70))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    d = ImageDraw.Draw(img)
    rrect(d, box, r, fill=fill, outline=outline, width=width)


def paste_fit(img, im, cx, cy, size):
    """按长边 contain 缩放后以中心贴到 (cx,cy)。"""
    s = size / max(im.size)
    w, h = int(im.width * s), int(im.height * s)
    im2 = im.resize((w, h), Image.LANCZOS)
    img.alpha_composite(im2, (int(cx - w / 2), int(cy - h / 2)))


def icon(img, name, cx, cy, size, fallback_fill=BORDER):
    """贴图标；缺资产时画圆形占位（描边圆）。"""
    im = asset(name)
    if im is not None:
        paste_fit(img, im, cx, cy, size)
    else:
        d = ImageDraw.Draw(img)
        r = size // 2
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  fill=(255, 255, 255, 120), outline=fallback_fill, width=3)


def glow_rect(img, box, r, color=GOLD, width=5):
    """外发光圆角框（悬浮/匹配高亮的静态表达）。color 取 RGB 前三位。"""
    rgb = tuple(color[:3])
    gl = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(gl)
    d.rounded_rectangle(box, r, outline=rgb + (200,), width=width)
    d.rounded_rectangle([box[0] - 6, box[1] - 6, box[2] + 6, box[3] + 6], r + 6,
                        outline=rgb + (90,), width=width + 6)
    img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(4)))


def bar(d, x, y, w, h, ratio, fill, track=TRACK, outline=BORDER):
    rrect(d, [x, y, x + w, y + h], h // 2, fill=track, outline=outline, width=1)
    if ratio > 0:
        rrect(d, [x + 2, y + 2, x + 2 + max(h - 4, int((w - 4) * ratio)), y + h - 2],
              (h - 4) // 2, fill=fill)


def chip(d, x, y, s, bg, fg=WHITE, size=14, pad=10, h=26, outline=INK, ow=1):
    f = font(size)
    tw = d.textlength(s, font=f)
    rrect(d, [x, y, x + tw + pad * 2, y + h], h // 2, fill=bg, outline=outline, width=ow)
    d.text((x + pad, y + (h - f.size) / 2 - 1), s, font=f, fill=fg)
    return x + tw + pad * 2


def drop_shadow(img, box, r=12, alpha=110, blur=8):
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [box[0] + 4, box[1] + 8, box[2] + 4, box[3] + 8], r, fill=(0, 0, 0, alpha))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))


def topbar(img, title=None):
    """战斗/地图顶栏 48px（09 §6.1）：菜单/金币/遗物栏 | 牌库/设置。"""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, 0, W, 48], fill=BRIGHT[:3] + (232,))
    d.line([0, 48, W, 48], fill=BORDER, width=2)
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    icon(img, "icon_menu.png", 26, 24, 26)
    icon(img, "icon_gold.png", 96, 24, 26)
    text(d, (116, 24), "150", size=18, anchor="lm")
    # 遗物栏在战斗界面由左侧竖排面板承担（09 §6.2 区域定义表），顶栏不再重复
    icon(img, "icon_deck.png", W - 140, 24, 26)
    text(d, (W - 122, 24), "牌库", size=15, anchor="lm")
    icon(img, "icon_settings.png", W - 44, 24, 26)
    if title:
        text(d, (W // 2, 24), title, size=18, fill=INK, anchor="mm")


def bottombar(img):
    """战斗底栏 64px（09 §6.6）：四堆计数 | 重新铺满 | 血量/格挡。"""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rectangle([0, H - 64, W, H], fill=BRIGHT[:3] + (232,))
    d.line([0, H - 64, W, H - 64], fill=BORDER, width=2)
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    x = 28
    for name, num, cap in (("icon_deck.png", "15", "抽牌"),
                           ("icon_discard.png", "3", "弃牌"),
                           ("icon_exhaust.png", "1", "消耗"),
                           ("icon_memory.png", "2", "记忆")):
        icon(img, name, x, H - 40, 26)
        text(d, (x + 20, H - 44), num, size=18, anchor="lm")
        text(d, (x + 20, H - 22), cap, size=12, fill=SUB, bold=False, anchor="lm")
        x += 88
    # 重新铺满（主按钮，居中）
    bw, bh = 190, 38
    panel(img, [W // 2 - bw // 2, H - 53, W // 2 + bw // 2, H - 53 + bh], 8,
          fill=GOLD, outline=(160, 120, 55, 255))
    text(d, (W // 2, H - 34), "重新铺满 +2", size=17, anchor="mm")
    # 玩家血量 + 格挡（右）
    icon(img, "icon_hp.png", W - 330, H - 32, 26)
    bar(d, W - 310, H - 42, 170, 20, 48 / 60, fill=RED)
    text(d, (W - 132, H - 32), "48/60", size=18, anchor="lm")
    icon(img, "icon_block.png", W - 62, H - 32, 26)
    text(d, (W - 42, H - 32), "5", size=18, fill=BLOCKBLUE, anchor="lm")


def actionbar(img, x, y):
    """右侧行动条：10 段圆点（09 §4.3）——已消耗红实心，剩余金空心，阈值段放大金环。"""
    d = ImageDraw.Draw(img)
    text(d, (x, y), "行动条", size=17)
    for i in range(10):
        r = 11 if i == 9 else 8
        cy = y + 44 + (i // 5) * 26
        cxx = x + 20 + (i % 5) * 30
        if i < 7:
            d.ellipse([cxx - r, cy - r, cxx + r, cy + r], fill=RED, outline=INK, width=2)
        else:
            d.ellipse([cxx - r, cy - r, cxx + r, cy + r], outline=BORDER,
                      width=3 if i == 9 else 2)
            if i == 9:
                d.ellipse([cxx - r - 4, cy - r - 4, cxx + r + 4, cy + r + 4],
                          outline=GOLD, width=2)
    text(d, (x + 86, y + 104), "7 / 10", size=18, anchor="mm")


def s03_battle():
    """S03 战斗界面（09 §6）：顶栏/敌人/4×4 网格/右侧面板/底栏 + 悬浮预览。"""
    base = asset("bg_battle.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    topbar(img)
    bottombar(img)

    # 左侧遗物竖排（64px 宽）
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([0, 48, 64, H - 64], fill=BRIGHT[:3] + (210,))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    d.line([64, 48, 64, H - 64], fill=BORDER, width=2)
    text(d, (32, 76), "遗物", size=13, fill=SUB, anchor="mm")
    for i in range(3):
        d.ellipse([14, 110 + i * 64, 50, 146 + i * 64],
                  fill=(255, 255, 255, 90), outline=BORDER, width=2)

    # 敌人区（顶部中央）
    goblin = asset("enemy_goblin.png")
    if goblin:
        paste_fit(img, goblin, W // 2, 168, 200)
    d = ImageDraw.Draw(img)
    bar(d, W // 2 - 90, 288, 180, 20, 35 / 40, fill=DARKRED)
    text(d, (W // 2, 322), "哥林布", size=18, anchor="mm")

    # 右侧信息面板（09 §6.5）
    px, py, pw = W - 216, 64, 200
    panel(img, [px, py, px + pw, py + 500])
    actionbar(img, px + 16, py + 14)
    d = ImageDraw.Draw(img)
    d.line([px + 12, py + 150, px + pw - 12, py + 150], fill=BORDER, width=1)
    text(d, (px + 16, py + 160), "意图", size=17)
    panel(img, [px + 14, py + 188, px + pw - 14, py + 264], 6,
          fill=BRIGHT, outline=BORDER, width=1, shadow=False)
    icon(img, "icon_intent_attack.png", px + 42, py + 212, 36, fallback_fill=RED)
    text(d, (px + 68, py + 210), "攻击", size=16)
    text(d, (px + 68, py + 234), "造成 8 点伤害", size=13, bold=False)
    d.line([px + 12, py + 284, px + pw - 12, py + 284], fill=BORDER, width=1)
    text(d, (px + 16, py + 294), "敌人状态", size=17)
    icon(img, "icon_status_burn.png", px + 32, py + 332, 26, fallback_fill=BURN)
    text(d, (px + 52, py + 332), "灼烧 ×2", size=14, bold=False, anchor="lm")
    d.line([px + 12, py + 362, px + pw - 12, py + 362], fill=BORDER, width=1)
    text(d, (px + 16, py + 372), "敌人能力", size=17)
    x2 = chip(d, px + 14, py + 404, "混乱", PURPLE)
    text(d, (x2 + 8, py + 417), "随机交换 2 张", size=13, bold=False, anchor="lm")

    # 4×4 卡牌网格（09 §6.3）：516×676 居中
    gx, gy, cw, ch, gap = 702, 335, 120, 160, 12
    faceup = {(1, 1): "cardframe_attack.png", (1, 2): "cardframe_skill.png"}
    hover = (3, 0)          # 网格左下角背面牌悬停上浮（09 §9.1：上浮4px+边框发光）
    back = asset("cardback_universal.png")
    for row in range(4):
        for col in range(4):
            x, y = gx + col * (cw + gap), gy + row * (ch + gap)
            if (row, col) in faceup:
                card = asset(faceup[(row, col)])
                img.alpha_composite(card.resize((cw, ch), Image.LANCZOS), (x, y))
            elif back is not None:
                dy = -8 if (row, col) == hover else 0
                img.alpha_composite(back.resize((cw, ch), Image.LANCZOS), (x, y + dy))
    hx, hy = gx, gy + 3 * (ch + gap) - 8
    glow_rect(img, [hx - 4, hy - 4, hx + cw + 4, hy + ch + 4], 10, width=6)
    # 标记角标：右上角金色 ✦×2（v1.20 增益化标记，仅层数不泄内容）
    mx, my = gx + 3 * (cw + gap), gy
    d.polygon([(mx + cw - 44, my + 8), (mx + cw - 47, my + 17), (mx + cw - 56, my + 20),
               (mx + cw - 47, my + 23), (mx + cw - 44, my + 32), (mx + cw - 41, my + 23),
               (mx + cw - 32, my + 20), (mx + cw - 41, my + 17)], fill=GOLD, outline=INK)
    text(d, (mx + cw - 26, my + 20), "×2", size=13, anchor="mm")

    # 悬浮预览卡（09 §6.7：240×320，正面牌悬停时弹出）
    pv = asset("cardframe_skill.png")
    if pv:
        pxv, pyv = 1330, 520
        drop_shadow(img, [pxv, pyv, pxv + 240, pyv + 320], r=14)
        img.alpha_composite(pv.resize((240, 320), Image.LANCZOS), (pxv, pyv))

    return img, "mockup_s03_battle.png"


def s01_menu():
    """S01 主菜单（09 §5.1）：bg_menu + 徽标 + 字标 + 主/次按钮组。"""
    base = asset("bg_menu.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    d = ImageDraw.Draw(img)
    logo = asset("logo_main.png")
    if logo:
        paste_fit(img, logo, W // 2, 268, 360)
    # 字标：正式实现为思源宋体 Bold 独立设计；此处雅黑加古金描边近似示意
    d.text((W // 2, 520), "记忆勇者", font=font(104), fill=INK, anchor="mm",
           stroke_width=3, stroke_fill=GOLD)
    text(d, (W // 2, 600), "记 忆 配 对  ·  卡 牌 肉 鸽", size=22, fill=(96, 84, 62, 255),
         bold=False, anchor="mm")
    # 按钮组（09 §4.2）
    panel(img, [W // 2 - 150, 668, W // 2 + 150, 736], 12, fill=GOLD,
          outline=(140, 105, 50, 255), width=3)
    text(d, (W // 2, 702), "开始游戏", size=24, anchor="mm")
    for i, label in enumerate(("角色选择", "设置", "退出")):
        y = 766 + i * 70
        panel(img, [W // 2 - 120, y, W // 2 + 120, y + 54], 10, fill=BRIGHT,
              outline=BORDER, width=2)
        text(d, (W // 2, y + 27), label, size=19, anchor="mm")
    return img, "mockup_s01_menu.png"


def _map_node(d, cx, cy, kind, dim=False):
    """已通过节点变暗：PIL ImageDraw 不做 alpha 混合，直接与面板色掺混成浅色。"""
    def c(rgb):
        if dim:
            return tuple(int(v * 0.45 + PANEL[i] * 0.55) for i, v in enumerate(rgb)) + (255,)
        return rgb + (255,)
    if kind == "battle":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=c((199, 62, 62)),
                  outline=INK, width=2)
    elif kind == "elite":
        d.polygon([(cx, cy - 24), (cx + 20, cy), (cx, cy + 24), (cx - 20, cy)],
                  fill=c((155, 69, 212)), outline=INK)
    elif kind == "shop":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=c((212, 168, 87)),
                  outline=INK, width=2)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=INK, width=2)
    elif kind == "campfire":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=c((232, 123, 53)),
                  outline=INK, width=2)
        d.polygon([(cx, cy - 11), (cx + 7, cy + 2), (cx - 7, cy + 2)], fill=INK)
    elif kind == "event":
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=c((74, 156, 212)),
                  outline=INK, width=2)
        text(d, (cx, cy - 1), "?", size=22, fill=WHITE, anchor="mm")
    elif kind == "boss":
        pts = [(cx + (30 if k % 2 == 0 else 14) * math.sin(math.radians(k * 36 - 90)),
                cy + (30 if k % 2 == 0 else 14) * math.cos(math.radians(k * 36 - 90)))
               for k in range(10)]
        d.polygon(pts, fill=c((232, 74, 32)), outline=INK)
    elif kind == "start":
        d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill=INK)
        d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], outline=GOLD, width=4)


def s04_map():
    """S04 Meta地图（09 §7.1）：奶油纸底 + 自下而上节点树 + 底部状态栏。"""
    img = Image.new("RGBA", (W, H), CREAM)
    topbar(img, "第 1 章 · 记忆回廊")
    panel(img, [70, 70, W - 70, H - 150], 12, fill=PANEL)
    d = ImageDraw.Draw(img)
    text(d, (110, 108), "● 当前位置 · 金线 = 已走路径 · 自下而上推进，顶端为章节 Boss",
         size=14, fill=SUB, bold=False, anchor="lm")

    # 层（自下而上，取 09 §5.3 章节1 示例布局）；节点加大、横向拉开占满面板
    cx0 = W // 2
    rows = [
        (860, [("start", 0)]),
        (740, [("battle", -360), ("battle", -120), ("event", 120), ("elite", 360)]),
        (620, [("battle", -360), ("shop", -120), ("battle", 120), ("battle", 360)]),
        (500, [("event", -360), ("battle", -120), ("campfire", 120), ("battle", 360)]),
        (360, [("boss", 0)]),
    ]
    chosen_edges = {(0, 0, 0), (1, 0, 0), (2, 0, 0), (3, 0, 0)}  # 已走路径（左侧）
    for ri in range(len(rows) - 1):
        y0, upper_y = rows[ri][0], rows[ri + 1][0]
        for ci, (_, dx) in enumerate(rows[ri][1]):
            for cj, (_, dx2) in enumerate(rows[ri + 1][1]):
                if abs(dx - dx2) <= 260:
                    chosen = (ri, ci, cj) in chosen_edges
                    d.line([cx0 + dx, y0 - 34, cx0 + dx2, upper_y + 40],
                           fill=GOLD if chosen else BORDER,
                           width=6 if chosen else 2)
    dimmed = {(740, -360), (620, -360), (500, -360)}
    for y0, nodes in rows:
        for kind, dx in nodes:
            _map_node(d, cx0 + dx, y0, kind, dim=(y0, dx) in dimmed)
    text(d, (cx0, 424), "记忆吞噬者", size=16, fill=INK, anchor="mm")

    # 底部状态栏
    panel(img, [70, H - 130, W - 70, H - 40], 10, fill=BRIGHT)
    for i in range(5):
        d.ellipse([100 + i * 46, H - 114, 132 + i * 46, H - 82],
                  fill=(255, 255, 255, 90), outline=BORDER, width=2)
    text(d, (356, H - 98), "遗物栏", size=13, fill=SUB, bold=False, anchor="lm")
    scholar = asset("portrait_scholar.png")
    if scholar:
        head = scholar.crop((0, 0, scholar.width, int(scholar.width * 1.1)))
        paste_fit(img, head, W - 300, H - 85, 60)
    text(d, (W - 262, H - 98), "角色：学者（情报型）", size=15, anchor="lm")
    return img, "mockup_s04_map.png"


def s05_reward():
    """S05 卡牌奖励（09 §8.1）：暗幕 + 三选一大卡（中卡悬浮发光）+ 跳过。"""
    base = asset("bg_battle.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    ov = Image.new("RGBA", img.size, (0, 0, 0, 115))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 170), "战斗胜利！", size=44, fill=GOLD, anchor="mm")
    text(d, (W // 2, 232), "选择一张卡牌加入牌库", size=20, fill=CREAM,
         bold=False, anchor="mm")
    cards = ("cardframe_attack.png", "cardframe_skill.png", "cardframe_ability.png")
    for i, name in enumerate(cards):
        card = asset(name)
        if card is None:
            continue
        c = card.resize((200, 280), Image.LANCZOS)
        cx = W // 2 + (i - 1) * 320
        top = 430 if i == 1 else 470   # 中间卡上浮 + 发光（悬浮态示意，09 §8.1）
        if i == 1:
            glow_rect(img, [cx - 108, top - 8, cx + 108, top + 288], 14, width=9)
        drop_shadow(img, [cx - 100, top, cx + 100, top + 280], r=14)
        img.alpha_composite(c, (cx - 100, top))
    bw = 220
    panel(img, [W // 2 - bw // 2, 940, W // 2 + bw // 2, 992], 10, fill=BRIGHT,
          outline=BORDER, width=2)
    text(d, (W // 2, 966), "跳过（不选）", size=18, anchor="mm")
    return img, "mockup_s05_reward.png"


SCREENS = {"s01": s01_menu, "s03": s03_battle, "s04": s04_map, "s05": s05_reward}


def main():
    ap = argparse.ArgumentParser(description="Memory Hero UI mockup compositor")
    ap.add_argument("screens", nargs="*", help="s01 s03 s04 s05（默认全部）")
    ap.add_argument("--publish", action="store_true",
                    help="把 ImageReview/mockups/ 全部发布到 Assets/UI/")
    args = ap.parse_args()
    keys = args.screens or list(SCREENS)
    for k in keys:
        if k not in SCREENS:
            sys.exit(f"unknown screen: {k}（可选：{list(SCREENS)}）")
    os.makedirs(REVIEW_DIR, exist_ok=True)
    for k in keys:
        img, fname = SCREENS[k]()
        out = os.path.join(REVIEW_DIR, fname)
        img.convert("RGB").save(out)
        print(f"Saved: {out}")
    if args.publish:
        os.makedirs(ASSETS, exist_ok=True)
        for f in sorted(os.listdir(REVIEW_DIR)):
            if f.startswith("mockup_") and f.endswith(".png"):
                shutil.move(os.path.join(REVIEW_DIR, f), os.path.join(ASSETS, f))
                print(f"Published: {f} -> {ASSETS}")


if __name__ == "__main__":
    main()
