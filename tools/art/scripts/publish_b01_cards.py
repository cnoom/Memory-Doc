"""Publish the three B01 card illustrations explicitly approved on 2026-10-07."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
ids={'card_attack_daji_etching_b01','card_skill_gedang_etching_b01','card_attack_biji_etching_b01'}
p=ROOT/'ImageReview/batches/etching-b01/assets.json'
data=json.loads(p.read_text(encoding='utf-8-sig'));selected=[a for a in data['assets'] if a['id'] in ids]
assert {a['id'] for a in selected}==ids
records=[]
for a in selected:
    src=ROOT/'ImageReview'/a['png'];dst=ROOT/'Assets/UI'/a['png'];digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Different existing target: {dst}')
    im=Image.open(src);im.load()
    records.append(dict(id=a['id'],name=a['name'],source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),sha256=digest,width=im.width,height=im.height))
for r in records:
    dst=ROOT/r['published'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/r['source'],dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==r['sha256']
for a in selected:a.update(status='approved',publishedPng='Assets/UI/'+a['png'],approvedOn='2026-10-07',approvalScope='Standalone opaque card illustration; not frame, back or effects')
for a in data['assets']:
    if a['id'].startswith(('border_card_','cardback_')):a.update(status='needs-revision',revisionDirection='C02 approved ornate card direction')
data['status']='22-approved-5-require-c02-revision';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以',reviewImage='ImageReview/batches/etching-b01/review_card_art_2026-10-07.png',scope='Three unchanged standalone illustrations only; frames/back remain unfinished',assets=records)
(p.parent/'card-publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 3 approved card illustrations.')
