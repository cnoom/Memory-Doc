#!/usr/bin/env python3
"""《记忆勇者》设计文档仓库资产生成包装器（mh-art）。

复用用户级 germmc-image2 技能脚本的 API 通道（key 解析/HTTP/重试），叠加项目预设：
按 --type 套用规格表的尺寸、风格片段、透明底、缩放、命名。

三目录工作流（详见 SKILL.md 与 ImageReview/README.md）:
    生成  -> 默认落 ImageReview/<类型>/ 预览区，供人工校验（不进 git）
    归档  -> --archive 把被取代的候选移入 ImageReview/_archived/<日期>/<类型>/（只进不出）
    发布  -> --publish 把校验通过的文件移动到 docs/design/assets/（扁平无子目录，
             文件名自带类别前缀；进 git，供文档嵌入）

用法（仓库根目录下运行）:
    python .agents/skills/mh-art/scripts/gen_asset.py --type relic --name relic_memory_crystal --desc "..."
    python .agents/skills/mh-art/scripts/gen_asset.py --type card --name card_attack_biji --desc "..." --n 2
    python .agents/skills/mh-art/scripts/gen_asset.py --archive ImageReview/cards/old.png
    python .agents/skills/mh-art/scripts/gen_asset.py --publish ImageReview/relics/relic_memory_crystal_1.png
    python .agents/skills/mh-art/scripts/gen_asset.py --publish ImageReview/relics   # 整目录发布

环境变量:
    IMAGE2_SKILL_DIR  germmc-image2 技能目录（默认按本机用户路径解析）
    IMAGE2_API_KEY    同 base 脚本，覆盖 key 解析
"""

import argparse
import base64
import datetime
import json
import os
import re
import shutil
import sys
import time

REVIEW_ROOT = "ImageReview"
ARCHIVE_ROOT = os.path.join(REVIEW_ROOT, "_archived")
ASSETS_ROOT = os.path.join("docs", "design", "assets")

# ---- 项目规格表（与 SKILL.md 保持同步）----
# 风格 v3（2026-08-25，已拍板）：v1 暗黑厚涂（"过于硬核"）、v2/v2.1 温暖绘本水彩
# （"还是不太行"）相继被否决。用户给出参照：Unity Asset Store「2D Characters -
# Casual Monsters」(LAYERLAB)——扁平休闲卡通：干净矢量感圆胖轮廓、无描边、双色阶
# 阴影（底色+一层暗部）、Q 版大头比例、中饱和青绿/奶油/暖棕系、无纹理无笔触。
# 记忆殿堂主题与功能色板（卡牌类型/状态/意图/稀有度）保留，渲染语言从"绘本水彩"
# 整体切到"扁平卡通"。基础 UI 色已随 v3 调亮（见 10-UI美术资源规格 §1.1 v1.3）。
STYLE_BASE = ("flat cartoon casual mobile-game art, clean rounded vector-style shapes, cute chibi "
              "proportions, flat color fills with simple two-tone shading (one soft darker shade "
              "under each shape), no outlines, smooth clean matte finish, moderately saturated "
              "cozy palette of teal, cream and warm brown with antique-gold accents, memory-palace "
              "scholar library fantasy theme, friendly playful casual mood, "
              "no painterly brushwork, no watercolor, no storybook wash, no texture noise, "
              "no realistic rendering, no dark hardcore mood")

