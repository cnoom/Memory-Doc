"""Publish only the four static actors explicitly approved on 2026-10-07."""
import hashlib, json, shutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
ids={'portrait_scholar_etching_b01','enemy_chaos_slime_etching_b01','enemy_training_dummy_etching_b01','enemy_goblin_etching_b01'}
manifest=ROOT/'ImageReview/batches/etching-b01/assets.json'
data=json.loads(manifest.read_text(encoding='utf-8-sig'))
records=[]
for a in data['assets']:
    if a['id'] not in ids: continue
    src=ROOT/'ImageReview'/a['png']; dst=ROOT/'Assets/UI'/a['png']
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:
        raise RuntimeError(f'Refusing to replace different existing file: {dst}')
    im=Image.open(src); im.load()
    assert 'A' in im.getbands()
    alpha=im.getchannel('A').getextrema()
    assert alpha[0]==0 and alpha[1]>=250 # Preserve original alpha; dummy peaks at 254.
    dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
    a.update(status='approved',publishedPng=dst.relative_to(ROOT).as_posix(),approvedOn='2026-10-07',approvalScope='static illustration only')
    records.append(dict(id=a['id'],name=a['name'],source=src.relative_to(ROOT).as_posix(),published=dst.relative_to(ROOT).as_posix(),width=im.width,height=im.height,sha256=digest,alphaRange=list(alpha)))
assert len(records)==4
data['status']='partially-approved'
manifest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
record=dict(date='2026-10-07',userReply='可以',reviewImage='ImageReview/batches/etching-b01/review_characters.png',scope='Four displayed static illustrations only; no animations or other B01 assets.',assets=records)
(ROOT/'ImageReview/batches/etching-b01/actor-publication-2026-10-07.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Published and hash-verified 4 approved static actor PNGs.')
