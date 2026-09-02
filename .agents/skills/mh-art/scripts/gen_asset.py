#!/usr/bin/env python3
"""《记忆勇者》设计文档仓库资产生成包装器（mh-art）。

复用用户级 germmc-image2 技能脚本的 API 通道（key 解析/HTTP/重试），叠加项目预设：
按 --type 套用规格表的尺寸、风格片段、透明底、缩放、命名。

三目录工作流（详见 SKILL.md 与 ImageReview/README.md）:
    生成  -> 默认落 ImageReview/<类型>/ 预览区，供人工校验（进 git，便于远端查看拍板）
    归档  -> --archive 把被取代的候选移入 ImageReview/_archived/<日期>/<类型>/（只进不出）
    发布  -> --publish 把用户拍板确认的文件移动到项目根 Assets/UI/<类型>/（按类型分子
             目录，与 ImageReview 类型目录同名；进 git，供文档嵌入）。校验/vision 通过
             ≠ 发布许可——必须等用户明确确认后才能执行 --publish。

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
ASSETS_ROOT = os.path.join("Assets", "UI")

# ---- 项目规格表（与 SKILL.md 保持同步）----
# 风格 v3.2（2026-08-25，用户直接反馈修正）：v3.1 三版哥布林被用户点评
# "不够简约，角色需要描边"——推翻此前视觉模型"参考无描边"的读图结论（模型读图
# 只作参考，用户的眼是标准）。v3.2 两处修正：①角色/图标/卡面主体要有干净、
# 粗细一致的深色细描边；②整体更简约——细节再砍、每形状少量平色。
# 保留：软渐变阴影、清新中饱和高明度、2-2.5 头身豆形身体、点眼单小方牙 DNA。
STYLE_BASE = ("clean simple 2D cartoon game art for casual mobile games, big rounded shapes, cute "
              "stylized proportions, very minimal design with only a few details, fresh airy "
              "palette: pastel mint-teal, cream and light warm brown with muted gold accents, "
              "medium saturation and light values, soft simple shading, memory-palace scholar "
              "fantasy theme, friendly casual mood, "
              "no watercolor, no painterly texture, no realistic rendering, no dark heavy "
              "colors, no complex details, no busy props")

# 发布目录（实际应用区）：按类型分子目录 Assets/UI/<review>/（与 ImageReview/<类型>/
# 同名，单一映射不重复维护）；prefix 字段同时用于发布时的命名规范校验。
SPECS = {
    "card": dict(size="1024x1536", transparent=False, resize=None,
                 review="cards", prefix="card_",
                 style="vertical card illustration presented like a game-asset showcase: one cute "
                       "clear focal subject standing centered on a simple soft ground, plain "
                       "pastel mint-cream backdrop with a soft elliptical shadow under the subject, "
                       "subject drawn with a clean thin dark outline and very few details, minimal "
                       "simple props, lots of clean empty space, no text, no watermark"),
    "cardback": dict(size="1024x1536", transparent=False, resize=None,
                     review="cardbacks", prefix="card_",
                     style="vertical card back design filling the whole canvas, perfectly "
                           "symmetrical: muted medium-depth teal field like a calm scholar "
                           "study at dusk, centered cute golden emblem of one glowing memory "
                           "orb floating above a small open cream book, enclosed in a thin "
                           "gold circular ring, elegant thin gold line border with tiny gold "
                           "dots at the four corners, a few tiny gold stars, soft warm glow, "
                           "very minimal, no text, no watermark"),
    "icon": dict(size="1024x1024", transparent=True, resize="256x256",
                 review="icons", prefix="icon_",
                 style="simple casual game icon, single object only, centered, bold rounded "
                       "silhouette instantly readable at small size, clean thin dark outline, "
                       "few flat colors with soft simple shading, plain transparent background, "
                       "no text, no watermark"),
    "relic": dict(size="1024x1024", transparent=True, resize="256x256",
                  review="relics", prefix="relic_",
                  style="simple casual game icon of a single small magical artifact, centered, "
                        "cute stylized prop with bold rounded silhouette, clean thin dark outline, "
                        "few flat colors with soft simple shading, plain transparent background, "
                        "no text, no watermark"),
    "potion": dict(size="1024x1024", transparent=True, resize="256x256",
                   review="potions", prefix="potion_",
                   style="simple casual game icon of a single cute alchemy potion bottle, centered, "
                         "bold rounded silhouette, clean thin dark outline, few flat colors with "
                         "soft simple shading, plain transparent background, no text, no watermark"),
    "node": dict(size="1024x1024", transparent=True, resize="256x256",
                 review="map-nodes", prefix="node_",
                    style="simple casual map node emblem, single centered object, bold rounded "
                          "shape, clean thin dark outline, few flat colors, plain transparent "
                          "background, no text, no watermark"),
    "enemy": dict(size="1024x1024", transparent=True, resize=None,
                  review="enemies", prefix="enemy_",
                  style="single cute simple cartoon fantasy monster, full body, centered, facing "
                        "viewer, 2 to 2.5 head-heights tall, bean-shaped rounded body, stubby "
                        "limbs, very simple dot eyes, extremely minimal design with only a few "
                        "flat colors, clean thin dark outline around the whole character with "
                        "consistent line weight, soft simple shading, soft elliptical ground "
                        "shadow, plain transparent background, no text, no watermark"),
    "portrait": dict(size="1024x1536", transparent=True, resize=None,
                     review="portraits", prefix="portrait_",
                     style="full body cute simple cartoon character, centered, facing viewer, "
                           "2 to 2.5 head-heights tall, bean-shaped rounded body, stubby limbs, "
                           "very simple dot eyes, extremely minimal design with only a few flat "
                           "colors, clean thin dark outline around the whole character with "
                           "consistent line weight, soft simple shading, transparent background, "
                           "no text, no watermark"),
    "logo": dict(size="1024x1024", transparent=True, resize=None,
                 review="logos", prefix="logo_",
                 style="game logo emblem mark: one single centered crest badge, bold rounded "
                       "shapes, clean thin dark outline on the emblem with consistent line "
                       "weight, few flat colors with soft simple shading, perfectly symmetrical, "
                       "plain transparent background, no text, no letters, no watermark"),
    "background": dict(size="2048x1152", transparent=False, resize="1920x1080",
                       review="backgrounds", prefix="bg_",
                       style="wide simple cartoon scene for a casual game, very minimal, big "
                             "rounded shapes in few flat colors with soft gradients, fresh airy "
                             "palette, gentle depth, large empty areas, empty center for UI, "
                             "no outlines on scenery, no characters, no text, no watermark"),
    "texture": dict(size="1024x1024", transparent=False, resize="256x256",
                    review="textures", prefix="texture_",
                    style="seamless tileable simple cartoon texture, evenly lit, no vignette, "
                          "no shadows at edges, no text, no watermark"),
    # 按钮九宫格底图（09 §4.2 三态：btn_primary/btn_secondary/btn_danger；
    # 10 §8.3 九宫格切片。所有装饰只允许落在四角与边框环，中央留净供文字）
    "button": dict(size="1536x1024", transparent=True, resize=None,
                   review="buttons", prefix="btn_",
                   style="horizontal game UI button base plate for nine-slice stretching: one "
                         "single wide rounded-rectangle button drawn flat, centered and fully "
                         "inside the canvas on plain transparent background, wide clean empty "
                         "center completely clear and plain reserved for text, all decoration "
                         "confined to the outer frame only, clean thin dark outline, few flat "
                         "colors with soft simple shading, no text, no letters, no watermark"),
    # 事件插画（S09 事件屏插图窗：横版叙事小场景，有明确主体；区别于 bg_ 的
    # "空景大场面"，插图要有聚焦叙事主体；贴入 UI 时由程序裁切加框）
    "illustration": dict(size="1536x1024", transparent=False, resize=None,
                         review="illustrations", prefix="ill_",
                         style="wide narrative still-scene illustration for a story event "
                               "card in a casual game: one clear cute focal object in the "
                               "center telling a small quiet story, a few minimal props "
                               "around it, soft pastel backdrop with gentle warm glow "
                               "accents, clean thin dark outline on the focal object, few "
                               "flat colors with soft simple shading, simple airy "
                               "composition, no characters, no text, no letters, "
                               "no watermark"),
    # 装饰面板底图（整版等比缩放用：地图页等大面积 UI 面板；装饰只落边缘与四角，
    # 中央大片留净供内容。注意：磨损毛边版不适九宫格——边带单轴拉伸会扭变形毛边，
    # 异形面板需九宫格时另出规则圆角边版本；按钮类小底图见上方 button 类型）
    "panel": dict(size="1024x1024", transparent=True, resize=None,
                  review="panels", prefix="panel_",
                  style="ornate game UI panel base plate for nine-slice stretching: one "
                        "single square panel sheet drawn flat, centered and fully inside "
                        "the canvas on plain transparent background, all decoration "
                        "strictly confined to the outer border band and the four corners, "
                        "large clean quiet center completely clear for content, clean thin "
                        "dark outline, few flat colors with soft simple shading, no text, "
                        "no letters, no watermark"),
}

# 程序合成资产类型：不走 AI 生成（size/style 为占位），条目仅让 --publish/--archive
# 能按 review 目录名推断类型、把文件落进 Assets/UI/<类型>/。
NON_AI_TYPES = {
    "cardframe": dict(review="cardframes", prefix="border_"),   # frame_b_pipeline.py 产物
    "mockup": dict(review="mockups", prefix="mockup_"),         # ui_mockup.py 产物
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
    review_to_type = {v["review"]: k for k, v in {**SPECS, **NON_AI_TYPES}.items()}
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
    spec = {**SPECS, **NON_AI_TYPES}[spec_key]
    files = collect_pngs(src)
    dst_dir = os.path.join(ASSETS_ROOT, spec["review"])
    os.makedirs(dst_dir, exist_ok=True)
    for f in files:
        name = canonical_name(os.path.splitext(os.path.basename(f))[0])
        if not name.startswith(spec["prefix"]):
            print(f"WARN [{name}.png]: name does not start with '{spec['prefix']}' "
                  f"(naming rule: docs/design/10-UI美术资源规格.md §9)", file=sys.stderr)
        dst = os.path.join(dst_dir, f"{name}.png")
        shutil.move(f, dst)
        print(f"Published: {f} -> {dst}")
    print(f"Next: 在对应设计文档里嵌入相对引用，如 ![名称](../../Assets/UI/{spec['review']}/<文件>.png)；"
          "发布目录进 git，记得提交。")


def main():
    parser = argparse.ArgumentParser(description="Memory Hero (记忆勇者) doc asset image generator")
    parser.add_argument("--type", choices=sorted({**SPECS, **NON_AI_TYPES}),
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
                        help="publish mode: move USER-CONFIRMED ImageReview file (or whole folder) "
                             "to Assets/UI/<type dir>/ (vision pass alone is NOT publish consent)")
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
    if args.type in NON_AI_TYPES:
        sys.exit(f"Error: '{args.type}' 是程序合成资产类型（frame_b_pipeline.py / ui_mockup.py 产出），"
                 "不走 AI 生成；本条目仅供 --publish/--archive 定位目录")
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
          f"用户拍板确认后发布: python {sys.argv[0]} --publish {review_dir}/<file>")


if __name__ == "__main__":
    main()