# 发布目录（实际应用区）：扁平无子目录——文件名自带类别前缀（prefix 字段），
# 发布时按前缀校验命名规范；仅 docs 文档仓库适用，勿再按类型嵌套。
SPECS = {
    "card": dict(size="1024x1536", transparent=False, resize=None,
                 review="cards", prefix="card_",
                 style="vertical card illustration for a casual mobile game, one cute clear focal "
                       "subject drawn large, simple flat background shapes, soft round shadow "
                       "under the subject, no text, no watermark"),
    "cardback": dict(size="1024x1536", transparent=False, resize=None,
                     review="cardbacks", prefix="cardback_",
                     style="full playing-card back design filling the whole canvas, symmetric cute "
                           "flat-cartoon emblem at center, chunky rounded border with simple "
                           "geometric ornaments, flat color field with a very subtle radial glow "
                           "behind the emblem, clean casual style, no text, no watermark"),
    "icon": dict(size="1024x1024", transparent=True, resize="256x256",
                 review="icons", prefix="icon_",
                 style="flat casual game icon, centered composition, thick rounded chunky silhouette, "
                       "instantly readable at small size, one accent color with a single soft "
                       "darker shade, plain transparent background, no text, no watermark"),
    "relic": dict(size="1024x1024", transparent=True, resize="256x256",
                  review="relics", prefix="relic_",
                  style="flat casual game icon of a small magical artifact, centered, cute stylized "
                        "prop with thick rounded chunky silhouette, one soft darker shade for "
                        "depth, plain transparent background, no text, no watermark"),
    "potion": dict(size="1024x1024", transparent=True, resize="256x256",
                   review="potions", prefix="potion_",
                   style="flat casual game icon of a cute alchemy potion bottle, centered, thick "
                         "rounded chunky silhouette, glossy flat liquid color, plain transparent "
                         "background, no text, no watermark"),
    "node": dict(size="1024x1024", transparent=True, resize="256x256",
                 review="map-nodes", prefix="node_",
                    style="flat casual map node emblem, centered, thick rounded chunky shape, "
                          "bold readable silhouette, plain transparent background, "
                          "no text, no watermark"),
    "enemy": dict(size="1024x1024", transparent=True, resize=None,
                  review="enemies", prefix="enemy_",
                  style="single cute casual-cartoon fantasy monster, full body, centered, facing "
                        "viewer, big-head chibi proportions, chunky rounded silhouette, friendly "
                        "mischievous expression, flat two-tone shading, soft round shadow under "
                        "feet, transparent background, no text, no watermark"),
    "portrait": dict(size="1024x1536", transparent=True, resize=None,
                     review="portraits", prefix="portrait_",
                     style="full body cute casual-cartoon character, centered, facing viewer, "
                           "big-head chibi proportions, friendly confident pose, chunky rounded "
                           "silhouette, flat two-tone shading, transparent background, "
                           "no text, no watermark"),
    "background": dict(size="2048x1152", transparent=False, resize="1920x1080",
                       review="backgrounds", prefix="bg_",
                       style="wide flat cartoon scene for a casual game, simple stylized "
                             "environment built from rounded shapes, layered flat colors for "
                             "gentle depth, empty center area for UI, no characters, no text, "
                             "no watermark"),
    "texture": dict(size="1024x1024", transparent=False, resize="256x256",
                    review="textures", prefix="texture_",
                    style="seamless tileable flat cartoon texture, evenly lit flat colors, "
                          "no vignette, no shadows at edges, no text, no watermark"),
}


