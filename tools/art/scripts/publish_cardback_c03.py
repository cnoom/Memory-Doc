"""Publish universal card back explicitly approved by the user."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
source = 'ImageReview/cardbacks/cardback_universal_ornate_c03.png'
target = 'Assets/UI/cardbacks/cardback_universal_ornate_c03.png'
src, dst = ROOT / source, ROOT / target
digest = hashlib.sha256(src.read_bytes()).hexdigest()
batch = ROOT / 'ImageReview/batches/card-production-c03'
manifest = json.loads((batch / 'assets.json').read_text(encoding='utf-8-sig'))
asset = next(a for a in manifest['assets'] if a['id'] == 'cardback_universal_ornate_c03')
assert digest == asset['sha256'], 'Preview differs from reviewed manifest'
if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
    raise RuntimeError('Existing destination differs')
dst.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(src, dst)
assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
(batch / 'cardback-publication-2026-10-11.json').write_text(json.dumps(dict(
    date='2026-10-11', approvalQuote='卡背也没问题',
    scope='Universal C03 card back only',
    files=[dict(source=source, target=target, sha256=digest)]
), ensure_ascii=False, indent=2), encoding='utf-8')
print('Published C03 universal card back; manifest and destination hashes verified.')
