"""Publish the 14 A03 assets approved 2026-10-07 and correct inherited metadata."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'ImageReview/batches/panel-refinement-a03/assets.json'
data=json.loads(p.read_text(encoding='utf-8-sig'));assert len(data['assets'])==14
records=[]
for a in data['assets']:
    w,h=a['width'],a['height']
    if a['id'].startswith('panel_'):
        a['padding']=36;a['textSafe']=dict(x=36,y=36,width=w-72,height=h-72)
    elif a['category']=='panels' and h>90:
        a['textSafe']=dict(x=36,y=32,width=w-64,height=h-66)
        a['note']='A03 binding and corner ornaments: use updated text-safe area; reflow long text. Scale uniformly; do not stretch.'
    elif a['category']=='panels':
        a['slice']=[24,16,32,16];a['textSafe']=dict(x=24,y=16,width=w-56,height=h-32)
    elif a['id'].startswith('hud_action_'):
        a['slice']=[14,11,14,11]
    if 'slice' in a:
        a['sliceOrder']='left,bottom,right,top';l,b,r,t=a['slice'];assert l+r<w and b+t<h
    a['engineValidation']='required; native geometry checked, target-engine stretch and long-text layout not yet verified'
    files={}
    for fmt in ['png','svg']:
        src=ROOT/'ImageReview'/a[fmt];dst=ROOT/'Assets/UI'/a[fmt];digest=hashlib.sha256(src.read_bytes()).hexdigest()
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Different existing target: {dst}')
        files[fmt]=dict(source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),sha256=digest)
    im=Image.open(ROOT/files['png']['source']);im.load();assert im.size==(w,h) and 'A' in im.getbands()
    records.append(dict(id=a['id'],replaces=a['replaces'],width=w,height=h,files=files))
    a.update(status='approved',publishedPng='Assets/UI/'+a['png'],publishedSvg='Assets/UI/'+a['svg'],approvedOn='2026-10-07',approvalScope='A03 panels, HUD and bars artwork')
for r in records:
    for f in r['files'].values():
        dst=ROOT/f['published'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f['source'],dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==f['sha256']
data['status']='approved';p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
replacements={a['replaces']:a['id'] for a in data['assets']}
for batch in ['foundation-a01','core-a02']:
    f=ROOT/f'ImageReview/batches/{batch}/assets.json';old=json.loads(f.read_text(encoding='utf-8-sig'))
    for a in old['assets']:
        if a['id'] in replacements:a.update(status='superseded',replacedBy=replacements[a['id']])
    old['status']='review-complete-with-a03-replacements'
    f.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以了',reviewImage='ImageReview/batches/panel-refinement-a03/comparison.png',scope='14 A03 replacements; artwork approval, engine integration remains unverified',assets=records)
(p.parent/'publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 14 A03 assets / 28 files; text-safe and slice metadata updated.')
