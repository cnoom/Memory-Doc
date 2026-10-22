"""Publish three D01 illustrations explicitly approved after the review sheet."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'ImageReview/batches/card-illustrations-d01'
assets = json.loads((BATCH / 'assets.json').read_text(encoding='utf-8'))['assets']
records = []
for asset in assets:
    src, dst = ROOT / 'ImageReview' / asset['png'], ROOT / 'Assets/UI' / asset['png']
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    assert digest == asset['sha256'], 'Preview changed since review'
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f'Destination differs: {dst}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
    records.append(dict(id=asset['id'], source=src.relative_to(ROOT).as_posix(), target=dst.relative_to(ROOT).as_posix(), sha256=digest))
(BATCH / 'publication-2026-10-11.json').write_text(json.dumps(dict(
    date='2026-10-11', approvalQuote='可以、', scope='考据、速读、全神贯注三张独立插画；不含组合预览', files=records
), ensure_ascii=False, indent=2), encoding='utf-8')
print('Published 3 D01 illustrations; source, manifest and destination hashes verified.')
