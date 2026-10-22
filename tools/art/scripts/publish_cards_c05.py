"""Publish C05 frames and derived masks after explicit approval."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'ImageReview/batches/card-production-c05'
manifest = json.loads((BATCH / 'assets.json').read_text(encoding='utf-8'))
records = []
for asset in manifest['assets']:
    pairs = [(ROOT / 'ImageReview' / asset['png'], ROOT / 'Assets/UI' / asset['png']),
             (ROOT / asset['windowMask'], ROOT / 'Assets/UI/cardframes' / (asset['id'] + '_window_mask.png'))]
    assert hashlib.sha256(pairs[0][0].read_bytes()).hexdigest() == asset['sha256']
    for src, dst in pairs:
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
            raise RuntimeError(f'Destination differs: {dst}')
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
        records.append(dict(source=src.relative_to(ROOT).as_posix(), target=dst.relative_to(ROOT).as_posix(), sha256=digest))
(BATCH / 'publication-2026-10-11.json').write_text(json.dumps(dict(
    date='2026-10-11', approvalQuote='可以', scope='C05 skill, ability and curse frames plus derived masks', files=records
), ensure_ascii=False, indent=2), encoding='utf-8')
print('Published 3 C05 frames and 3 masks; all hashes verified.')
