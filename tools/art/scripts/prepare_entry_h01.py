"""Preserve generated concepts and adapt review copies to the 1920x1080 project canvas."""
import json, hashlib, shutil
from pathlib import Path
from PIL import Image, ImageOps
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'ImageReview/batches/entry-h01'
SOURCE=Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
items=[]
for slug,uid in [('main_menu','38d52175-bfd0-4ad6-bba5-eef4b55160fa'),('loading','30ba4f67-7a17-41b6-820a-e6822e945578')]:
    src=SOURCE/f'exec-{uid}.png'
    original=OUT/f'{slug}_source.png'
    shutil.copy2(src,original)
    im=Image.open(original)
    dest=OUT/f'mockup_{slug}_h01_1920x1080.png'
    ImageOps.fit(im.convert('RGB'),(1920,1080),Image.Resampling.LANCZOS).save(dest)
    assert Image.open(dest).size==(1920,1080)
    items.append(dict(id=f'mockup_{slug}_h01',path=dest.relative_to(ROOT).as_posix(),source=original.relative_to(ROOT).as_posix(),sourceResolution=list(im.size),width=1920,height=1080,method='Lanczos cover; centered negligible aspect crop',native1080p=False,status='pending-review',productionEligible=False,role='composite-ui-design-reference',sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
(OUT/'assets.json').write_text(json.dumps(dict(batch='entry-h01',assets=items),ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(items,ensure_ascii=False))
