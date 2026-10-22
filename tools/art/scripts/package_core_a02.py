"""Rebuild the core delivery from its explicit file list and verify every byte."""
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIR = ROOT / 'ImageReview/batches/core-a02'
manifest_path = DIR / 'package-manifest.json'
old = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
paths = {entry['path'] for entry in old['files']}
paths.update([
    'ImageReview/batches/core-a02/resolution-update.json',
    'ImageReview/backgrounds/bg_battle_empty_a01_r2_source.png',
    'tools/art/scripts/package_core_a02.py',
])
files = []
for rel in sorted(paths):
    p = ROOT / rel
    assert p.is_file(), rel
    files.append(dict(path=rel, sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
manifest = dict(status='pending-review', revision='1080p-r2',
                targetResolution=[1920, 1080], pathBase='repository-root', files=files)
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
target = DIR / 'core-art-a02.zip'
temp = DIR / 'core-art-a02.build.zip'
with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as z:
    for item in files:
        z.write(ROOT / item['path'], item['path'])
    z.write(manifest_path, manifest_path.relative_to(ROOT).as_posix())
with zipfile.ZipFile(temp) as z:
    assert z.testzip() is None
    for item in files:
        assert hashlib.sha256(z.read(item['path'])).hexdigest() == item['sha256'], item['path']
temp.replace(target)
print(f'Updated {target.name}: {len(files)+1} files, {target.stat().st_size} bytes; all hashes verified')
