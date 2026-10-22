"""Publish the 19 controls explicitly approved on 2026-10-07."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
sets={
 'foundation-a01':{f'btn_{kind}_{state}_a01' for kind in ['menu','danger'] for state in ['normal','hover','pressed','disabled']} | {f'{s}_a01' for s in ['toggle_off','toggle_on','check_off','check_on','slider_track','slider_fill','slider_thumb']},
 'core-a02':{f'focus_{s}_a02' for s in ['button','toggle','check','slider']}}
records=[];manifests=[]
for batch,ids in sets.items():
    p=ROOT/f'ImageReview/batches/{batch}/assets.json';data=json.loads(p.read_text(encoding='utf-8-sig'))
    selected=[a for a in data['assets'] if a['id'] in ids];assert {a['id'] for a in selected}==ids
    for a in selected:
        files={}
        for fmt in ['png','svg']:
            src=ROOT/'ImageReview'/a[fmt];dst=ROOT/'Assets/UI'/a[fmt];digest=hashlib.sha256(src.read_bytes()).hexdigest()
            if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Different existing target: {dst}')
            files[fmt]=dict(source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),sha256=digest)
        im=Image.open(ROOT/files['png']['source']);im.load();assert im.size==(a['width'],a['height'])
        records.append(dict(id=a['id'],batch=batch,files=files,width=im.width,height=im.height))
        a.update(status='approved',publishedPng='Assets/UI/'+a['png'],publishedSvg='Assets/UI/'+a['svg'],approvedOn='2026-10-07',approvalScope='Button states, settings controls and focus overlays artwork; no engine interaction implementation')
    data['status']='partially-approved';manifests.append((p,data))
assert len(records)==19
for r in records:
    for f in r['files'].values():
        dst=ROOT/f['published'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f['source'],dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==f['sha256']
for p,data in manifests:p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以',reviewImage='ImageReview/batches/core-a02/review_controls_2026-10-07.png',scope='8 button states, 7 control parts, 4 focus overlays; no panels or HUD',assets=records)
(ROOT/'ImageReview/batches/core-a02/control-publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 19 control assets / 38 PNG+SVG files.')
