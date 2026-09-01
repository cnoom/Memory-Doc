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
GREEN = (91, 168, 91, 255)       # #5BA85B 成功绿
BLOCKBLUE = (122, 143, 168, 255) # #7A8FA8 格挡蓝
DARKRED = (139, 44, 44, 255)     # #8B2C2C 敌人血条
BURN = (232, 74, 32, 255)        # #E84A20 灼烧
PURPLE = (155, 69, 212, 255)     # #9B45D4 特殊/精英
TRACK = (217, 205, 176, 255)     # #D9CDB0 条底
WHITE = (255, 255, 255, 255)

FONTS_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
REVIEW_DIR = os.path.join("ImageReview", "mockups")
ASSETS = os.path.join("Assets", "UI")

# Assets/UI 按类型分子目录（与 ImageReview/<类型>/ 同名），asset() 依次查找
ASSET_SUBDIRS = ("cards", "cardbacks", "cardframes", "icons", "relics", "potions",
                 "map-nodes", "enemies", "portraits", "backgrounds", "textures",
                 "logos", "mockups")


def font(size, bold=True):
    for name in (["msyhbd.ttc", "msyh.ttc"] if bold else ["msyh.ttc", "simhei.ttf"]):
        p = os.path.join(FONTS_DIR, name)
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    sys.exit("no CJK font in " + FONTS_DIR)


def asset(name):
    """已发布资产优先（Assets/UI/<类型>/ 分目录），预览区兜底，无则 None（调用方画占位）。"""
    dirs = ([os.path.join(ASSETS, d) for d in ASSET_SUBDIRS]
            + [os.path.join("ImageReview", "icons"),
               os.path.join("ImageReview", "backgrounds"),
               os.path.join("ImageReview", "logos")])
    for d in dirs:
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


