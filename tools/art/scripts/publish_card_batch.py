"""Publish checked small card illustrations under user's standing batch authorization."""
import hashlib,json,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
batch=sys.argv[1]
assert batch in {'d02','d03','d04','d05','d06','d07','d08','d09','d10'}
folder=ROOT/f'ImageReview/batches/card-illustrations-{batch}'
publication_date='2026-10-13' if batch=='d10' else '2026-10-11'
manifest=json.loads((folder/'assets.json').read_text(encoding='utf-8'))
records=[]
for asset in manifest['assets']:
    src=ROOT/'ImageReview'/asset['png'];dst=ROOT/'Assets/UI'/asset['png']
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    assert digest==asset['sha256']
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()!=digest:raise RuntimeError(f'Destination differs: {dst}')
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
    records.append(dict(id=asset['id'],source=src.relative_to(ROOT).as_posix(),target=dst.relative_to(ROOT).as_posix(),sha256=digest))
(folder/f'publication-{publication_date}.json').write_text(json.dumps(dict(date=publication_date,authorizationQuote='继续吧，这种icon可以批量生成无需向我确认',approvalMode='standing-user-authorization-after-agent-review',scope='小型卡牌插画；不扩展到卡框、角色立绘或界面',files=records),ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{batch}: {len(records)} illustrations published; hashes verified')
