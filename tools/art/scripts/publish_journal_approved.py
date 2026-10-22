"""Publish only the journal structure and ornaments approved 2026-10-07."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
sets={
 'foundation-a01':{f'journal_{s}_a01' for s in ['cover','page_edges','page_left','page_right','spine','binding','ribbon','fold']},
 'core-a02':{f'decor_{s}_a02' for s in ['chapter_tab','loose_leaf','portrait_mount','paper_tape','stamp_frame','page_flourish','pressed_ring','margin_ticks','foreedge']}}
records=[]; manifests=[]
for batch,ids in sets.items():
    p=ROOT/f'ImageReview/batches/{batch}/assets.json';data=json.loads(p.read_text(encoding='utf-8-sig'))
    selected=[a for a in data['assets'] if a['id'] in ids]
    assert {a['id'] for a in selected}==ids
    for a in selected:
        files={}
        for fmt in ['png','svg']:
            src=ROOT/'ImageReview'/a[fmt];dst=ROOT/'Assets/UI'/a[fmt];digest=hashlib.sha256(src.read_bytes()).hexdigest()
            if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Different existing target: {dst}')
            files[fmt]=dict(source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),sha256=digest)
        im=Image.open(ROOT/files['png']['source']);im.load();assert im.size==(a['width'],a['height'])
        records.append(dict(id=a['id'],batch=batch,files=files,width=im.width,height=im.height))
        a.update(status='approved',publishedPng='Assets/UI/'+a['png'],publishedSvg='Assets/UI/'+a['svg'],approvedOn='2026-10-07',approvalScope='Journal structure and ornaments only; wording issues deferred')
    data['status']='partially-approved';manifests.append((p,data))
assert len(records)==17
for r in records:
    for f in r['files'].values():
        dst=ROOT/f['published'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f['source'],dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==f['sha256']
for p,data in manifests:p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以，就是一些细节描述上的小问题，可以先不处理',reviewImage='ImageReview/batches/core-a02/journal-1080.png',scope='8 A01 journal layers and 9 A02 ornaments; no buttons, controls or HUD',deferred='细节描述小问题暂不处理；用户未指定具体句子，保留现有文案，后续单独汇总。',assets=records)
(ROOT/'ImageReview/batches/core-a02/journal-publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 17 journal assets / 34 PNG+SVG files.')
