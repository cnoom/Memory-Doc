"""Publish the 15 B01 icons explicitly approved on 2026-10-07."""
import hashlib,json,shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
ids={f'icon_{group}_{name}_etching_b01' for group,names in {
    'type':['attack','skill','ability','curse'],
    'status':['burn','freeze','poison','armor','vulnerable','weak'],
    'intent':['attack','charge','defend','special','berserk']}.items() for name in names}
manifest=ROOT/'ImageReview/batches/etching-b01/assets.json'
data=json.loads(manifest.read_text(encoding='utf-8-sig'))
selected=[a for a in data['assets'] if a['id'] in ids]
assert len(selected)==15 and {a['id'] for a in selected}==ids
records=[]
# Preflight all files before copying.
for a in selected:
    files={}
    for fmt in ['png','svg']:
        src=ROOT/'ImageReview'/a[fmt]; dst=ROOT/'Assets/UI'/a[fmt]
        digest=hashlib.sha256(src.read_bytes()).hexdigest()
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:
            raise RuntimeError(f'Refusing to replace different existing file: {dst}')
        files[fmt]=dict(source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),sha256=digest)
    im=Image.open(ROOT/files['png']['source']);im.load()
    assert 'A' in im.getbands() and im.getchannel('A').getextrema()[0]==0
    records.append(dict(id=a['id'],name=a['name'],width=im.width,height=im.height,alphaRange=list(im.getchannel('A').getextrema()),files=files))
for r in records:
    for f in r['files'].values():
        dst=ROOT/f['published'];dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(ROOT/f['source'],dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==f['sha256']
for a in selected:
    a.update(status='approved',publishedPng='Assets/UI/'+a['png'],publishedSvg='Assets/UI/'+a['svg'],approvedOn='2026-10-07',approvalScope='B01 type, status and intent icon artwork')
data['status']='partially-approved'
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以',reviewImage='ImageReview/batches/etching-b01/review_icons_2026-10-07.png',scope='15 displayed B01 icons, PNG and SVG formats; no other batch assets.',assets=records)
(ROOT/'ImageReview/batches/etching-b01/icon-publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 15 approved icons / 30 PNG+SVG files.')
