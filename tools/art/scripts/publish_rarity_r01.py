import json,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'ImageReview/batches/card-rarity-r01'
assets=json.loads((folder/'assets.json').read_text(encoding='utf-8'))['assets'];records=[]
for a in assets:
    pairs=[(ROOT/'ImageReview'/a['png'],ROOT/'Assets/UI'/a['png']),(ROOT/a['windowMask'],ROOT/'Assets/UI/cardframes'/(a['id']+'_window_mask.png'))]
    assert hashlib.sha256(pairs[0][0].read_bytes()).hexdigest()==a['sha256']
    for src,dst in pairs:
        h=hashlib.sha256(src.read_bytes()).hexdigest()
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=h:raise RuntimeError('Destination differs')
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest()==h
        records.append(dict(source=src.relative_to(ROOT).as_posix(),target=dst.relative_to(ROOT).as_posix(),sha256=h))
(folder/'publication-2026-10-11.json').write_text(json.dumps(dict(approvalQuote='可以',scope='R01罕见与稀有攻击框及派生遮罩',files=records),ensure_ascii=False,indent=2),encoding='utf-8')
print('Published 2 R01 frames and 2 masks; hashes verified')
