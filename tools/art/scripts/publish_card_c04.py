"""Publish the explicitly approved C04 attack frame and its derived window mask."""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BATCH = ROOT / 'ImageReview/batches/card-production-c04'
pairs = [
    ('ImageReview/cardframes/border_card_attack_ornate_c04.png', 'Assets/UI/cardframes/border_card_attack_ornate_c04.png'),
    ('ImageReview/batches/card-production-c04/illustration-window-mask.png', 'Assets/UI/cardframes/border_card_attack_ornate_c04_window_mask.png'),
]
records = []
for source, target in pairs:
    src, dst = ROOT / source, ROOT / target
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest() != digest:
        raise RuntimeError(f'Existing destination differs: {target}')
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    assert hashlib.sha256(dst.read_bytes()).hexdigest() == digest
    records.append(dict(source=source, target=target, sha256=digest))
(BATCH / 'publication-2026-10-11.json').write_text(json.dumps(dict(
    date='2026-10-11', approvalQuote='可以了',
    scope='C04 attack frame and derived illustration mask only; C03 back remains pending.',
    files=records), ensure_ascii=False, indent=2), encoding='utf-8')
print('Published approved C04 frame and derived mask; both hashes verified.')
