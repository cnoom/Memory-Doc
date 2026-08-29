#!/usr/bin/env python3
"""卡背/卡框发布前处理——《记忆勇者》卡形定稿。

两条路径：
- --compose-type TYPE  【当前主路径·分层合成】程序描边环（RING_PALETTES，
  逐层圆角矩形，宽度/颜色精确可控，四类型绝对等粗色准）+ 源图内容层
  （内缩 30px 取纯卡面区，等比贴入、奶油单色延伸补宽，零重绘零变形）。
  详见 compose_card 与 references/frame-pipeline-pitfalls.md。
- （旧）--fit-34 源图像素路径：内容掩膜裁切/等比拉伸/渐变重绘——历经
  多轮修复仍难兼顾质感与规整，仅作回退保留。
- 默认：卡背等满幅设计，居中裁 3:4 + 60px 圆角透明角。
"""

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RADIUS = 60  # @1024 宽；480 显示时约 28px


def _bg_color(im):
    """画布底色：四角 8px 内采样均值（安全区生成时框体外是纯画布底）。"""
    w, h = im.size
    px = im.load()
    pts = [(4, 4), (w - 5, 4), (4, h - 5), (w - 5, h - 5)]
    return tuple(sum(px[x, y][i] for x, y in pts) // 4 for i in range(3))


def _content_mask(im, bg, tol=78):
    """卡体内容掩膜（bool 数组）：色描边区域。

    内容 = 色差超阈 且 满足任一：①高饱和（attack 红/skill 藏青/金线等
    彩色描边）；②暗色低饱和实带（ability 暗紫边带 sat≈32、诅咒炭黑——
    它们是边带本体而非阴影，画布底 sum≈700 自然排除）。再排除 AI 画在
    框体外侧、贯穿全高/全宽的近黑轮廓线（sum<60 行列）。
    """
    import numpy as np
    a = np.asarray(im.convert("RGB"), dtype=np.int32)
    diff = np.abs(a - np.array(bg, dtype=np.int32)).sum(axis=2)
    sat = a.max(axis=2) - a.min(axis=2)
    sumv = a.sum(axis=2)
    mask = (diff > tol) & ((sat > 60) | (sumv < 450))
    dark = sumv < 60
    mask[:, dark.mean(axis=0) > 0.7] = False   # 贯穿全高的黑线列
    mask[dark.mean(axis=1) > 0.7, :] = False   # 贯穿全宽的黑线行
    return mask


def _content_bbox(im, bg, tol=78):
    """色描边外缘包围盒（=卡框边界）。"""
    import numpy as np
    ys, xs = np.nonzero(_content_mask(im, bg, tol))
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _creamish(a):
    """卡面奶油色判定（numpy 数组，RGB int）。"""
    return (np.abs(a[..., 0] - 248) < 30) & (np.abs(a[..., 1] - 237) < 30)         & (np.abs(a[..., 2] - 215) < 35)


def _creamish(a):
    """卡面奶油色判定（numpy 数组，RGB int）。"""
    return (np.abs(a[..., 0] - 248) < 30) & (np.abs(a[..., 1] - 237) < 30)         & (np.abs(a[..., 2] - 215) < 35)


def _max_edge_band(rgb):
    """最大边带宽：全体行/列从边缘到首个卡面奶油像素的距离最大值。

    源图 AI 描边宽度沿边不均（局部段可达均值的 2-3 倍），内缩量按最大值
    取才能保证内容层不含边带残余；重绘/环带深度同理。
    """
    c = _creamish(rgb)
    h, w = rgb.shape[:2]
    mx = 0
    for y in range(h):
        nz = np.flatnonzero(c[y])
        if nz.size:
            mx = max(mx, int(nz[0]), int(w - 1 - nz[-1]))
    for x in range(w):
        nz = np.flatnonzero(c[:, x])
        if nz.size:
            mx = max(mx, int(nz[0]), int(h - 1 - nz[-1]))
    return mx


def _min_edge_band(body_rgb):
    """边带宽度：中线四向从边缘向内到第一个奶油像素的距离，取最小。"""
    h, w = body_rgb.shape[:2]

    def scan(line):
        c = _creamish(line)
        nz = np.flatnonzero(c)
        return int(nz[0]) if nz.size else 150

    return min(scan(body_rgb[h // 2, :]), scan(body_rgb[h // 2, ::-1]),
               scan(body_rgb[:, w // 2]), scan(body_rgb[::-1, w // 2]))


def _grow_edge(arr, t):
    """掩膜向外生长 t 圈：每圈用当前最外行/列延伸（角部复制角像素）。

    仅用于布尔掩膜（无纹理，逐圈复制无伪影）；RGB 颜色带的加粗走
    _smooth_band_fill（逐圈复制会把边缘像素起伏拉成放射条纹）。
    """
    for _ in range(t):
        top, bot = arr[:1], arr[-1:]
        left, right = arr[:, :1], arr[:, -1:]
        arr = np.vstack([
            np.hstack([arr[:1, :1], top, arr[:1, -1:]]),
            np.hstack([left, arr, right]),
            np.hstack([arr[-1:, :1], bot, arr[-1:, -1:]]),
        ])
    return arr


def _smooth_band_fill(body, t):
    """边带加粗的最终方案：生长区填"沿边方向强平滑的均值带"，无径向条纹。

    逐圈最近邻复制会把源图描边边缘的像素起伏拉成放射条纹（用户指出的
    "辅助线"——attack/skill/curse 生长 9-14 圈全部中招，ability 1 圈无恙）。
    改为：取四边最外 3px 的行/列均值 → 41px 窗沿边平滑（保留描边沿边的
    大趋势渐变、消除 ±2px 起伏）→ 端部外推 → 四带拼装（左右带全高覆盖
    角区，角部为平滑描边色）。
    """
    h, w = body.shape[:2]
    k = 41

    trim = 60  # 两端圆角弧区：bbox 角像素含画布底/过渡色，生长会沿边复制出亮缝

    def edge_seq(strip):
        seq = strip.astype(float).mean(axis=1)[trim:-trim]
        pad = np.pad(seq, ((k, k), (0, 0)), mode="edge")
        c = np.cumsum(pad, axis=0)
        return (c[2 * k:] - c[:-2 * k]) / (2 * k)

    def ext(seq, total):
        pad_l = (total - len(seq)) // 2
        pad_r = total - len(seq) - pad_l
        return np.vstack([np.repeat(seq[:1], pad_l, 0), seq,
                          np.repeat(seq[-1:], pad_r, 0)])

    def band(seq, n):
        return np.repeat(seq[:, None, :], t, axis=1)

    L = edge_seq(body[:, :3]); R = edge_seq(body[:, -3:])
    T = edge_seq(body[:3].transpose(1, 0, 2)); B = edge_seq(body[-3:].transpose(1, 0, 2))
    H2, W2 = h + 2 * t, w + 2 * t
    canvas = np.zeros((H2, W2, 3), dtype=float)
    canvas[:, :t] = band(ext(L, H2), t)
    canvas[:, -t:] = band(ext(R, H2), t)
    canvas[t:t + h, t:t + w] = body
    canvas[:t, t:t + w] = np.repeat(ext(T, W2)[t:-t][None, :, :], t, axis=0)
    canvas[t + h:, t:t + w] = np.repeat(ext(B, W2)[t:-t][None, :, :], t, axis=0)
    return np.rint(canvas).astype(body.dtype)



def _redraw_band(card_rgb, mask, band_px=50, main_rgb=(139, 44, 44), light_rgb=(212, 69, 69)):
    """边带重绘为五段规整立体描边：外缘色→主色→高光→暗线→卡面奶油。

    颜色**锚定 10 §1.2 卡牌类型色板**（main=色板主色、hi=色板亮色，
    outer/sh 为其深/暗变体）——不再从源图采样：源图描边的勾线深色、
    中位混合与手绘高光正是重绘后色偏的根源（复盘文档 #14）。
    抹掉 AI 手绘的断续高光/杂线（"辅助线"）；深度 band_px 须覆盖边带
    与柱头金饰延伸段、止于金线效果框竖线之前。
    """
    h, w = mask.shape
    any_row = mask.any(axis=1)
    any_col = mask.any(axis=0)
    left = np.where(any_row, mask.argmax(axis=1), 0)
    right = np.where(any_row, w - 1 - mask[:, ::-1].argmax(axis=1), w - 1)
    top = np.where(any_col, mask.argmax(axis=0), 0)
    bot = np.where(any_col, h - 1 - mask[::-1].argmax(axis=0), h - 1)
    yy, xx = np.mgrid[0:h, 0:w]
    dl = xx - left[yy]
    dr = right[yy] - xx
    dt = yy - top[xx]
    db = bot[xx] - yy
    d = np.minimum(np.minimum(dl, dr), np.minimum(dt, db))

    def full(v):
        return np.broadcast_to(np.array(v, dtype=float), (h, w, 3))

    main = full(main_rgb)
    outer = main * 0.72
    hi = full(light_rgb)
    sh = main * 0.65
    inner = full((249.0, 234.0, 206.0))

    t = np.clip(d / band_px, 0, 1)[..., None]
    col = np.zeros((h, w, 3))
    tf = t[..., 0]
    segs = [(0.0, 0.16, outer, main), (0.16, 0.62, main, main),
            (0.62, 0.72, main, hi), (0.72, 0.80, hi, sh),
            (0.80, 0.88, sh, inner), (0.88, 1.01, inner, inner)]
    for p0, p1, c0, c1 in segs:
        m = (tf >= p0) & (tf < p1)
        if not m.any():
            continue
        tt = ((tf[m] - p0) / (p1 - p0))[..., None]
        col[m] = c0[m] + (c1 - c0)[m] * tt
    out = card_rgb.astype(float).copy()
    zone = d < band_px
    out[zone] = col[zone]
    return np.rint(out).astype(np.uint8)



# ---- 分层合成（compose）：程序描边环 + 源图内容层，替代像素重绘 ----
# 描边环色标（由外到内，(RGB, 宽px)）：主/亮色锚定 10 §1.2 类型色板，
# 宽度程序控制——四类型绝对等粗、绝对色准；框体艺术（拱窗/柱/金饰/效果区）
# 为独立内容层按像素搬移，零重绘零变形。
RING_PALETTES = {
    "attack":  [((100, 32, 32), 6), ((139, 44, 44), 10), ((212, 69, 69), 5), ((111, 35, 35), 5)],
    "skill":   [((31, 52, 97), 6), ((44, 74, 139), 10), ((69, 119, 212), 5), ((35, 59, 111), 5)],
    "ability": [((66, 32, 100), 6), ((91, 44, 139), 15), ((212, 168, 87), 5)],
    "curse":   [((41, 41, 43), 8), ((58, 58, 60), 18)],
}
RING_RADIUS = 60
CREAM = (249, 234, 206)


def punch_arch_window(card, band_px=26, tol_ch=14, dilate=3):
    """拱形插画窗镂空：窗内净底区 alpha=0，动态插画由引擎在窗下垫层。

    窗区提取：拱窗中心采样净底色 → 逐通道容差二值 → **种子区域生长**
    （与已区域邻接差判定，容忍窗底渐变暗角；PIL floodfill 的"与种子点
    比色"会被渐变截断，故自写迭代膨胀）→ 逐行 span 填充（拱形凸体，
    连窗内云/塔影等装饰一并纳入）→ 膨胀 dilate px 覆盖暗角边。
    容差取紧值 14：窗台附近薄荷→奶油渐变桥会在宽松容差下把窗区泄漏到卡底（已踩坑）；
    洞略小于真窗、边缘留渐变环，插画垫层下不可见。
    """
    rgb = np.asarray(card.convert("RGB")).astype(int)
    h, w = rgb.shape[:2]
    sx, sy = w // 2, int(h * 0.42)
    ref = rgb[sy, sx]
    base = (np.abs(rgb - ref) < tol_ch).all(axis=2)
    m = np.zeros_like(base)
    m[sy - 2:sy + 3, sx - 2:sx + 3] = base[sy - 2:sy + 3, sx - 2:sx + 3]
    for _ in range(400):                      # 区域生长（邻接扩张，容忍渐变）
        grown = m.copy()
        grown[1:, :] |= m[:-1, :]
        grown[:-1, :] |= m[1:, :]
        grown[:, 1:] |= m[:, :-1]
        grown[:, :-1] |= m[:, 1:]
        grown &= base
        grown[0, :] = grown[-1, :] = False
        grown[:, 0] = grown[:, -1] = False
        if (grown == m).all():
            break
        m = grown
    # 洞形用参数化拱形（bbox 内缩 4px：半椭圆拱顶+矩形身），而非生长结果
    # 本身——窗底渐变的等色线会把逐容差区域限制成菱形（已踩坑）。
    ys, xs = np.nonzero(m)
    if not ys.size:
        return card
    bx0, by0 = int(xs.min()) + 4, int(ys.min()) + 4
    bx1 = int(xs.max()) + 1 - 4
    # 下缘不依赖色连通（窗台下薄荷→奶油渐变桥在任意容差内连通、本质无界），
    # 锚定结构线：窗台=效果区金框顶线（金色横行检测，源图实测 y≈460@480）
    gold = ((np.abs(rgb[..., 0] - 212) < 45) & (np.abs(rgb[..., 1] - 168) < 45)
            & (np.abs(rgb[..., 2] - 87) < 55))
    rowgold = gold[:, w // 4: 3 * w // 4].mean(axis=1)
    cand = [y for y in range(h // 2, h) if rowgold[y] > 0.5]
    by1 = min(int(ys.max()) + 1 - 4, (cand[0] - 4) if cand else h - 4)
    arc_h = max((bx1 - bx0) // 2, 8)
    cy = by0 + arc_h
    hole = np.zeros((h, w), bool)
    yy, xx = np.mgrid[0:h, 0:w]
    ell = (((xx - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2)) ** 2
           + ((yy - cy) / arc_h) ** 2) <= 1
    hole |= (yy <= cy) & ell
    hole |= (yy > cy) & (yy <= by1) & (xx >= bx0) & (xx <= bx1)
    alpha = np.asarray(card.getchannel("A")).copy()
    fade = Image.fromarray(((~hole) * 255).astype("uint8"), "L")
    fade = fade.filter(ImageFilter.GaussianBlur(1.0))
    alpha = np.minimum(alpha, np.asarray(fade))
    card.putalpha(Image.fromarray(alpha, "L"))
    return card


def compose_card(im, type_key):
    """分层合成定稿卡：程序描边环 + 源图内容层。

    1. 内容掩膜定 bbox，裁出含边带 body；
    2. 内缩（最大边带宽+2px）取纯卡面内容层——边带及其附属装饰（含金饰
       延伸段）整体留在描边环一侧，由程序环替代；
    3. 逐层绘制同心圆角描边环（环宽=色标宽度，四类型绝对等粗色准）；
    4. 内容层等比贴入内区（本方案 scale≈1 零拉伸），宽度不足处用卡面
       奶油单色延伸（内容层边缘即奶油，平色无缝）；
    5. 内区与整卡几何圆角 alpha。
    """
    bg = _bg_color(im)
    m = _content_mask(im, bg)
    ys, xs = np.nonzero(m)
    x0, y0 = int(xs.min()), int(ys.min())
    x1, y1 = int(xs.max()) + 1, int(ys.max()) + 1
    body = im.crop((x0, y0, x1, y1))
    inset = 30  # 固定内缩：≥ 全类型边带宽（≤30px，含 ability 金线），内容层零边带残余；
    #            不可用"到首奶油像素的距离"自适应——拱肩等卡面内部结构会干扰测量
    inner = body.crop((inset, inset, body.width - inset, body.height - inset))

    rings = RING_PALETTES[type_key]
    t = sum(wd for _, wd in rings)
    H2 = inner.height + 2 * t
    W2 = int(round(H2 * 3 / 4))

    card = Image.new("RGB", (W2, H2))
    dr = ImageDraw.Draw(card)
    off = 0
    for col, wd in rings:
        dr.rounded_rectangle([off, off, W2 - 1 - off, H2 - 1 - off],
                             max(RING_RADIUS - off, 6), fill=col)
        off += wd
    inner_r = max(RING_RADIUS - t, 6)
    dr.rounded_rectangle([t, t, W2 - 1 - t, H2 - 1 - t], inner_r, fill=CREAM)

    iw2, ih2 = W2 - 2 * t, H2 - 2 * t
    scale = ih2 / inner.height
    inner_s = inner.resize((max(int(round(inner.width * scale)), 1), ih2), Image.LANCZOS)
    if inner_s.width < iw2:
        pad = (iw2 - inner_s.width) // 2
        lcol = tuple(int(v) for v in np.asarray(inner_s)[:, 0].mean(axis=0))
        rcol = tuple(int(v) for v in np.asarray(inner_s)[:, -1].mean(axis=0))
        ext = Image.new("RGB", (iw2, ih2), lcol)
        ext.paste(inner_s, (pad, 0))
        if iw2 - pad - inner_s.width > 0:
            rstrip = Image.new("RGB", (iw2 - pad - inner_s.width, ih2), rcol)
            ext.paste(rstrip, (pad + inner_s.width, 0))
        inner_s = ext
    msk = Image.new("L", (inner_s.width, ih2), 0)
    ImageDraw.Draw(msk).rounded_rectangle([0, 0, iw2 - 1, ih2 - 1], inner_r, fill=255)
    card.paste(inner_s, (t, t), msk)

    card = card.convert("RGBA")
    am = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(am).rounded_rectangle([0, 0, W2 - 1, H2 - 1], RING_RADIUS, fill=255)
    card.putalpha(am)
    punch_arch_window(card)
    return card


def fit_34(im, unify_edge=0, redraw_band=False, band_main=None, band_hi=None):
    """以色描边为卡缘定稿 3:4：裁到描边外缘，横向等比拉伸到 3:4，
    圆角 alpha 由内容掩膜贴合生成（几何圆角蒙版会斜切角部描边）。

    unify_edge=N：四类型边带宽度统一——窄于 N 的框用最近邻边缘生长把
    描边加粗到 N（圆角同心外扩），宽于 N 的不动；N 为源图像素尺度。
    用户定稿（2026-08-29）：有颜色的那层描边就是卡框边，且四类型描边
    等粗。曾用边缘色补条补比例（描边加粗不均+假边）、60px 几何圆角
    蒙版（斜切角部描边），均已废弃。
    """
    bg = _bg_color(im)
    m = _content_mask(im, bg)
    ys, xs = np.nonzero(m)
    x0, y0, x1, y1 = int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1
    body_m = m[y0:y1, x0:x1]
    body = np.asarray(im.crop((x0, y0, x1, y1)).convert("RGB"))
    grow_t = 0
    if unify_edge > 0:
        grow_t = max(unify_edge - _min_edge_band(body), 0)
        if grow_t > 0:
            body = _smooth_band_fill(body, grow_t)
            body_m = _grow_edge(body_m.astype(np.uint8), grow_t).astype(bool)
    bh, bw = body.shape[:2]
    W, H = bw, int(round(bw * 4 / 3))
    if H < bh:
        W, H = int(round(bh * 3 / 4)), bh

    card = Image.fromarray(body.astype("uint8"), "RGB").resize((W, H), Image.LANCZOS).convert("RGBA")
    # alpha = 内容掩膜同比例缩放 → 逐行 span 填充成实心卡体（凸形）→ 羽化
    mm = Image.fromarray((body_m * 255).astype("uint8"), "L").resize((W, H), Image.LANCZOS)
    ma = np.asarray(mm) > 96
    for y in range(H):
        row = ma[y]
        nz = np.flatnonzero(row)
        if nz.size:
            row[nz[0]:nz[-1] + 1] = True
    if redraw_band:
        # 重绘深度固定 50px：覆盖边带（26px）与柱头金饰延伸段（深至 ~45px，
        # 其浅金色与卡面奶油色板重叠、颜色检测不可分），并止于金线效果框
        # 竖线（距卡缘 54px）之前
        rgb = _redraw_band(np.asarray(card.convert("RGB")), ma, band_px=50,
                           main_rgb=band_main or (139, 44, 44),
                           light_rgb=band_hi or (212, 69, 69))
        card = Image.fromarray(rgb, "RGB").convert("RGBA")
        # 重绘带为参数化渐变，几何圆角（描边圆角 45px + 生长量 t）完美适配；
        # 内容掩膜在 curse 等框的角部有色差盲区缺口，redraw 路径弃用
        gm = Image.new("L", (W, H), 0)
        ImageDraw.Draw(gm).rounded_rectangle([0, 0, W - 1, H - 1], 45 + grow_t, fill=255)
        card.putalpha(gm.filter(ImageFilter.GaussianBlur(1.0)))
        return card
    alpha = Image.fromarray((ma * 255).astype("uint8"), "L").filter(ImageFilter.GaussianBlur(1.2))
    card.putalpha(alpha)
    return card


def roundify(path, corner=0, band=None, fit=False, unify_edge=0, redraw=False, band_main=None, band_hi=None, compose_type=None):
    im = Image.open(path).convert("RGBA")
    if compose_type:
        im = compose_card(im, compose_type)
    elif fit:
        im = fit_34(im, unify_edge, redraw, band_main, band_hi)
    w, h = im.size
    th = int(w * 4 / 3)
    if not fit and h > th:
        top = (h - th) // 2
        im = im.crop((0, top, w, top + th))
        w, h = im.size

    if corner:
        bx, by = band
        px = im.load()
        band_rgb = px[bx, by][:3]
        c = corner
        squares = [(0, 0), (w - c, 0), (0, h - c), (w - c, h - c)]
        for x0, y0 in squares:
            for y in range(y0, y0 + c):
                for x in range(x0, x0 + c):
                    px[x, y] = (*band_rgb, px[x, y][3])

    if not fit and not compose_type:
        # 卡背等满幅设计：几何圆角裁角。fit_34/compose 路径的 alpha 已自足
        # （内容掩膜贴合 / 程序环+镂空窗），此处不再覆盖。
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1], RADIUS, fill=255)
        im.putalpha(mask)
    im.save(path)
    print(f"{path}: {w}x{h} radius={'content-mask' if fit else RADIUS} fit34={fit} corner={corner or 'off'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="+", help="asset PNG paths (in place)")
    ap.add_argument("--compose-type", choices=["attack", "skill", "ability", "curse"],
                    help="layered compose mode: program-drawn ring border + source content layer")
    ap.add_argument("--band-main", default="139,44,44",
                    help="edge band main color R,G,B (10 §1.2 type palette)")
    ap.add_argument("--band-hi", default="212,69,69",
                    help="edge band highlight color R,G,B (type palette light)")
    ap.add_argument("--redraw-band", action="store_true",
                    help="repaint the edge band as a smooth radial gradient (removes the "
                         "AI-drawn inner highlight line); skip for frames with inner "
                         "decorative lines worth keeping")
    ap.add_argument("--unify-edge", type=int, default=0,
                    help="normalize edge band width to N px (source scale) by growing "
                         "thin bands outward; 0=keep as generated")
    ap.add_argument("--fit-34", action="store_true",
                    help="trim to content bbox then pad canvas color to 3:4 (for frames "
                         "with safe-area margins); without it, center-crop 2:3 to 3:4")
    ap.add_argument("--corner", type=int, default=0,
                    help="corner square size to normalize into band color (0=off)")
    ap.add_argument("--band-x", type=int, default=0, help="band color sample x")
    ap.add_argument("--band-y", type=int, default=0, help="band color sample y")
    args = ap.parse_args()
    if args.corner and not (args.band_x or args.band_y):
        sys.exit("Error: --corner needs --band-x/--band-y sample point on the band")
    for p in args.paths:
        if not os.path.isfile(p):
            sys.exit(f"Error: not a file: {p}")
        roundify(p, args.corner, (args.band_x, args.band_y), fit=args.fit_34,
                 unify_edge=args.unify_edge, redraw=args.redraw_band,
                 band_main=tuple(float(v) for v in args.band_main.split(",")),
                 band_hi=tuple(float(v) for v in args.band_hi.split(",")),
                 compose_type=args.compose_type)


if __name__ == "__main__":
    main()
