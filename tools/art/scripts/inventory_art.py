"""Read current design entries and disk manifests; write the art content ledger."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/design/art-inventory';OUT.mkdir(exist_ok=True)
rows=[]
def add(key,kind,name,source,status='缺失',existing='',priority='P1',note=''):
    rows.append(dict(id=key,category=kind,name=name,source=source,status=status,existing=existing,priority=priority,note=note))
known={'打击':'Assets/UI/cards/card_attack_daji_etching_b01.png','格挡':'Assets/UI/cards/card_skill_gedang_etching_b01.png','笔记':'Assets/UI/cards/card_attack_biji_etching_b01.png','读书笔记':'Assets/UI/cards/card_attack_dushubiji_illustration_v02.png'}
for file in ['06-学者角色卡牌设计.md','02-卡牌与词条系统.md','08-原型敌人设计.md']:
    text=(ROOT/'docs/design'/file).read_text(encoding='utf-8')
    for match in re.finditer(r'^  ([^\s\[\]:]+)\s{3,}\[([^\]]+)\]',text,re.M):
        name,typ=match.groups();existing=known.get(name,'')
        add(f'CARD-{sum(r["category"]=="卡牌插画" for r in rows)+1:03}','卡牌插画',name,'docs/design/'+file,'已收录' if name in known else '缺失',existing,'P0' if name in known else 'P1',typ+'；同名复用，升级通过文字/标记表达，不默认新增插画')
assert len(rows)==61 and len({r['name'] for r in rows})==61
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d08/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d09/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d10/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d07/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d06/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d05/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d04/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d03/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d02/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
for asset in json.loads((ROOT/'ImageReview/batches/card-illustrations-d01/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='卡牌插画' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
text=(ROOT/'docs/design/07-遗物设计.md').read_text(encoding='utf-8')
for i,match in enumerate(re.finditer(r'^  ([^\s\[\]:]+)\s{3,}\[(普通|罕见|稀有|Boss)\]',text,re.M),1):
    name,rarity=match.groups();add(f'RELIC-{i:02}','遗物',name,'docs/design/07-遗物设计.md',priority='P0' if name in ['记忆水晶','共鸣石','急救包','减速印记'] else 'P1',note=rarity+'；图标+详情复用同主体')
for asset in json.loads((ROOT/'ImageReview/batches/relics-e02/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='遗物' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
    if asset['name']=='思维导图': row['note']+='；07文档v1.31暂缓投放，美术完成不改变游戏投放状态'
for asset in json.loads((ROOT/'ImageReview/batches/relics-e01/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='遗物' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
enemies=[('训练假人','training_dummy'),('哥林布','goblin'),('混乱史莱姆','chaos_slime'),('蛮族战士','barbarian'),('腐化花蕾','corrupted_bud'),('幻影','phantom'),('双刃执行者','twinblade_executor'),('记忆窃贼','memory_thief'),('记忆吞噬者','memory_devourer')]
for i,(name,slug) in enumerate(enemies,1):
    approved=slug in {'training_dummy','goblin','chaos_slime'} # Explicit user approval 2026-10-07.
    p=f'{"Assets/UI" if approved else "ImageReview"}/enemies/enemy_{slug}_etching_b01.png';exists=(ROOT/p).is_file()
    if approved: assert exists,p
    add(f'ENEMY-{i:02}','敌人',name,'docs/design/08-原型敌人设计.md','已收录' if approved else '待审' if exists else '缺失',p if exists else '', 'P0' if i<=3 else 'P1','静态主体之外需待机/攻击/受击/死亡；Boss另需三阶段表现，先拆层复用')
for asset in json.loads((ROOT/'ImageReview/batches/enemies-f01/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='敌人' and r['name']==asset['name'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
text=(ROOT/'docs/design/05-Meta系统.md').read_text(encoding='utf-8')
for match in re.finditer(r'^\| (E\d+) \| ([^|]+) \|',text,re.M):
    key,name=match.groups();add(key,'事件插画',name.strip(),'docs/design/05-Meta系统.md',note='独立主体插画+通用手记事件模板；标题仍写8个但实际E01—E10')
for asset in json.loads((ROOT/'ImageReview/batches/events-g01/assets.json').read_text(encoding='utf-8'))['assets']:
    row=next(r for r in rows if r['category']=='事件插画' and r['id']==asset['eventId'])
    row.update(status='已收录',existing='Assets/UI/'+asset['png'])
add('CHAR-01','角色','学者','docs/design/06-学者角色卡牌设计.md','已收录','Assets/UI/portraits/portrait_scholar_etching_b01.png','P0','2026-10-07用户确认独立静态立绘；不等于已完成全身或动作资源')
for i,name in enumerate(['狂战士','术士'],2):add(f'CHAR-{i:02}','角色',name,'docs/design/05-Meta系统.md','范围待定',priority='P2',note='角色卡组详细设计未完成，先轮廓配色储备')
counts={kind:sum(r['category']==kind for r in rows) for kind in dict.fromkeys(r['category'] for r in rows)}
for r in rows:
    assert (ROOT/r['source']).is_file()
    if r['existing']:assert (ROOT/r['existing']).is_file()
(OUT/'content-ledger.json').write_text(json.dumps({'scope':'当前已命名内容；不含UI组件和动效工作包，不作为总贴图数量','counts':counts,'items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
md=['# 美术内容逐项台账','', '> 由 tools/art/scripts/inventory_art.py 按当前策划条目与路径生成；优先级是制作建议。ID 是本台账编号，不替代游戏内容 ID。','']
for kind in counts:
    md+=['## '+kind,'','| ID | 内容 | 当前状态 | 优先级 | 来源 / 现有文件 |','|---|---|---|---|---|']
    for r in rows:
        if r['category']!=kind:continue
        source='[策划](../../../'+r['source']+')';existing=(' · [现有文件](../../../'+r['existing']+')') if r['existing'] else ''
        md.append(f'| {r["id"]} | {r["name"]} | {r["status"]} | {r["priority"]} | {source}{existing} |')
    md+=['']
(OUT/'内容逐项台账.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps(counts,ensure_ascii=True))