def hover_glow(img, box, r=10):
    """悬停高亮加强版：亮芯线 + 饱和橙金双层晕——米色浅底上比 glow_rect 醒目。"""
    for w, col, blur in ((3, (255, 236, 170, 255), 0),
                         (6, (255, 190, 70, 230), 3),
                         (11, (255, 168, 40, 140), 6)):
        ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(ov).rounded_rectangle(box, r, outline=col, width=w)
        img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(blur)))


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
    icon(img, "icon_deck.png", W - 152, 24, 26)
    text(d, (W - 134, 24), "牌库", size=15, anchor="lm")
    icon(img, "icon_settings.png", W - 44, 24, 26)
    if title:
        text(d, (W // 2, 24), title, size=18, fill=INK, anchor="mm")


def deck_tray(img, box):
    """牌桌托盘（09 §6.6 左右结构版）：四堆计数 + 重新铺满主按钮，托在网格下方。"""
    x0, y0, x1, y1 = box
    panel(img, box, 10, fill=BRIGHT)
    d = ImageDraw.Draw(img)
    x = x0 + 26
    for name, num, cap in (("icon_deck.png", "15", "抽牌"),
                           ("icon_discard.png", "3", "弃牌"),
                           ("icon_exhaust.png", "1", "消耗"),
                           ("icon_memory.png", "2", "记忆")):
        icon(img, name, x, (y0 + y1) // 2, 28)
        text(d, (x + 22, y0 + 19), num, size=17, anchor="lm")
        text(d, (x + 22, y0 + 41), cap, size=12, fill=SUB, bold=False, anchor="lm")
        x += 84
    bw, bh = 190, 40
    bb = [x1 - 22 - bw, (y0 + y1) // 2 - bh // 2, x1 - 22, (y0 + y1) // 2 + bh // 2]
    glow_rect(img, bb, 8, width=3)
    panel(img, bb, 8, fill=GOLD, outline=(160, 120, 55, 255))
    text(d, (x1 - 22 - bw // 2, (y0 + y1) // 2), "重新铺满 +2", size=17, anchor="mm")


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
    """S03 战斗界面（09 §6，左右结构）：左=牌桌（4×4 网格放大 136×181 + 堆计数
    托盘），右=敌人展示（大立绘/血条/意图/状态）+ 行动条 + 玩家状态；无全局底栏。"""
    base = asset("bg_battle.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    topbar(img)

    # 左侧遗物竖排（64px 宽，通高）
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([0, 48, 64, H], fill=BRIGHT[:3] + (210,))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    d.line([64, 48, 64, H], fill=BORDER, width=2)
    text(d, (32, 76), "遗物", size=13, fill=SUB, anchor="mm")
    for i in range(3):
        d.ellipse([14, 110 + i * 64, 50, 146 + i * 64],
                  fill=(255, 255, 255, 90), outline=BORDER, width=2)

    # ---- 左区·牌桌：4×4 网格（136×181，卡面放大提升记牌可读性）----
    gx, gy, cw, ch, gap = 443, 84, 136, 181, 14
    faceup = {(1, 0): "cardframe_skill.png", (1, 3): "cardframe_attack.png"}
    pv_src = (1, 0)          # 正面牌悬停：发光 + 左侧弹出预览（09 §6.7 跟随鼠标）
    hover = (3, 3)           # 右下角背面牌悬停上浮（09 §9.1：上浮+边框发光）
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
    hx, hy = gx + 3 * (cw + gap), gy + 3 * (ch + gap) - 8
    hover_glow(img, [hx - 4, hy - 4, hx + cw + 4, hy + ch + 4])
    # 正面悬停卡发光（与悬浮预览卡配对表达）
    fx, fy = gx + pv_src[1] * (cw + gap), gy + pv_src[0] * (ch + gap)
    hover_glow(img, [fx - 4, fy - 4, fx + cw + 4, fy + ch + 4])
    # 标记角标：右上角金色 ✦×2（v1.20 增益化标记，仅层数不泄内容）
    mx, my = gx + 3 * (cw + gap), gy
    d.polygon([(mx + cw - 44, my + 8), (mx + cw - 47, my + 17), (mx + cw - 56, my + 20),
               (mx + cw - 47, my + 23), (mx + cw - 44, my + 32), (mx + cw - 41, my + 23),
               (mx + cw - 32, my + 20), (mx + cw - 41, my + 17)], fill=GOLD, outline=INK)
    text(d, (mx + cw - 26, my + 20), "×2", size=13, anchor="mm")

    # 牌桌托盘：四堆计数 + 重新铺满（原全局底栏职能并入牌桌下方，与网格同宽对齐）
    deck_tray(img, [443, 884, 1029, 948])

    # ---- 右列·敌人展示（上）与玩家状态（下）----
    ex = 1658
    goblin = asset("enemy_goblin.png")
    if goblin:
        paste_fit(img, goblin, ex, 268, 400)
    d = ImageDraw.Draw(img)
    text(d, (ex, 496), "哥林布", size=20, anchor="mm")
    bar(d, ex - 140, 518, 280, 20, 35 / 40, fill=DARKRED)
    text(d, (ex + 150, 528), "35/40", size=15, anchor="lm")
    # 行动条（01 §6：敌人蓄力计量，翻牌+1、满则敌人出手——归属敌人信息块）
    actionbar(img, 1520, 566)
    d = ImageDraw.Draw(img)
    panel(img, [ex - 160, 712, ex + 160, 778], 8, fill=BRIGHT, width=2)
    icon(img, "icon_intent_attack.png", ex - 118, 745, 38, fallback_fill=RED)
    text(d, (ex - 88, 730), "意图 · 攻击", size=16)
    text(d, (ex - 88, 754), "造成 8 点伤害", size=13, bold=False)
    icon(img, "icon_status_burn.png", ex - 148, 819, 24, fallback_fill=BURN)
    text(d, (ex - 130, 819), "灼烧 ×2", size=14, bold=False, anchor="lm")
    x2 = chip(d, ex - 160, 838, "混乱", PURPLE)
    text(d, (x2 + 8, 851), "随机交换 2 张", size=13, bold=False, anchor="lm")

    # 玩家状态横条（右列底部）
    panel(img, [1448, 916, 1868, 996], 12)
    icon(img, "icon_hp.png", 1520, 956, 26)
    bar(d, 1540, 946, 180, 20, 48 / 60, fill=RED)
    text(d, (1728, 956), "48/60", size=17, anchor="lm")
    icon(img, "icon_block.png", 1810, 956, 26)
    text(d, (1836, 956), "5", size=17, fill=BLOCKBLUE, anchor="lm")

    # 悬浮预览卡（09 §6.7：240×320，跟随鼠标——示意表达为悬停卡左缘贴身弹出）
    pv = asset("cardframe_skill.png")
    if pv:
        cy = fy + ch // 2
        pxv, pyv = fx - 20 - 240, cy - 160
        text(d, (pxv + 120, pyv - 14), "悬浮预览（跟随鼠标）", size=13,
             fill=(96, 84, 62, 255), bold=False, anchor="mm")
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


def relic_glyph(d, cx, cy, r, kind, ring=(232, 123, 53, 255)):
    """遗物占位徽记（Boss 橙环 + 简笔符号）——真遗物图标批量后替换。"""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BRIGHT, outline=ring, width=4)
    ink = INK
    if kind == "eye":
        d.ellipse([cx - r * 0.55, cy - r * 0.3, cx + r * 0.55, cy + r * 0.3],
                  fill=WHITE, outline=ink, width=2)
        d.ellipse([cx - r * 0.16, cy - r * 0.16, cx + r * 0.16, cy + r * 0.16],
                  fill=(74, 122, 212, 255), outline=ink, width=2)
    elif kind == "swirl":
        for i, rr in enumerate((0.62, 0.42, 0.22)):
            d.arc([cx - r * rr, cy - r * rr, cx + r * rr, cy + r * rr],
                  90 + i * 60, 360 + i * 60, fill=ink if i % 2 else (155, 69, 212, 255), width=4)
        d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=ink)
    elif kind == "crown":
        d.polygon([(cx - r * 0.5, cy + r * 0.3), (cx - r * 0.5, cy - r * 0.2),
                   (cx - r * 0.25, cy + r * 0.02), (cx, cy - r * 0.42),
                   (cx + r * 0.25, cy + r * 0.02), (cx + r * 0.5, cy - r * 0.2),
                   (cx + r * 0.5, cy + r * 0.3)], fill=GOLD, outline=ink)
    elif kind == "brain":
        # 大脑徽记：双圆叶主体 + 中缝 + 三条青色脑回弧线
        d.ellipse([cx - r * 0.52, cy - r * 0.34, cx + r * 0.52, cy + r * 0.34],
                  fill=(242, 235, 217, 255), outline=ink, width=3)
        d.line([cx, cy - r * 0.32, cx, cy + r * 0.32], fill=ink, width=3)
        d.arc([cx - r * 0.44, cy - r * 0.22, cx - r * 0.04, cy + r * 0.26],
              200, 340, fill=TEAL, width=3)
        d.arc([cx - r * 0.2, cy - r * 0.26, cx + r * 0.2, cy + r * 0.22],
              200, 340, fill=TEAL, width=3)
        d.arc([cx + r * 0.04, cy - r * 0.22, cx + r * 0.44, cy + r * 0.26],
              200, 340, fill=TEAL, width=3)
    elif kind == "bolt":
        d.polygon([(cx - r * 0.15, cy - r * 0.55), (cx + r * 0.35, cy - r * 0.55),
                   (cx + r * 0.02, cy - r * 0.05), (cx + r * 0.3, cy - r * 0.05),
                   (cx - r * 0.3, cy + r * 0.55), (cx - r * 0.02, cy),
                   (cx - r * 0.3, cy)], fill=(232, 194, 58, 255), outline=ink)


def slider(d, x, y, w, ratio, label=None, value=None):
    """设置行滑条：暖沙轨道 + 古金圆钮。"""
    if label:
        text(d, (x, y - 14), label, size=15, bold=False, anchor="lm")
    d.rounded_rectangle([x, y - 3, x + w, y + 3], 3, fill=TRACK, outline=BORDER, width=1)
    d.rounded_rectangle([x, y - 3, x + int(w * ratio), y + 3], 3, fill=TEAL)
    d.ellipse([x + int(w * ratio) - 9, y - 9, x + int(w * ratio) + 9, y + 9],
              fill=GOLD, outline=INK, width=2)
    if value:
        text(d, (x + w + 16, y), value, size=14, bold=False, anchor="lm")


def s02_select():
    """S02 角色选择（09 §5.1）：学者可选、狂战士/术士锁定，附被动与初始牌库预览。"""
    img = Image.new("RGBA", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    icon(img, "icon_back.png", 96, 60, 30)
    text(d, (120, 60), "返回", size=15, bold=False, anchor="lm")
    text(d, (W // 2, 60), "角色选择", size=24, anchor="mm")
    icon(img, "icon_settings.png", W - 44, 60, 26)

    def char_slot(cx, name, sub, active):
        box = [cx - 185, 110, cx + 185, 900]
        panel(img, box, 14, fill=BRIGHT if active else SAND,
              outline=GOLD if active else BORDER, width=4 if active else 2)
        if active:
            glow_rect(img, [box[0] - 8, box[1] - 8, box[2] + 8, box[3] + 8], 18, width=6)
        if name == "学者":
            scholar = asset("portrait_scholar.png")
            if scholar:
                paste_fit(img, scholar, cx, 350, 340)
            text(d, (cx, 566), name, size=26, anchor="mm")
            chip(d, cx - 172, 596, "被动", TEAL, size=12, pad=8, h=22)
            text(d, (cx - 100, 607), "触类旁通", size=14, bold=False, anchor="lm")
            text(d, (cx, 640), "[共鸣]配对时附加额外效果", size=13, fill=SUB,
                 bold=False, anchor="mm")
            text(d, (cx, 700), "初始牌库 · 10 张（战斗中 20 张）", size=13, fill=SUB,
                 bold=False, anchor="mm")
            text(d, (cx, 726), "缩略为 5 张代表卡", size=11, fill=SUB, bold=False, anchor="mm")
            for i, f in enumerate(("cardframe_attack.png", "cardframe_skill.png",
                                   "cardframe_ability.png", "cardframe_attack.png",
                                   "cardframe_skill.png")):
                c = asset(f)
                if c:
                    thumb = c.resize((56, 75), Image.LANCZOS)
                    img.alpha_composite(thumb, (cx - 158 + i * 66, 756))
        else:
            lock = (232, 123, 53, 255)
            d.rounded_rectangle([cx - 26, 324, cx + 26, 376], 10,
                                fill=(217, 205, 176, 255), outline=lock, width=4)
            d.arc([cx - 18, 292, cx + 18, 328], 180, 360, fill=lock, width=5)
            d.ellipse([cx - 70, 420, cx + 70, 560], outline=BORDER, width=3)
            text(d, (cx, 490), "?", size=64, fill=BORDER, anchor="mm")
            text(d, (cx, 566), name, size=26, fill=SUB, anchor="mm")
            text(d, (cx, 607), sub, size=13, fill=SUB, bold=False, anchor="mm")
            text(d, (cx, 700), "待解锁 · 形象设计中", size=13, fill=SUB, bold=False, anchor="mm")
        return box

    char_slot(500, "学者", "情报型 · 已可选", True)
    char_slot(960, "狂战士", "暴力输出型", False)
    char_slot(1420, "术士", "高风险解锁型", False)
    panel(img, [W // 2 - 130, 946, W // 2 + 130, 1002], 10, fill=GOLD,
          outline=(140, 105, 50, 255), width=3)
    text(d, (W // 2, 974), "选择并开始", size=20, anchor="mm")
    return img, "mockup_s02_select.png"


def s06_deck():
    """S06 牌库查看（09 §8.2/§8.2.1）：左侧按类型分组缩略，右侧预览+统计。"""
    img = Image.new("RGBA", (W, H), CREAM)
    topbar(img, "牌库查看")
    d = ImageDraw.Draw(img)
    icon(img, "icon_deck.png", 1560, 24, 24)
    text(d, (1580, 24), "共 15 张 · 战斗中 30 张", size=14, bold=False, anchor="lm")

    groups = [
        ("攻击牌（7 张）", RED, [("cardframe_attack.png", "笔记", 3),
                                ("cardframe_attack.png", "读书笔记", 2)]),
        ("技能牌（6 张）", (69, 119, 212, 255), [("cardframe_skill.png", "速读", 3),
                                                ("cardframe_skill.png", "笔记本格挡", 2)]),
        ("能力牌（1 张）", PURPLE, [("cardframe_ability.png", "全神贯注", 1)]),
        ("诅咒牌（1 张）", (58, 42, 58, 255), [("cardframe_curse.png", "遗忘", 1)]),
    ]
    y = 84
    for title, color, cards in groups:
        panel(img, [80, y, 1160, y + 224], 10, fill=PANEL)
        d = ImageDraw.Draw(img)
        d.ellipse([108, y + 18, 124, y + 34], fill=color)
        text(d, (136, y + 26), title, size=17, anchor="lm")
        x = 120
        for f, name, n in cards:
            c = asset(f)
            if c:
                thumb = c.resize((78, 104), Image.LANCZOS)
                drop_shadow(img, [x, y + 56, x + 78, y + 160], r=8, alpha=60, blur=4)
                img.alpha_composite(thumb, (x, y + 56))
            text(d, (x + 39, y + 178), name, size=13, bold=False, anchor="mm")
            chip(d, x + 44, y + 48, f"×{n}", color, size=11, pad=6, h=18)
            x += 130
        y += 246

    # 右列：悬浮预览 + 统计
    panel(img, [1210, 84, 1840, 480], 10, fill=BRIGHT)
    text(d, (1525, 116), "悬浮预览（点击卡牌展示）", size=13, fill=SUB, bold=False, anchor="mm")
    pv = asset("cardframe_attack.png")
    if pv:
        drop_shadow(img, [1405, 150, 1645, 470], r=14)
        img.alpha_composite(pv.resize((240, 320), Image.LANCZOS), (1405, 150))
    panel(img, [1210, 510, 1840, 1010], 10, fill=PANEL)
    text(d, (1240, 544), "统计", size=17)
    for i, (label, num, col) in enumerate((("攻击", 7, RED), ("技能", 6, (69, 119, 212, 255)),
                                           ("能力", 1, PURPLE), ("诅咒", 1, (58, 42, 58, 255)))):
        yy = 584 + i * 44
        d.ellipse([1244, yy - 9, 1260, yy + 7], fill=col)
        text(d, (1276, yy), label, size=15, bold=False, anchor="lm")
        text(d, (1800, yy), str(num), size=16, anchor="rm")
    d.line([1240, 776, 1810, 776], fill=BORDER, width=1)
    text(d, (1240, 802), "同名分组", size=17)
    for i, (name, n) in enumerate((("笔记", 3), ("速读", 3), ("读书笔记", 2),
                                   ("笔记本格挡", 2), ("全神贯注", 1), ("遗忘", 1))):
        yy = 842 + i * 30
        text(d, (1244, yy), f"{name} ×{n}", size=14, bold=False, anchor="lm")
    return img, "mockup_s06_deck.png"


def s07_shop():
    """S07 商店（09 §7.2）：卡牌出售 + 遗物出售 + 移除服务。"""
    base = asset("bg_shop.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    topbar(img, "商店")
    d = ImageDraw.Draw(img)
    icon(img, "icon_back.png", 96, 120, 30)
    text(d, (120, 120), "返回", size=15, bold=False, anchor="lm")
    icon(img, "icon_gold.png", 1770, 120, 30)
    text(d, (1794, 120), "150 G", size=18, anchor="lm")

    panel(img, [110, 170, 1130, 990], 12)
    text(d, (140, 210), "卡牌出售（3 张）", size=20)
    for i, (f, price) in enumerate((("cardframe_attack.png", "45G"),
                                    ("cardframe_skill.png", "60G"),
                                    ("cardframe_ability.png", "75G"))):
        c = asset(f)
        cx = 260 + i * 380
        if c:
            card = c.resize((180, 240), Image.LANCZOS)
            drop_shadow(img, [cx - 90, 280, cx + 90, 520], r=14)
            img.alpha_composite(card, (cx - 90, 280))
        chip(d, cx - 34, 548, price, GOLD, fg=INK, size=15, h=30, outline=INK, ow=2)
    text(d, (140, 640), "购买后加入牌库（战斗中以 2 份出现）", size=13, fill=SUB,
         bold=False, anchor="lm")
    d = ImageDraw.Draw(img)
    d.line([140, 700, 1100, 700], fill=BORDER, width=1)
    text(d, (140, 740), "刷新商品（下次到访）", size=14, bold=False, anchor="lm")

    panel(img, [1190, 170, 1830, 620], 12)
    text(d, (1220, 210), "遗物出售（2 件）", size=20)
    for i, (glyph, name, price, desc) in enumerate((
            ("brain", "思维导图", "75G", "翻开时概率额外触发"),
            ("bolt", "蓄能水晶", "120G", "每回合首张牌效果+1"))):
        cx = 1360 + i * 320
        relic_glyph(d, cx, 340, 64, glyph)
        text(d, (cx, 436), name, size=17, anchor="mm")
        text(d, (cx, 470), desc, size=12, fill=SUB, bold=False, anchor="mm")
        chip(d, cx - 30, 496, price, GOLD, fg=INK, size=14, h=28, outline=INK, ow=2)
    panel(img, [1190, 660, 1830, 990], 12, fill=BRIGHT)
    text(d, (1220, 700), "移除卡牌服务", size=20)
    text(d, (1220, 748), "选择牌库中的一张牌永久移除", size=14, bold=False, anchor="lm")
    text(d, (1220, 780), "（战斗同名恒偶数张，移除也不落单）", size=12, fill=SUB,
         bold=False, anchor="lm")
    panel(img, [1520, 860, 1800, 916], 8, fill=GOLD, outline=(140, 105, 50, 255), width=2)
    text(d, (1660, 888), "选择牌牌 · 75G", size=16, anchor="mm")
    return img, "mockup_s07_shop.png"


def s08_campfire():
    """S08 篝火（09 §7.3）：篝火 + 休息/升级二选一。"""
    base = asset("bg_campfire.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 90), "篝火", size=34, anchor="mm")
    # 篝火：圆木 + 大火焰 + 暖光（动画的静态表达）
    for ang, x0 in ((24, 820), (-24, 1060)):
        d.rounded_rectangle([x0 - 90, 316, x0 + 90, 348], 16, fill=(160, 112, 62, 255),
                            outline=INK, width=2)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse([W // 2 - 170, 190, W // 2 + 170, 380],
                                 fill=(255, 190, 90, 110))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(40)))
    icon(img, "icon_status_burn.png", W // 2, 240, 210)
    panel(img, [560, 470, 1360, 890], 14)
    text(d, (960, 516), "你要做什么？", size=22, anchor="mm")
    for i, (title, desc, glyph) in enumerate((
            ("休息", "回复 30% 最大生命（18/60）", "heart"),
            ("升级", "强化牌库中的一张卡牌", "arrow"))):
        x = 640 + i * 360
        panel(img, [x, 570, x + 320, 820], 12, fill=BRIGHT, outline=GOLD, width=3)
        d = ImageDraw.Draw(img)
        cx, cy = x + 160, 650
        if glyph == "heart":
            icon(img, "icon_hp.png", cx, cy, 64)
        else:
            d.polygon([(cx, cy - 36), (cx + 30, cy), (cx + 10, cy), (cx + 10, cy + 34),
                       (cx - 10, cy + 34), (cx - 10, cy), (cx - 30, cy)],
                      fill=GREEN, outline=INK)
        text(d, (cx, 726), title, size=22, anchor="mm")
        text(d, (cx, 768), desc, size=13, fill=SUB, bold=False, anchor="mm")
    return img, "mockup_s08_campfire.png"


def s09_event():
    """S09 事件（09 §7.4）：事件插图区 + 叙事面板 + 三选项。"""
    base = asset("bg_event.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 76), "神秘事件", size=32, anchor="mm")
    # 事件插图区（400×200，按 09 §7.4；插画待补，拱形底纹占位）
    panel(img, [W // 2 - 200, 120, W // 2 + 200, 320], 12, fill=BRIGHT)
    d = ImageDraw.Draw(img)
    d.arc([W // 2 - 130, 140, W // 2 + 130, 300], 180, 360, fill=TEAL, width=4)
    d.arc([W // 2 - 70, 170, W // 2 + 70, 300], 180, 360, fill=BORDER, width=3)
    text(d, (W // 2, 286), "事件插图", size=12, fill=SUB, bold=False, anchor="mm")
    panel(img, [620, 360, 1300, 560], 12)
    d = ImageDraw.Draw(img)
    for i, ln in enumerate(("「你在记忆回廊中发现一本古老的日记。",
                            "　 翻开它，一股力量涌入脑海……」")):
        text(d, (W // 2, 424 + i * 40), ln, size=18, bold=False, anchor="mm")
    options = (("仔细阅读", "获得 1 张随机卡牌，失去 3 点生命", "book"),
               ("快速翻阅", "获得 15 金币", "coin"),
               ("离开", "无事发生", "door"))
    for i, (title, desc, glyph) in enumerate(options):
        y = 604 + i * 128
        panel(img, [620, y, 1300, y + 104], 12, fill=BRIGHT, outline=BORDER, width=2)
        d = ImageDraw.Draw(img)
        cx, cy = 700, y + 52
        if glyph == "coin":
            icon(img, "icon_gold.png", cx, cy, 44)
        elif glyph == "book":
            d.rounded_rectangle([cx - 26, cy - 20, cx + 26, cy + 22], 6,
                                fill=(248, 242, 227, 255), outline=INK, width=2)
            d.line([cx, cy - 20, cx, cy + 22], fill=INK, width=2)
        else:
            d.rounded_rectangle([cx - 18, cy - 24, cx + 18, cy + 24], 8,
                                fill=(181, 132, 84, 255), outline=INK, width=2)
            d.ellipse([cx + 4, cy - 4, cx + 10, cy + 2], fill=GOLD)
        text(d, (760, y + 38), title, size=19)
        text(d, (760, y + 72), desc, size=13, fill=SUB, bold=False)
    return img, "mockup_s09_event.png"


def s10_bossrelic():
    """S10 Boss遗物奖励（09 §8.3）：三选一 Boss 遗物。"""
    base = asset("bg_battle.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    ov = Image.new("RGBA", img.size, (0, 0, 0, 115))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    text(d, (W // 2, 150), "Boss 已击败！", size=42, fill=GOLD, anchor="mm")
    text(d, (W // 2, 212), "选择一件 Boss 遗物", size=20, fill=CREAM, bold=False, anchor="mm")
    relics = (("eye", "全知之眼", ("场上可同时翻开的", "牌数量 +1")),
              ("swirl", "混沌核心", ("每回合开始时随机", "交换 2 张牌位置")),
              ("crown", "记忆王冠", ("所有能力牌的", "持续效果翻倍")))
    for i, (glyph, name, lines) in enumerate(relics):
        x = W // 2 + (i - 1) * 460
        panel(img, [x - 200, 300, x + 200, 720], 14)
        d = ImageDraw.Draw(img)
        relic_glyph(d, x, 440, 78, glyph)
        text(d, (x, 560), name, size=22, anchor="mm")
        chip(d, x - 34, 590, "Boss", (232, 123, 53, 255), size=12, h=24)
        for j, ln in enumerate(lines):
            text(d, (x, 650 + j * 30), ln, size=14, bold=False, anchor="mm")
    text(d, (W // 2, 800), "Boss 遗物全场唯一，选定后立即生效", size=13, fill=CREAM,
         bold=False, anchor="mm")
    return img, "mockup_s10_bossrelic.png"


def s11_victory():
    """S11 胜利结算（09 §5.1）：第三章 Boss 后的 Run 结算。"""
    base = asset("bg_menu.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    ov = Image.new("RGBA", img.size, (255, 244, 214, 90))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    logo = asset("logo_main.png")
    if logo:
        paste_fit(img, logo, W // 2, 210, 240)
    d.text((W // 2, 430), "胜  利", font=font(88), fill=INK, anchor="mm",
           stroke_width=3, stroke_fill=GOLD)
    text(d, (W // 2, 512), "记忆殿堂恢复了宁静，你找回了全部记忆", size=20,
         fill=(96, 84, 62, 255), bold=False, anchor="mm")
    panel(img, [660, 580, 1260, 830], 14)
    for i, (label, val) in enumerate((("到达章节", "第 3 章 · 通关"),
                                      ("击败敌人", "18"), ("获得金币", "320"),
                                      ("剩余生命", "42 / 60"))):
        text(d, (760, 620 + i * 46), label, size=16, bold=False, anchor="lm")
        text(d, (1160, 620 + i * 46), val, size=16, anchor="rm")
    panel(img, [W // 2 - 260, 880, W // 2 - 10, 944], 10, fill=GOLD,
          outline=(140, 105, 50, 255), width=3)
    text(d, (W // 2 - 135, 912), "再来一局", size=19, anchor="mm")
    panel(img, [W // 2 + 10, 880, W // 2 + 260, 944], 10, fill=BRIGHT, outline=BORDER, width=2)
    text(d, (W // 2 + 135, 912), "返回主菜单", size=19, anchor="mm")
    return img, "mockup_s11_victory.png"


def s12_pause():
    """S12 暂停菜单（09 §9.4）：模态面板四按钮。"""
    base = asset("bg_battle.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    ov = Image.new("RGBA", img.size, (0, 0, 0, 140))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    panel(img, [W // 2 - 240, 300, W // 2 + 240, 820], 14)
    text(d, (W // 2, 356), "暂停", size=30, anchor="mm")
    panel(img, [W // 2 - 180, 410, W // 2 + 180, 466], 10, fill=GOLD,
          outline=(140, 105, 50, 255), width=3)
    text(d, (W // 2, 438), "继续", size=19, anchor="mm")
    for i, label in enumerate(("查看牌库", "设置")):
        y = 496 + i * 76
        panel(img, [W // 2 - 180, y, W // 2 + 180, y + 56], 10, fill=BRIGHT,
              outline=BORDER, width=2)
        text(d, (W // 2, y + 28), label, size=18, anchor="mm")
    panel(img, [W // 2 - 180, 648, W // 2 + 180, 704], 10, fill=RED,
          outline=(120, 30, 30, 255), width=2)
    text(d, (W // 2, 676), "放弃当前 Run", size=18, fill=WHITE, anchor="mm")
    text(d, (W // 2, 764), "时间已暂停（timeScale = 0）", size=13, fill=SUB,
         bold=False, anchor="mm")
    return img, "mockup_s12_pause.png"


def s13_settings():
    """S13 设置（09 §5.1）：音量/画质/按键模态。"""
    base = asset("bg_menu.png") or Image.new("RGBA", (W, H), CREAM)
    img = base.copy()
    ov = Image.new("RGBA", img.size, (0, 0, 0, 120))
    img.alpha_composite(ov)
    d = ImageDraw.Draw(img)
    panel(img, [W // 2 - 330, 180, W // 2 + 330, 950], 14)
    text(d, (W // 2, 236), "设置", size=30, anchor="mm")
    text(d, (W // 2 - 270, 300), "音频", size=17)
    slider(d, W // 2 - 270, 372, 420, 0.7, "主音量", "70%")
    slider(d, W // 2 - 270, 452, 420, 0.8, "音效", "80%")
    d = ImageDraw.Draw(img)
    d.line([W // 2 - 270, 512, W // 2 + 270, 512], fill=BORDER, width=1)
    text(d, (W // 2 - 270, 546), "画质", size=17)
    for i, lv in enumerate(("低", "中", "高")):
        x = W // 2 - 270 + i * 150
        active = lv == "中"
        panel(img, [x, 580, x + 130, 630], 10,
              fill=GOLD if active else BRIGHT,
              outline=(140, 105, 50, 255) if active else BORDER, width=2)
        text(d, (x + 65, 605), lv, size=16, anchor="mm")
    d = ImageDraw.Draw(img)
    d.line([W // 2 - 270, 676, W // 2 + 270, 676], fill=BORDER, width=1)
    text(d, (W // 2 - 270, 710), "按键", size=17)
    for i, (act, key) in enumerate((("翻牌", "鼠标左键"), ("暂停", "Esc"), ("牌库", "D"))):
        yy = 752 + i * 40
        text(d, (W // 2 - 270, yy), act, size=15, bold=False, anchor="lm")
        panel(img, [W // 2 + 60, yy - 18, W // 2 + 270, yy + 18], 8, fill=SAND,
              outline=BORDER, width=1, shadow=False)
        text(d, (W // 2 + 165, yy), key, size=14, bold=False, anchor="mm")
    panel(img, [W // 2 - 110, 880, W // 2 + 110, 932], 10, fill=BRIGHT,
          outline=BORDER, width=2)
    text(d, (W // 2, 906), "关闭", size=17, anchor="mm")
    return img, "mockup_s13_settings.png"


SCREENS = {
    "s01": s01_menu, "s02": s02_select, "s03": s03_battle, "s04": s04_map,
    "s05": s05_reward, "s06": s06_deck, "s07": s07_shop, "s08": s08_campfire,
    "s09": s09_event, "s10": s10_bossrelic, "s11": s11_victory, "s12": s12_pause,
    "s13": s13_settings,
}


def main():
    ap = argparse.ArgumentParser(description="Memory Hero UI mockup compositor")
    ap.add_argument("screens", nargs="*", help="s01 s03 s04 s05（默认全部）")
    ap.add_argument("--publish", action="store_true",
                    help="把 ImageReview/mockups/ 全部发布到 Assets/UI/mockups/"
                         "（仅在用户拍板确认后执行）")
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
        dst_dir = os.path.join(ASSETS, "mockups")
        os.makedirs(dst_dir, exist_ok=True)
        for f in sorted(os.listdir(REVIEW_DIR)):
            if f.startswith("mockup_") and f.endswith(".png"):
                shutil.move(os.path.join(REVIEW_DIR, f), os.path.join(dst_dir, f))
                print(f"Published: {f} -> {dst_dir}")


if __name__ == "__main__":
    main()
