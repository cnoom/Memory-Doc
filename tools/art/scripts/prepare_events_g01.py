"""Copy event sources unchanged and build review-only contact sheets."""
import json, hashlib, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
ROOT=Path(__file__).resolve().parents[3]
folder=ROOT/'ImageReview/batches/events-g01'
source=Path('C:/Users/Administrator/.codex/generated_images/01a11676-0a6c-7dd3-b7c7-20ab00b8e9c9')
prompts=json.loads((folder/'final-prompts.json').read_text(encoding='utf-8'))
ids=json.loads((folder/'source-ids.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
full=Image.new('RGB',(1240,2330),'#e7e0d0')
crop=Image.new('RGB',(1240,1570),'#e7e0d0')
assets=[]
for i,p in enumerate(prompts):
    aid='ill_event_'+p['slug']+'_etching_g01'
    dest=ROOT/'ImageReview/illustrations'/f'{aid}.png'
    dest.parent.mkdir(exist_ok=True)
    src=source/f'exec-{ids[p["slug"]]}.png'
    if dest.exists(): assert dest.read_bytes()==src.read_bytes(),dest
    shutil.copy2(src,dest)
    im=Image.open(dest)
    assert im.size==(1536,1024),im.size
    assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
    for sheet,h,size in [(full,460,(600,400)),(crop,310,(600,260))]:
        x=10+(i%2)*620;y=10+(i//2)*h
        preview=ImageOps.fit(im.convert('RGB'),size,Image.Resampling.LANCZOS)
        sheet.paste(preview,(x,y))
        ImageDraw.Draw(sheet).text((x+8,y+size[1]+10),p['eventId']+' '+p['name'],font=font,fill='#252c2d')
    assets.append(dict(id=aid,eventId=p['eventId'],name=p['name'],category='illustrations',png='illustrations/'+dest.name,width=im.width,height=im.height,status='pending-review',productionEligible=False,sourceFile=src.name,sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),display=[600,260],scaling='cover; centered crop; keep text outside artwork'))
full.save(folder/'review.png');crop.save(folder/'review-window.png')
(folder/'assets.json').write_text(json.dumps(dict(batch='events-g01',assets=assets),ensure_ascii=False,indent=2),encoding='utf-8')
print('10 original 1536x1024 opaque PNGs checked; full and 600x260 crop previews saved.')