def load_base_module():
    skill_dir = os.environ.get("IMAGE2_SKILL_DIR") or os.path.join(
        os.path.expanduser("~"), ".zcode", "skills", "germmc-image2")
    path = os.path.join(skill_dir, "scripts", "generate_image.py")
    if not os.path.isfile(path):
        sys.exit(f"Error: base script not found: {path}\n"
                 f"Set IMAGE2_SKILL_DIR to the germmc-image2 skill directory.")
    import importlib.util
    spec = importlib.util.spec_from_file_location("generate_image", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def request_with_retry(mod, payload, retries=3):
    host = mod.BASE_URL.replace("https://", "")
    key = mod.get_api_key()
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            status, data = mod._do_request(host, key, payload)
            if status == 200:
                return data
            last_err = f"HTTP {status}: {data.decode('utf-8', errors='replace')[:200]}"
            if status == 400 and b"Transparent background" in data:
                # 网关 gpt-image-2 已验证不支持 background=transparent —— 立即降级
                payload.pop("background", None)
                print("WARN: gateway rejects background=transparent, "
                      "retrying without it (output will have a solid background).",
                      file=sys.stderr)
                continue
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        print(f"Request failed (attempt {attempt}/{retries}): {last_err}", file=sys.stderr)
        if attempt < retries:
            time.sleep(2)
    sys.exit(f"All {retries} attempts failed. Last error: {last_err}")


def _review_subdir(path):
    """返回 ImageReview/<subdir>/ 的 subdir（不在校验区下返回 None）。"""
    parts = os.path.normpath(os.path.abspath(path)).split(os.sep)
    if REVIEW_ROOT in parts:
        i = parts.index(REVIEW_ROOT)
        if i + 1 < len(parts) and parts[i + 1] != "_archived":
            return parts[i + 1]
    return None


def infer_type(path):
    """从 ImageReview 路径段推断资产类型（发布/归档模式免 --type）。"""
    review_to_type = {v["review"]: k for k, v in SPECS.items()}
    sub = _review_subdir(path)
    return review_to_type.get(sub) if sub else None


def canonical_name(stem):
    """候选文件名 -> 规范资产名：去掉 _N 候选后缀，统一小写（本仓库命名全 snake_case）。"""
    return re.sub(r"_\d+$", "", stem).lower()


def downscale(path, resize):
    from PIL import Image
    w, h = (int(x) for x in resize.split("x"))
    with Image.open(path) as im:
        im.convert("RGBA").resize((w, h), Image.LANCZOS).save(path)


def check_alpha(path):
    """透明类资产校验：返回告警文本（无问题返回 None）。"""
    from PIL import Image
    with Image.open(path) as im:
        if im.mode != "RGBA":
            return f"expected transparent background but got {im.mode} (solid background, needs manual cutout)"
        lo, _ = im.getchannel("A").getextrema()
        if lo == 255:
            return "alpha channel exists but fully opaque — background is NOT transparent, needs manual cutout"
    return None


def collect_pngs(src):
    """单文件或目录 -> png 文件列表。"""
    files = ([os.path.join(src, f) for f in sorted(os.listdir(src))
              if f.lower().endswith(".png")]
             if os.path.isdir(src) else [src])
    if not files or not all(os.path.isfile(f) for f in files):
        sys.exit(f"Error: no PNG files found at: {src}")
    return files


def archive(src):
    """归档：移动到 ImageReview/_archived/<今日>/<类型子目录>/，保留原子目录结构。只进不出。"""
    if _review_subdir(src) is None:
        sys.exit(f"Error: archive source must be inside {REVIEW_ROOT}/<type>/ (got: {src})")
    sub = _review_subdir(src)
    files = collect_pngs(src)
    day = datetime.date.today().isoformat()
    dst_dir = os.path.join(ARCHIVE_ROOT, day, sub)
    os.makedirs(dst_dir, exist_ok=True)
    for f in files:
        dst = os.path.join(dst_dir, os.path.basename(f))
        if os.path.exists(dst):
            stem, ext = os.path.splitext(os.path.basename(f))
            dst = os.path.join(dst_dir, f"{stem}_{int(time.time())}{ext}")
        shutil.move(f, dst)
        print(f"Archived: {f} -> {dst}")
    print("Archived files are never published; browse by date directory to review old proposals.")


def publish(spec_key, src):
    spec = SPECS[spec_key]
    files = collect_pngs(src)
    os.makedirs(ASSETS_ROOT, exist_ok=True)
    for f in files:
        name = canonical_name(os.path.splitext(os.path.basename(f))[0])
        if not name.startswith(spec["prefix"]):
            print(f"WARN [{name}.png]: name does not start with '{spec['prefix']}' "
                  f"(naming rule: docs/design/10-UI美术资源规格.md §9)", file=sys.stderr)
        dst = os.path.join(ASSETS_ROOT, f"{name}.png")
        shutil.move(f, dst)
        print(f"Published: {f} -> {dst}")
    print("Next: 在对应设计文档里嵌入相对引用，如 ![名称](./assets/<文件>.png)；"
          "发布目录进 git，记得提交。")


def main():
    parser = argparse.ArgumentParser(description="Memory Hero (记忆勇者) doc asset image generator")
    parser.add_argument("--type", choices=sorted(SPECS),
                        help="asset type preset (publish/archive mode can infer it from the ImageReview path)")
    parser.add_argument("--name", help="asset file name (without extension, snake_case)")
    parser.add_argument("--desc", help="content description (style auto-prepended)")
    parser.add_argument("--no-style", action="store_true", help="do not prepend style fragments")
    parser.add_argument("--quality", default="medium", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--size", default=None, help="override preset size")
    parser.add_argument("--n", type=int, default=1, choices=[1, 2, 3],
                        help="number of candidates (saved as name_1.png ... in ImageReview)")
    parser.add_argument("--out", default=None,
                        help="override output file/folder path (default: ImageReview/<type dir>/)")
    parser.add_argument("--no-transparent", action="store_true",
                        help="force opaque even if the type defaults to transparent")
    parser.add_argument("--no-resize", action="store_true", help="skip preset downscale")
    parser.add_argument("--publish", nargs="?", const="", metavar="FILE",
                        help="publish mode: move reviewed ImageReview file (or whole folder) to docs/design/assets/")
    parser.add_argument("--archive", nargs="?", const="", metavar="FILE",
                        help="archive mode: move superseded ImageReview file (or whole folder) to _archived/<date>/")
    args = parser.parse_args()

    if args.archive is not None:
        src = args.archive or os.path.join(REVIEW_ROOT, args.type or "")
        if not args.type and not infer_type(src):
            sys.exit(f"Error: archive mode needs --type or an {REVIEW_ROOT}/<type dir>/... path")
        archive(src)
        return

    if args.publish is not None:
        spec_key = args.type or infer_type(args.publish or "")
        if not spec_key:
            sys.exit(f"Error: publish mode needs --type or an {REVIEW_ROOT}/<type dir>/... path")
        src = args.publish or os.path.join(REVIEW_ROOT, SPECS[spec_key]["review"])
        publish(spec_key, src)
        return

    if not args.type:
        sys.exit("Error: --type is required in generate mode")
    spec = SPECS[args.type]

    if not (args.name and args.desc):
        sys.exit("Error: --name and --desc are required in generate mode")

    name = args.name.lower()
    review_dir = args.out or os.path.join(REVIEW_ROOT, spec["review"])

    prompt = args.desc
    if not args.no_style:
        prompt = f"{STYLE_BASE}. {spec['style']}. {args.desc}"

    transparent = spec["transparent"] and not args.no_transparent

    mod = load_base_module()
    payload = {
        "model": mod.MODEL,
        "prompt": prompt,
        "size": args.size or spec["size"],
        "quality": args.quality,
        "n": args.n,
    }
    # 网关实测（2026-08-25）：n>1 会被网关转成 tools[0].n 并返回 400
    # "Unknown parameter: 'tools[0].n'"，故多候选拆成 n 次 n=1 请求。
    payload["n"] = 1
    if transparent:
        payload["background"] = "transparent"

    os.makedirs(review_dir, exist_ok=True)
    saved = []
    for i in range(args.n):
        data = request_with_retry(mod, payload)
        result = json.loads(data)
        if "data" not in result or not result["data"]:
            sys.exit(f"Unexpected API response: {json.dumps(result)[:300]}")
        item = result["data"][0]
        try:
            img_bytes = base64.b64decode(item["b64_json"])
        except (KeyError, TypeError):
            sys.exit(f"Unexpected API response (no b64_json): {json.dumps(item)[:200]}")
        fname = f"{name}.png" if args.n == 1 else f"{name}_{i + 1}.png"
        out_path = os.path.join(review_dir, fname)
        with open(out_path, "wb") as f:
            f.write(img_bytes)
        saved.append(out_path)

    resize = None if args.no_resize else spec["resize"]
    try:
        from PIL import Image  # noqa: F401  (统一在此探测，downscale/check_alpha 内部使用)
        has_pil = True
    except ImportError:
        has_pil = False
        print("WARN: PIL not available, saved at generated size (no downscale / no alpha check).",
              file=sys.stderr)

    for out_path in saved:
        if resize and has_pil:
            downscale(out_path, resize)
        if transparent and has_pil:
            warn = check_alpha(out_path)
            if warn:
                print(f"WARN [{os.path.basename(out_path)}]: {warn}", file=sys.stderr)
        print(f"Saved: {os.path.abspath(out_path)} ({os.path.getsize(out_path)} bytes)")

    print(f"Type={args.type} Name={name} Size={args.size or spec['size']}"
          f"{' -> ' + spec['resize'] if resize and not args.no_resize else ''} Candidates={args.n}")
    print(f"Review: 人工在 {REVIEW_ROOT}/ 校验（或让 agent 用 Read 回看）; "
          f"被取代的旧候选: python {sys.argv[0]} --archive {review_dir}/<file>; "
          f"通过后发布: python {sys.argv[0]} --publish {review_dir}/<file>")


if __name__ == "__main__":
    main()
