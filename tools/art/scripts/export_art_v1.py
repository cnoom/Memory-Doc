"""Export approved assets and their dependencies without changing canonical paths."""
import copy, hashlib, json, re, shutil
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '美术资源v1'
registry = json.loads((ROOT/'docs/design/art-inventory/developer-asset-registry.json').read_text(encoding='utf-8'))
items = [copy.deepcopy(a) for a in registry['items'] if a.get('productionEligible') and a['status']=='approved']
files = {}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def transfer(source):
    src = (ROOT/source).resolve()
    assert src.is_relative_to(ROOT/'Assets/UI'), source
    rel = src.relative_to(ROOT/'Assets/UI')
    dst = OUT/rel
    assert src.is_file(), source
    if source in files: return rel.as_posix()
    if dst.exists() and digest(dst)!=digest(src): raise RuntimeError(f'Existing export differs: {dst}')
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    assert digest(src)==digest(dst)
    files[source] = dict(source=source,path=rel.as_posix(),sha256=digest(dst),bytes=dst.stat().st_size)
    if src.suffix=='.svg':
        for link in re.findall(r'(?:href=["\x27]|url\(["\x27]?)([^"\x27)]+)',src.read_text(encoding='utf-8')):
            if link.startswith(('data:','#')): continue
            dependency=(src.parent/link).resolve()
            transfer(dependency.relative_to(ROOT).as_posix())
    return rel.as_posix()
def rewrite(value):
    if isinstance(value,dict): return {k:rewrite(v) for k,v in value.items()}
    if isinstance(value,list): return [rewrite(v) for v in value]
    if isinstance(value,str) and value.startswith('Assets/UI/') and (ROOT/value).is_file(): return transfer(value)
    return value
for item in items:
    assert digest(ROOT/item['paths']['png'])==item['sha256'],item['id']
items = rewrite(items)
transfer('Assets/UI/integration-v1/README.md')
transfer('Assets/UI/integration-v1/battle-replacement.md')
transfer('Assets/UI/integration-v1/battle-replacement.json')
transfer('Assets/UI/integration-v1/ui-finalization.md')
transfer('Assets/UI/integration-v1/ui-finalization.json')
for file in registry.get('supplementalFiles',[]):
    if file['status']=='approved':
        assert digest(ROOT/file['path'])==file['sha256']
        transfer(file['path'])
ledger=json.loads((ROOT/'docs/design/art-inventory/content-ledger.json').read_text(encoding='utf-8'))
cards=[r for r in ledger['items'] if r['category']=='卡牌插画']
assert len(cards)==61 and all(r['status']=='已收录' for r in cards)
assert all(r['existing'] in files for r in cards)
OUT.mkdir(exist_ok=True)
(OUT/'资源索引.json').write_text(json.dumps(dict(schemaVersion=1,asOf='2026-10-21',pathBase='美术资源v1',items=items),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'文件校验清单.json').write_text(json.dumps(dict(date='2026-10-21',assetCount=len(items),fileCount=len(files),files=list(files.values())),ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 卡牌插画目录','','| 卡名 | 文件 |','|---|---|']
for row in cards:
    rel=files[row['existing']]['path']
    lines.append(f'| {row["name"]} | [{Path(rel).name}]({rel}) |')
(OUT/'卡牌目录.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
counts={}
for f in files.values():
    category=f['path'].split('/')[0]
    counts[category]=counts.get(category,0)+1
readme=f'''# 美术资源 v1

整理日期：2026-10-21。包含当前正式收录的 {len(items)} 项独立资源，共 {len(files)} 个资源文件（包含PNG、SVG及辅助遮罩）。原始正式目录 Assets/UI 保留，此目录为可独立拷贝的分类交付副本。

包含61种卡牌插画、10种卡框、统一卡背，以及已确认的角色／敌人、图标、背景与UI组件。未收录待审候选、已替代版本和卡牌装框预览。

先查看 [资源索引](资源索引.json) 获取尺寸、类型、窗口、文字安全区和配套遮罩。索引中的文件路径相对此目录。逐文件来源与SHA256见 [校验清单](文件校验清单.json)，中文卡名检索见 [卡牌目录](卡牌目录.md)。

接入前必读 [客户端接入与视觉一致性验收](integration-v1/README.md)，逐页保存同状态截图与叠加对照。

先读 [17类UI视觉定稿清单](integration-v1/ui-finalization.md)。设计参考目录中的正式稿可按稿接入，不因productionEligible=false视为待审。

## 使用约定

- 卡牌插画为不透明骨白底，按对应卡框窗口等比容纳并应用该框自己的遮罩；不要混用遮罩。
- 卡名、效果与数值需单独渲染。所有隐藏卡使用统一卡背。
- backgrounds 包含一张旧的含角色组合背景（索引角色 composite-background-with-actors），仅供参考；分层场景使用 empty-battle-background，避免重复叠加人物。
- PNG与SVG可能是同一资源的两种格式，不是两个独立资源；导入时选择适合引擎的格式。
- 此包完成资源整理，不代表引擎接入、动画或运行时控件已实现。
- 详细接入说明位于原项目 docs/design/13-开发AI美术资源使用说明.md；原索引和设计文档路径保持不变。

## 分类文件数

| 目录 | 文件数 |
|---|---:|
'''
for category,count in sorted(counts.items()): readme+=f'| {category} | {count} |\n'
(OUT/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps(dict(assets=len(items),files=len(files),cards=len(cards),categories=counts),ensure_ascii=False))
reference_files=[]
for ref in registry.get('references',[]):
    if not ref.get('exportReference'): continue
    source_paths=[p.relative_to(ROOT).as_posix() for p in (ROOT/ref['bundleDirectory']).rglob('*') if p.is_file()] if ref.get('bundleDirectory') else [ref['path'],ref['clientSpec']]+ref.get('additionalPaths',[])
    for source_path in source_paths:
        source=ROOT/source_path
        rel=source.relative_to(ROOT/ref['bundleDirectory']) if ref.get('bundleDirectory') else source.name
        dest=OUT/'设计参考'/ref['id']/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists(): assert digest(dest)==digest(source),dest
        shutil.copy2(source,dest)
        assert digest(source)==digest(dest)
        reference_files.append(dict(path=dest.relative_to(OUT).as_posix(),sha256=digest(dest),productionEligible=False,visualStatus=ref.get('visualStatus','final'),runtimeTexture=False))
(OUT/'设计参考索引.json').write_text(json.dumps(dict(scope='FINAL visual specifications. productionEligible=false means not standalone runtime textures, NOT unapproved designs.',asOf=registry['asOf'],finalizationGuide='integration-v1/ui-finalization.md',references=[r for r in registry['references'] if r.get('exportReference')],files=reference_files),ensure_ascii=False,indent=2),encoding='utf-8')

